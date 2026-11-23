param(
    [ValidatePattern('^[a-z0-9][a-z0-9_-]{1,62}$')]
    [string]$Project = 'adaptive-spot-lab',
    # The owner's main folder: the checkout that holds the normal app's settings. Default: the folder this file is in.
    [string]$Repository = '',
    [string]$EnvFile = '',
    [string]$BackupRoot = '',
    # Set by the run that started this one after the folder check had brought a newer copy of this file.
    [switch]$Relaunched,
    # The model test only (tools/m8/update-model.ps1): no wait near midnight and no keep-awake call. Refused
    # for any project whose name does not begin with asl-model-.
    [switch]$Model
)

# The update file (ExecPlan 0031 section 4.4): the one double-click that installs what main holds on the
# owner's PC. It never asks for input. In this order:
# 1. The folder check: with no uncommitted change to a tracked file, the folder is put on main and fast-forwarded
#    to origin/main; with any, nothing is changed and the files are named. A newer copy of this file that the
#    fast-forward brought is then run instead of this one.
# 2. A read-only preflight: Docker, the env file, postgres, api and web running and the api ready, the schema, and
#    every running service's ASL_*_ENABLED flags as the env file renders them.
# 3. A protected backup of the main database with its SHA-256, and rollback tags (<project>-<service>:before-update)
#    on the images that run now. After a run that stopped once it had set them, they are kept: they still name
#    the release before it.
# 4. The builds of every image of the app (never postgres; test services are not built).
# 5. Forward migrations of the main database to the head of the built code. The api and then the web are replaced
#    first when the new api accepts the schema that is there (expand), otherwise after the migration. The api always
#    comes before the web, whose health check reads it: on 2026-10-25 a new web that needs the new api (ExecPlan 0042's,
#    which signs nobody in) failed its health check against the old one, and the update stopped there.
#    Before a migration the new api needs first (a contract), the workers that write the database every second (the
#    execution and market workers) stop, each in its container, so that the migration waits for no session of theirs
#    (ExecPlan 0060's migration 0041 took each moved table's exclusive lock); a migration that does not apply starts
#    them again by their ids (docker start: Compose's start refuses a service whose one-shot migrate dependency has no
#    container), so that the app runs as before, and after one that applied step 6 recreates them on their built
#    images. The services a stopped run's migration stop left stopped (its record names them) count as running for
#    this run: they are recreated on their built images, the api before the web as always.
# 6. Every running service whose image or settings (Compose's config hash) changed is recreated, with --no-deps
#    and its flags unchanged; services that do not run stay stopped. A recreated execution worker with
#    ASL_EXECUTION_ENABLED=1 must hold its lease.
# 7. Verify: the folder at origin/main, each running service on its built image, the api ready, the
#    reconciliation OK and the pages answering. Then a read-out that never stops the update: Bitcoin's spot feed and
#    its daily history, the spot account, its run, the rule's newest reading, the backtest and the futures app's
#    records kept in the archive (ExecPlan 0060).
# 8. A JSON record beside the backup, and what the update changes, from the release notes of the merges.
# 9. Tidy: delete each branch that main contains through a merge (never main, never a branch that only points
#    into main's own history, never one with commits main lacks; on GitHub with a lease on the tip it checked),
#    then list local branches with unmerged work; delete the database dumps older than the newest three (never the
#    copy in before-futures/, the futures app's clean start's of ExecPlan 0039, which is the owner's to delete);
#    remove this app's images that no current service uses, by exact name (ExecPlan 0034). A step here that fails is
#    reported; the update itself is done by then.
# ExecPlan 0061 removed what only the move to the futures app and then to spot needed: the futures account's
# preflight, the clean start and its undo, the removal of the retired services and the Claude sign-in's starter.
# Before each change it waits by itself while the clock is near the day's reference and reading (23:55 to 00:10 UTC,
# ExecPlan 0061), and it keeps the PC awake while it runs (SetThreadExecutionState with ES_CONTINUOUS |
# ES_SYSTEM_REQUIRED, reset with ES_CONTINUOUS at the end: Microsoft's Win32 reference, MicrosoftDocs/sdk-api, ms.date
# 12/05/2018).
# Any failed step stops the run where it is, records FAILED and prints what it left; nothing reports success
# after a failed step. A stopped run is fixed forward: a later run continues from what is installed.
# It enables no identity, sets no flag and approves nothing.
# Windows PowerShell 5.1 compatible; ASCII only.
$ErrorActionPreference = 'Stop'
# This file as it runs, read before the folder check can replace it on disk.
$mine = [IO.File]::ReadAllText($PSCommandPath)
if (-not $Repository) { $Repository = Join-Path $PSScriptRoot '..' }
$Repository = (Resolve-Path -LiteralPath $Repository).Path
if (-not $EnvFile) { $EnvFile = Join-Path $Repository '.env' }
if (-not $BackupRoot) { $BackupRoot = Join-Path $Repository '.cache/deployments' }
$BackupRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($BackupRoot)
if ($Model -and $Project -notmatch '^asl-model-') { throw '-Model is for the model test (asl-model-...), never for an installation' }
foreach ($name in @('DOCKER_HOST', 'DOCKER_CONTEXT')) {
    if ([Environment]::GetEnvironmentVariable($name, 'Process')) { throw "$name is set in this shell: run the update from a shell without it" }
}
# Compose reads the calling shell before the env file. Nothing of the shell may decide an update.
foreach ($name in @([Environment]::GetEnvironmentVariables('Process').Keys)) {
    if ("$name" -like 'ASL_*' -or "$name" -like 'COMPOSE_*' -or "$name" -eq 'WEB_PORT') {
        [Environment]::SetEnvironmentVariable("$name", $null, 'Process')
    }
}
# git fails instead of asking for a password.
$env:GIT_TERMINAL_PROMPT = '0'
# Git for Windows installed without its PATH entry: its usual folder.
if (-not (Get-Command git -CommandType Application -ErrorAction SilentlyContinue) -and $env:ProgramFiles -and
    (Test-Path -LiteralPath (Join-Path $env:ProgramFiles 'Git\cmd\git.exe'))) {
    $env:PATH = (Join-Path $env:ProgramFiles 'Git\cmd') + ';' + $env:PATH
}

# ExecPlan 0060: the agents' and the sources' profiles have no service any more.
$profiles = @('market', 'execution')
$profileArguments = @()
foreach ($name in $profiles) { $profileArguments += @('--profile', $name) }
# The order in which running services are recreated: a running service named in neither list comes between them.
$mainOrder = @('api', 'web', 'market-worker', 'execution-worker')
$lastOrder = @()
# Every page of the four menu items of the spot app (ExecPlan 0060 section 4.9): Cockpit, Trades, Backtest and
# Settings.
$pages = @('/', '/trades', '/backtest', '/settings')
# The folder of the copy of the backup the futures app's clean start made (ExecPlan 0039 section 5.1): the tidy step
# never deletes it.
$keptFolder = 'before-futures'
$stopped = @()
# The app's workers stopped for the migration, by service.
$halted = @()
# The container each stopped service had (by service), for the undo; and the services a stopped run left stopped.
$stoppedIds = @{}
$left = @()
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$record = [ordered]@{ started_utc = [DateTime]::UtcNow.ToString('o'); project = $Project; status = 'IN_PROGRESS'; model = [bool]$Model
    steps = [ordered]@{} }
$stage = 'folder'
$backup = $null
$compose = $null
$database = $null
$replaced = @()
$current = @()
$built = [ordered]@{}
$awake = $false

function Say { param([string]$Text) Write-Output $Text }

function Invoke-Git {
    # git on the owner's folder: its output lines. Its exit code is kept in $script:GitCode and what it wrote to
    # stderr in $script:GitErrors, apart from the output (Git for Windows warns there about line ends, for
    # example); a failure is an error unless allowed.
    param([Parameter(Mandatory = $true)][string[]]$Arguments, [switch]$AllowFailure)
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $global:LASTEXITCODE = 125
    $all = @()
    try { $all = @(& git -C $Repository @Arguments 2>&1) } finally { $ErrorActionPreference = $saved }
    $script:GitCode = $LASTEXITCODE
    $lines = @($all | Where-Object { $_ -isnot [Management.Automation.ErrorRecord] } | ForEach-Object { "$_" })
    $script:GitErrors = @($all | Where-Object { $_ -is [Management.Automation.ErrorRecord] } | ForEach-Object { "$_" })
    if ($script:GitCode -ne 0 -and -not $AllowFailure) {
        throw "git $($Arguments[0]) failed: $((@($script:GitErrors) + @($lines) | Select-Object -Last 3) -join ' ')"
    }
    return $lines
}

function Invoke-Native {
    # docker with its stderr kept as text: Windows PowerShell 5.1 turns redirected native stderr into a terminating
    # error under 'Stop'. The caller checks $LASTEXITCODE.
    param([Parameter(Mandatory = $true)][string[]]$Arguments)
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $global:LASTEXITCODE = 125
    try { return @(& docker @Arguments 2>&1 | ForEach-Object { "$_" }) } finally { $ErrorActionPreference = $saved }
}

function Invoke-App {
    # docker compose on the app, with every profile whose services this file reads or builds.
    param([Parameter(Mandatory = $true)][string[]]$Arguments, [switch]$AllowFailure)
    return Invoke-PilotCompose -Compose $compose -Arguments ($profileArguments + $Arguments) -AllowFailure:$AllowFailure
}

function Invoke-Psql {
    # One statement on the main database: the last line it prints.
    param([string]$Sql)
    $lines = Invoke-PilotCompose -Compose $compose -Arguments @('exec', '-T', 'postgres', 'psql', '-X', '-U', 'asl', '-d', $database,
        '-At', '-v', 'ON_ERROR_STOP=1', '-c', $Sql)
    return "$($lines | Select-Object -Last 1)".Trim()
}

function Get-Schema {
    # The main database's schema revision, or nothing on a database the migrations have not reached yet.
    if ((Invoke-Psql "SELECT to_regclass('public.alembic_version') IS NULL") -eq 't') { return '' }
    return Invoke-Psql 'SELECT version_num FROM alembic_version'
}

function Stop-Writers {
    # Step 5, before a migration the new api needs first (ExecPlan 0060): the app's workers that write the database
    # every second stopped, each in its container, so that the migration waits for no session of theirs. Each is
    # recorded as it stops; Undo-Writers starts them again by their ids when the migration does not apply. Called as a
    # statement, so that what it says is printed.
    $script:stage = 'stop for the migration'
    $result = $record.steps.migration_stop
    foreach ($service in @('execution-worker', 'market-worker')) {
        if (-not $running.Contains($service) -or $running[$service].status -notin @('running', 'restarting')) { continue }
        $script:stoppedIds[$service] = $running[$service].container
        $script:halted += $service
        $script:stopped += $service
        $result.stopped = @($script:halted)
        Invoke-App -Arguments @('stop', $service) | Out-Null
    }
    Say "  Stopped for the migration: $(if ($script:halted.Count) { $script:halted -join ', ' } else { 'none' })"
}

function Undo-Writers {
    # The workers Stop-Writers stopped, started again by their ids after a migration that did not apply (it rolls
    # back whole), so that the app runs as before. It always throws: with what it did, or with what it could not do.
    param([string]$Failure)
    $result = $record.steps.migration_stop
    $again = @()
    $result.started_again = $again
    try {
        foreach ($service in @($script:halted)) {
            $output = Invoke-Native @('start', $script:stoppedIds[$service])
            if ($LASTEXITCODE -ne 0) { throw "docker start of the container of $service failed: $(($output | Select-Object -Last 1))" }
            $again += $service
            $result.started_again = $again
        }
        if ($again.Count) {
            Start-Sleep -Seconds 5
            $down = @($script:halted | Where-Object { $found = Get-Container $_; -not $found -or $found.status -ne 'running' })
            if ($down.Count) { throw "started again but not running: $($down -join ', ')" }
        }
    } catch {
        throw "$Failure. Starting the containers stopped for the migration again failed too ($($_.Exception.Message)); started again before that: $(if ($again.Count) { $again -join ', ' } else { 'none' })"
    }
    $script:stopped = @($script:stopped | Where-Object { $_ -notin $script:halted })
    $script:halted = @()
    throw "$Failure. The containers stopped for the migration were started again, so the app runs as before (started again: $(if ($again.Count) { $again -join ', ' } else { 'none' }))"
}

function Get-ImageId {
    # The image a name points to, or nothing when Docker says that no such image exists; any other answer is an error.
    param([string]$Name)
    $lines = Invoke-Native @('image', 'inspect', '-f', '{{.Id}}', $Name)
    $code = $LASTEXITCODE
    $ids = @($lines | ForEach-Object { "$_".Trim() } | Where-Object { $_ -match '^sha256:[0-9a-f]{64}$' })
    if ($code -eq 0 -and $ids.Count -eq 1) { return $ids[0] }
    if ($code -ne 0 -and (($lines -join ' ') -match '(?i)no such (image|object)')) { return $null }
    throw "Could not read the image ${Name}: $(($lines | Select-Object -Last 2) -join ' ')"
}

function Get-Container {
    # The one container of a service of this project (not a 'compose run' container), or nothing: its id,
    # image, state, restart count and ASL_*_ENABLED flags. A listing that fails is an error, never "none".
    param([string]$Service)
    $lines = Invoke-Native @('ps', '-a', '--no-trunc', '--filter', "label=com.docker.compose.project=$Project", '--filter',
        "label=com.docker.compose.service=$Service", '--filter', 'label=com.docker.compose.oneoff=False', '--format', '{{.ID}}')
    if ($LASTEXITCODE -ne 0) { throw "Could not list the container of ${Service}: $(($lines | Select-Object -Last 2) -join ' ')" }
    $ids = @($lines | ForEach-Object { "$_".Trim() } | Where-Object { $_ })
    if (-not $ids.Count) { return $null }
    if ($ids.Count -gt 1) { throw "Service $Service has $($ids.Count) containers; remove the extra one by its name first" }
    $fields = ((Invoke-Native @('inspect', '-f', '{{.Id}}|{{.Image}}|{{.State.Status}}|{{.RestartCount}}|{{.State.StartedAt}}', $ids[0])) -join '').Split('|')
    if ($LASTEXITCODE -ne 0 -or $fields.Count -ne 5) { throw "Could not inspect the container of $Service" }
    $labels = ((Invoke-Native @('inspect', '-f', '{{json .Config.Labels}}', $ids[0])) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $labels -notmatch '^\{') { throw "Could not read the labels of the container of $Service" }
    $hash = "$(($labels | ConvertFrom-Json).'com.docker.compose.config-hash')"
    $json = ((Invoke-Native @('inspect', '-f', '{{json .Config.Env}}', $ids[0])) -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $json -notmatch '^\[') { throw "Could not read the flags of the container of $Service" }
    $flags = [ordered]@{}
    # Through a variable: Windows PowerShell 5.1 passes a JSON array down the pipeline as one object.
    $entries = $json | ConvertFrom-Json
    foreach ($entry in $entries) {
        if ("$entry" -match '^(ASL_[A-Z]+_ENABLED)=(.*)$') { $flags[$Matches[1]] = $Matches[2] }
    }
    return [ordered]@{ container = $fields[0]; image = $fields[1]; status = $fields[2]; restarts = $fields[3]; started = $fields[4]; flags = $flags
        config_hash = $hash }
}

function Get-Running {
    # Every service of the app that has a container, by name.
    $found = [ordered]@{}
    foreach ($service in $services.Keys) {
        $container = Get-Container $service
        if ($container) { $found[$service] = $container }
    }
    return $found
}

function Test-ApiReady {
    Invoke-PilotCompose -Compose $compose -Arguments @('exec', '-T', 'api', 'python', '-c',
        "import urllib.request; assert urllib.request.urlopen('http://127.0.0.1:8000/v1/health/ready', timeout=5).status == 200") | Out-Null
}

function Test-QuietTime {
    # Not near the day's reference and reading (ExecPlan 0061): the engine takes the day's reference in the first five
    # minutes after 00:00 UTC and reads the rule from 00:05, so a change begins at or after 00:10 UTC and ends, with the
    # minutes it needs, by 23:55 UTC. The same in tools/docker-cleanup.ps1; tools/m8/update-model.ps1 tests both.
    param([DateTime]$At, [int]$Minutes)
    $minute = $At.TimeOfDay.TotalMinutes
    return ($minute -ge 10 -and $minute + $Minutes -le 1435)
}

function Wait-QuietTime {
    param([int]$Minutes = 2, [string]$What = 'the next step')
    if ($Model) { return }
    $said = $false
    while ($true) {
        $now = [DateTime]::UtcNow
        if (Test-QuietTime $now $Minutes) { return }
        if (-not $said) {
            Say "Waiting for a quiet minute before $What (the day's reference and reading run from 00:00 to 00:10 UTC; now $($now.ToString('HH:mm')) UTC)."
            $said = $true
        }
        Start-Sleep -Seconds 20
    }
}

function Set-KeepAwake {
    # SetThreadExecutionState (kernel32): ES_CONTINUOUS | ES_SYSTEM_REQUIRED keeps the PC from sleeping until
    # ES_CONTINUOUS alone is set again. A return of 0 is a failure. Best effort: a failure is reported only.
    param([bool]$On)
    if ($Model) { return $false }
    try {
        if (-not ('AslUpdate.Power' -as [type])) {
            Add-Type -Namespace AslUpdate -Name Power -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'
        }
        $flags = if ($On) { [uint32]2147483649 } else { [uint32]2147483648 }
        return ([AslUpdate.Power]::SetThreadExecutionState($flags) -ne 0)
    } catch { return $false }
}

function Wait-Running {
    # A recreated service runs and has not restarted, 20 s after it was started.
    param([string]$Service, [string]$Image)
    $container = $null
    for ($i = 0; $i -lt 10; $i++) {
        Start-Sleep -Seconds 2
        $container = Get-Container $Service
    }
    if (-not $container) { throw "Service $Service has no container after it was recreated" }
    if ($container.image -ne $Image) { throw "Service $Service runs $($container.image), not the image built for it" }
    if ($container.status -ne 'running') { throw "Service $Service is $($container.status) after it was recreated" }
    if ("$($container.restarts)" -ne '0') { throw "Service $Service restarted $($container.restarts) time(s) after it was recreated" }
    return $container
}

function Wait-ExecutionLease {
    for ($i = 0; $i -lt 61; $i++) {
        $text = Invoke-Psql 'SELECT (owner_id IS NOT NULL AND expires_at > clock_timestamp())::text FROM execution_lease WHERE id = 1'
        if ($text -eq 'true') { return $i + 1 }
        if ($text -ne 'false') { throw "Could not read the execution lease ('$text')" }
        Start-Sleep -Seconds 2
    }
    throw 'The execution worker did not take its lease within 120 s. Its log: docker compose --profile execution logs execution-worker'
}

function Update-Service {
    # Recreates one running service on its built image, unless it runs that image already with the settings
    # compose.yaml and the env file now give it (Compose's config hash, where it could be read). A service a stopped run
    # left stopped counts as running.
    param([string]$Service)
    $now = $running[$Service]
    if (-not $now -or ($now.status -notin @('running', 'restarting') -and $Service -notin $script:left)) { return }
    if (-not $built.Contains($Service) -or $Service -in $script:replaced) { return }
    $settings = $hashes.Contains($Service) -and $hashes[$Service] -ne $now.config_hash
    # A service the migration stopped, or a stopped run left stopped, is started again whatever its image.
    $wasStopped = $Service -in $script:stopped -or $Service -in $script:left
    if ($now.image -eq $built[$Service] -and -not $settings -and -not $wasStopped) { if ($Service -notin $script:current) { $script:current += $Service }; return }
    Wait-QuietTime -What "recreating $Service"
    $script:stage = "recreate $Service"
    $script:replaced += $Service
    $wait = @()
    if ($Service -in @('web', 'api')) { $wait = @('--wait') }
    Invoke-App -Arguments (@('up', '-d', '--no-deps', '--no-build', '--force-recreate') + $wait + @($Service)) | Out-Null
    $after = Wait-Running $Service $built[$Service]
    foreach ($flag in $now.flags.Keys) {
        if ("$($after.flags[$flag])" -cne "$($now.flags[$flag])") { throw "Service $Service was recreated with $flag '$($after.flags[$flag])', not '$($now.flags[$flag])'" }
    }
    $note = ''
    if ($Service -eq 'execution-worker' -and $after.flags['ASL_EXECUTION_ENABLED'] -eq '1') {
        $reads = Wait-ExecutionLease
        $note = " (it holds the execution lease; $reads read(s))"
    }
    if ($Service -eq 'api') { Test-ApiReady }
    $record.steps.recreated[$Service] = [ordered]@{ from = $now.image; to = $after.image; settings_changed = $settings }
    $what = if ($now.image -ne $after.image) { 'on its new image' } elseif ($settings) { 'with its new settings' }
    elseif ($Service -in $script:halted) { 'after the migration' } else { 'after the stopped update' }
    Say "  $Service recreated $what$note"
}

function Show-ReadOut {
    # Read-only, after the check (ExecPlan 0060 sections 4.7 and 9): Bitcoin's spot feed and its daily history, the spot
    # account and its run, the rule's newest reading, the backtest, and the futures app's records in the archive. It
    # waits up to three minutes, all told, for the feed to connect and fill its daily history, for the engine's first
    # reading and for the backtest the execution worker computes from that history. Printed, and kept in the record.
    # It never stops the update: a value it cannot read is written as not read, and a feed that does not connect is
    # reported, not a failed update: the rule and the valuation wait for fresh data on their own (rule 11).
    $feed = "SELECT jsonb_build_object('status', s.status, 'reason', s.reason, 'written', " +
        "to_char(s.heartbeat_at AT TIME ZONE 'UTC', 'HH24:MI:SS'), 'instrument', (SELECT i.status || CASE WHEN i.usable " +
        "THEN ', usable' ELSE ', not usable' END FROM spot_instruments i WHERE i.id = s.instrument_id), 'clock', " +
        "s.clock_verified, 'history', s.daily_checked_at IS NOT NULL, 'days', (SELECT count(*) FROM spot_daily_bars), " +
        "'first_day', (SELECT to_char(to_timestamp(min(open_ms) / 1000.0) AT TIME ZONE 'UTC', 'YYYY-MM-DD') " +
        "FROM spot_daily_bars), 'last_day', (SELECT to_char(to_timestamp(max(open_ms) / 1000.0) AT TIME ZONE 'UTC', " +
        "'YYYY-MM-DD') FROM spot_daily_bars), 'candles', (SELECT count(*) FROM spot_bars WHERE final)) " +
        "FROM spot_feed_state s WHERE s.id = 1"
    # The account keeps its money through the switch (ExecPlan 0060 section 4.7); an empty database's is funded by the
    # api when it starts (ExecPlan 0042), and its first run starts by itself once it is funded.
    $account = "SELECT jsonb_build_object('funded', a.initialized, 'cash', round(a.cash, 2)::text, 'btc', " +
        "(SELECT trim_scale(h.quantity)::text FROM account_holdings h WHERE h.asset = 'BTC'), 'run', " +
        "(SELECT jsonb_build_object('seq', r.seq, 'state', r.state, 'causes', r.causes) FROM spot_runs r " +
        "ORDER BY r.seq DESC LIMIT 1), 'reading', (SELECT jsonb_build_object('day', to_char(g.utc_date, 'YYYY-MM-DD'), " +
        "'result', g.result, 'action', g.action, 'outcome', g.outcome, 'target', trim_scale(g.target)::text, " +
        "'codes', g.codes) FROM spot_rule_readings g ORDER BY g.seq DESC LIMIT 1), 'fills', " +
        "(SELECT count(*) FROM spot_fills), 'backtest', (SELECT jsonb_build_object('computed', " +
        "to_char(b.computed_at AT TIME ZONE 'UTC', 'YYYY-MM-DD HH24:MI'), 'days', b.days, 'first_day', " +
        "to_char(to_timestamp(b.first_day_ms / 1000.0) AT TIME ZONE 'UTC', 'YYYY-MM-DD'), 'last_day', " +
        "to_char(to_timestamp(b.last_day_ms / 1000.0) AT TIME ZONE 'UTC', 'YYYY-MM-DD')) FROM spot_backtests b " +
        "ORDER BY b.seq DESC LIMIT 1), 'funding', (SELECT f.status FROM funding_requests f " +
        "WHERE f.idempotency_key = 'SYSTEM:INITIALIZE')) FROM account_state a WHERE a.id = 1"
    $archive = "SELECT jsonb_build_object('tables', (SELECT count(*) FROM archive.moved_objects WHERE kind = 'TABLE'), " +
        "'retired', (SELECT count(*) FROM archive.futures_run_events WHERE kind = 'FUTURES_RETIRED'))"
    $result = [ordered]@{ feed = 'not read'; account = 'not read'; archive = 'not read' }
    $record.steps.read_out = $result
    $deadline = [DateTime]::UtcNow.AddSeconds(180)
    $found = $null
    $state = $null
    try {
        while ($true) {
            $found = ConvertFrom-Json -InputObject (Invoke-Psql $feed)
            $state = ConvertFrom-Json -InputObject (Invoke-Psql $account)
            $ready = $found.status -eq 'CONNECTED' -and $found.history -and $state.reading -and $state.backtest
            if ($ready -or $Model -or [DateTime]::UtcNow -ge $deadline) { break }
            Start-Sleep -Seconds 10
        }
    } catch { Say "  Not read: $($_.Exception.Message)" }
    if ($found) {
        $result.feed = $found
        # A feed that has written nothing yet is STARTING, with no reason.
        $text = if ($found.reason) { "$($found.status) ($($found.reason))" } else { "$($found.status)" }
        $written = if ($found.written) { "newest write at $($found.written) UTC" } else { 'nothing written yet' }
        $instrument = if ($found.instrument) { "BTCUSDT $($found.instrument)" } else { 'BTCUSDT not checked yet' }
        $clock = if ($found.clock) { 'clock checked' } else { 'clock not checked yet' }
        $days = if ([int64]$found.days -gt 0) { "$($found.days) daily candles ($($found.first_day) to $($found.last_day))" } else { 'no daily candle yet' }
        $history = if ($found.history) { '' } else { ', the daily history still filling' }
        Say "  Bitcoin spot feed: $text, $written, $instrument, $clock; $days$history; $($found.candles) one-minute candles"
    } else { Say '  Bitcoin spot feed: not read' }
    if ($state) {
        $result.account = $state
        if (-not $state.funded) {
            $why = if ($state.funding) { "its starting contribution is $($state.funding)" } else { 'the api has not added its starting contribution' }
            Say "  Spot account: not funded yet ($why). The app adds the 10,000 virtual USDT by itself when the api starts; trading then starts by itself."
        } else {
            $run = if ($state.run) { "run #$($state.run.seq) $($state.run.state)" } else { 'no run yet' }
            if ($state.run -and @($state.run.causes).Count) { $run += " ($(@($state.run.causes) -join ', '))" }
            Say "  Spot account: $($state.cash) USDT and $($state.btc) BTC; $run; $($state.fills) trade(s)"
        }
        $reading = $state.reading
        $text = if (-not $reading) { 'none yet (the engine reads the rule at its first step after 00:05 UTC once the daily history is there)' }
        elseif ($reading.outcome -eq 'NOT_READABLE') { "$($reading.day) not readable yet; the engine tries again every 15 minutes" }
        else {
            # The target is the share of the account in Bitcoin, as a decimal string; written as a percentage.
            $share = ([decimal]$reading.target * 100).ToString('0.##', [Globalization.CultureInfo]::InvariantCulture)
            $line = "$($reading.day) $($reading.result) (target $share% in Bitcoin): $($reading.outcome)"
            if ($reading.action -and $reading.action -ne 'NO_CHANGE') { $line += " ($($reading.action))" }
            if (@($reading.codes).Count) { $line += ": $(@($reading.codes) -join ', ')" }
            $line
        }
        Say "  The rule's newest reading: $text"
        $test = $state.backtest
        $text = if ($test) { "computed at $($test.computed) UTC on $($test.days) days ($($test.first_day) to $($test.last_day)); its page is Backtest" }
        else { 'not computed yet (the execution worker computes it once the daily history is there)' }
        Say "  Backtest: $text"
    } else { Say '  Spot account: not read' }
    try {
        $moved = ConvertFrom-Json -InputObject (Invoke-Psql $archive)
        $result.archive = $moved
        Say "  Archive: $($moved.tables) table(s) of the futures app kept read-only; $($moved.retired) futures run(s) retired by the switch"
    } catch { Say "  Archive: not read ($($_.Exception.Message))" }
}

function Get-ReleaseNote {
    # The lines after 'Release note:' in a commit message, up to its trailers.
    param([string[]]$Lines)
    $note = @()
    $inside = $false
    foreach ($line in $Lines) {
        if (-not $inside) {
            if ($line -match '^\s*Release note:\s*$') { $inside = $true }
            continue
        }
        if ($line -match '^(Co-Authored-By|Claude-Session|Signed-off-by):' -or $line -match '^-{3,}\s*$' -or $line -match 'Generated with \[') { break }
        $note += $line.TrimEnd()
    }
    while ($note.Count -and -not $note[-1]) { $note = @($note | Select-Object -First ($note.Count - 1)) }
    return $note
}

function Get-PreviousCommit {
    # The commit the newest completed update (or M7 deployment) installed, when there is a record of it.
    $newest = $null
    if (-not (Test-Path -LiteralPath $BackupRoot)) { return $null }
    # Windows PowerShell 5.1 ignores -Include beside -LiteralPath, so the names are filtered here: otherwise every
    # file is read, the database dumps included.
    foreach ($file in @(Get-ChildItem -LiteralPath $BackupRoot -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -in @('update.json', 'm7-deploy.json') })) {
        try {
            $found = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
            $commit = "$($found.source.commit)"
            if ("$($found.status)" -ne 'COMPLETE' -or $commit -notmatch '^[0-9a-f]{40}$') { continue }
            $finished = [DateTime]::Parse("$($found.finished_utc)", [Globalization.CultureInfo]::InvariantCulture, [Globalization.DateTimeStyles]::RoundtripKind)
            if (-not $newest -or $finished -gt $newest.finished) { $newest = @{ commit = $commit; finished = $finished } }
        } catch { continue }
    }
    if ($newest) { return $newest.commit }
    return $null
}

function Get-LastRecordFailed {
    # Whether the newest update that set rollback tags stopped before it completed: then the tags still name the
    # release before it. A stop before the tags (folder, preflight, backup) does not count, and a record beside
    # an update.json belongs to a run that completed.
    $files = @(Get-ChildItem -LiteralPath $BackupRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -in @('update.json', 'update-failed.json') } | Sort-Object LastWriteTimeUtc -Descending)
    foreach ($file in $files) {
        if ($file.Name -eq 'update.json') { return $false }
        if (Test-Path -LiteralPath (Join-Path $file.DirectoryName 'update.json')) { return $false }
        try { $found = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json } catch { continue }
        if ($null -ne $found.steps -and $null -ne $found.steps.rollback_tags) { return $true }
    }
    return $false
}

function Get-LeftStopped {
    # The services a stopped run's migration stop (ExecPlan 0060) left stopped: named by the newest record, since the
    # last completed update, of a run that knew them (the services its migration stop stopped, and those its preflight
    # found left so), less those its undo started again. A completed update leaves none.
    $files = @(Get-ChildItem -LiteralPath $BackupRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -in @('update.json', 'update-failed.json') } | Sort-Object LastWriteTimeUtc -Descending)
    foreach ($file in $files) {
        if ($file.Name -eq 'update.json') { return @() }
        if (Test-Path -LiteralPath (Join-Path $file.DirectoryName 'update.json')) { return @() }
        try { $found = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json } catch { continue }
        if ($null -eq $found.steps) { continue }
        $halt = $found.steps.migration_stop
        # Assigned, not the output of an if statement: that would unroll an empty list to nothing.
        $before = $null
        if ($null -ne $found.steps.preflight) { $before = $found.steps.preflight.left_stopped }
        if ($null -eq $before -and $null -eq $halt) { continue }
        $names = @()
        $again = @()
        if ($null -ne $before) { $names += @($before) }
        if ($null -ne $halt) {
            $names += @($halt.stopped)
            $again += @($halt.started_again)
        }
        return @($names | ForEach-Object { "$_" } | Where-Object { $_ -and $_ -notin $again } | Select-Object -Unique)
    }
    return @()
}

function Save-Record {
    param([string]$Status, [string]$Message = '')
    $record.status = $Status
    $record.finished_utc = [DateTime]::UtcNow.ToString('o')
    $record.stage = $stage
    $record.services_replaced = @($replaced)
    if ($Message) { $record.message = $Message }
    $name = if ($Status -eq 'COMPLETE') { 'update.json' } else { 'update-failed.json' }
    if ($backup) { $directory = Split-Path -Parent $backup.path }
    else {
        $directory = Join-Path $BackupRoot "update-record-$stamp"
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }
    $out = Join-Path $directory $name
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $out -Encoding UTF8
    return $out
}

function Remove-OldLeftovers {
    # After a completed update (ExecPlan 0034): the database dumps older than the newest three under the backup root
    # (never this run's, nor those of stopped runs since the last completed one),
    # and this app's images that no service of the update's profiles uses (an image named <project>-<service> keeps
    # :latest and :before-update; every other tag, the test and tool images, and this app's untagged builds go; a
    # test run builds its images again). Each by its exact name or id, never with
    # -f and never a prune: an image a container still uses stays.
    $result = [ordered]@{ dumps_deleted = @(); bytes_freed = [long]0; images_removed = @(); images_left = @() }
    # The copy the futures app's clean start made (ExecPlan 0039 section 5.1) is the owner's to delete, never the tidy
    # step's.
    $dumps = @(Get-ChildItem -LiteralPath $BackupRoot -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne $keptFolder } | ForEach-Object {
            Get-ChildItem -LiteralPath $_.FullName -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*.dump' }
        } | Sort-Object LastWriteTimeUtc -Descending)
    # The backups of the stopped runs since the last completed one stay too: the rollback tags may still name the
    # release before the first of them, and its backup is the one that matches those images.
    $kept = @{}
    $records = @(Get-ChildItem -LiteralPath $BackupRoot -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -in @('update.json', 'update-failed.json') } | Sort-Object LastWriteTimeUtc -Descending)
    # This run's own record (saved at step 8) is skipped: the walk starts at the run before it.
    $own = if ($backup) { Split-Path -Parent $backup.path } else { Join-Path $BackupRoot "update-record-$stamp" }
    foreach ($file in $records) {
        if ($file.DirectoryName -eq $own) { continue }
        if ($file.Name -eq 'update.json' -or (Test-Path -LiteralPath (Join-Path $file.DirectoryName 'update.json'))) { break }
        $kept[$file.DirectoryName] = $true
    }
    foreach ($dump in @($dumps | Select-Object -Skip 3)) {
        if ($backup -and $dump.FullName -eq $backup.path) { continue }
        if ($kept.ContainsKey($dump.DirectoryName)) { continue }
        $result.bytes_freed += $dump.Length
        Remove-Item -LiteralPath $dump.FullName -Force
        $sha = "$($dump.FullName).sha256"
        if (Test-Path -LiteralPath $sha) { Remove-Item -LiteralPath $sha -Force }
        $result.dumps_deleted += $dump.FullName
    }
    $names = @()
    foreach ($line in @(Invoke-Native @('image', 'ls', '--format', '{{.Repository}}|{{.Tag}}'))) {
        $parts = "$line".Split('|')
        if ($parts.Count -ne 2 -or -not $parts[0].StartsWith("$Project-") -or $parts[1] -eq '<none>') { continue }
        $service = $parts[0].Substring($Project.Length + 1)
        if ($services.Contains($service) -and ($parts[1] -eq 'latest' -or $parts[1] -eq 'before-update')) { continue }
        $names += "$($parts[0]):$($parts[1])"
    }
    $names += @(Invoke-Native @('image', 'ls', '-q', '--no-trunc', '--filter', 'dangling=true', '--filter',
            "label=com.docker.compose.project=$Project") | ForEach-Object { "$_".Trim() } | Where-Object { $_ -match '^sha256:[0-9a-f]{64}$' })
    foreach ($name in $names) {
        $output = Invoke-Native @('image', 'rm', $name)
        if ($LASTEXITCODE -eq 0) { $result.images_removed += $name } else { $result.images_left += "${name}: $(($output | Select-Object -Last 1))" }
    }
    return $result
}

function Remove-MergedBranches {
    # Step 9. Deletes only branches whose tip main reaches through a merge: a branch that points into main's own
    # first-parent history (a new branch not yet worked on) is kept, and git refuses a branch with unmerged work.
    $result = [ordered]@{ deleted_on_github = @(); deleted_here = @(); kept = @(); failed = @(); unmerged_here = @() }
    Invoke-Git @('fetch', '--prune', '--quiet', 'origin') | Out-Null
    $line = @{}
    foreach ($commit in (Invoke-Git @('rev-list', '--first-parent', 'origin/main'))) { $line["$commit".Trim()] = $true }
    foreach ($ref in (Invoke-Git @('branch', '-r', '--merged', 'origin/main', '--format=%(refname:short)'))) {
        $ref = "$ref".Trim()
        if (-not $ref.StartsWith('origin/') -or $ref -in @('origin/main', 'origin/HEAD')) { continue }
        $branch = $ref.Substring(7)
        $tip = "$(Invoke-Git @('rev-parse', $ref) | Select-Object -Last 1)".Trim()
        if ($line.ContainsKey($tip)) { $result.kept += "$branch (GitHub; points into main's own history)"; continue }
        # Only the tip checked above: a push to the branch since the fetch makes GitHub refuse the delete.
        $output = Invoke-Git @('push', '--quiet', "--force-with-lease=refs/heads/$($branch):$tip", 'origin', ":refs/heads/$branch") -AllowFailure
        if ($script:GitCode -eq 0) { $result.deleted_on_github += $branch }
        else { $result.failed += "$branch (GitHub): $((@($script:GitErrors) + @($output) | Select-Object -Last 1))" }
    }
    $current = "$(Invoke-Git @('rev-parse', '--abbrev-ref', 'HEAD') | Select-Object -Last 1)".Trim()
    foreach ($branch in (Invoke-Git @('branch', '--merged', 'main', '--format=%(refname:short)'))) {
        $branch = "$branch".Trim()
        if (-not $branch -or $branch -in @('main', $current)) { continue }
        $tip = "$(Invoke-Git @('rev-parse', $branch) | Select-Object -Last 1)".Trim()
        if ($line.ContainsKey($tip)) { $result.kept += "$branch (this folder; points into main's own history)"; continue }
        $output = Invoke-Git @('branch', '-d', $branch) -AllowFailure
        if ($script:GitCode -eq 0) { $result.deleted_here += $branch }
        else { $result.kept += "$branch (this folder): $((@($script:GitErrors) + @($output) | Select-Object -Last 1))" }
    }
    $result.unmerged_here = @(Invoke-Git @('branch', '--no-merged', 'main', '--format=%(refname:short)') | ForEach-Object { "$_".Trim() } | Where-Object { $_ })
    return $result
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
$transcript = Join-Path $BackupRoot "update-$stamp.log"
$transcribing = $false
try { Start-Transcript -LiteralPath $transcript -Append | Out-Null; $transcribing = $true } catch { $transcribing = $false }
try {
    $awake = Set-KeepAwake $true
    Say "Update of the app in $Repository ($([DateTime]::UtcNow.ToString('yyyy-MM-dd HH:mm')) UTC). Nothing to answer: it says when it is done."
    if (-not $Model -and -not $awake) { Say 'NOTE: the PC could not be kept awake; keep it from sleeping until this window says it is done.' }

    Say '[1/9] The folder: main, as on GitHub'
    $changed = @(Invoke-Git @('status', '--porcelain', '--untracked-files=no') | Where-Object { "$_".Trim() })
    if ($changed.Count) {
        throw "This folder has uncommitted changes in $($changed.Count) tracked file(s), so nothing was changed: $(($changed | ForEach-Object { "$_".Substring(3) }) -join ', ')"
    }
    $fetched = $false
    for ($attempt = 1; $attempt -le 4 -and -not $fetched; $attempt++) {
        $output = Invoke-Git @('fetch', '--quiet', 'origin', 'main') -AllowFailure
        $fetched = ($script:GitCode -eq 0)
        if (-not $fetched -and $attempt -lt 4) { Start-Sleep -Seconds ([math]::Pow(2, $attempt)) }
    }
    if (-not $fetched) { throw "Could not fetch main from GitHub: $((@($script:GitErrors) + @($output) | Select-Object -Last 2) -join ' ')" }
    $branchBefore = "$(Invoke-Git @('rev-parse', '--abbrev-ref', 'HEAD') | Select-Object -Last 1)".Trim()
    $headBefore = "$(Invoke-Git @('rev-parse', 'HEAD') | Select-Object -Last 1)".Trim()
    if ($branchBefore -ne 'main') {
        Invoke-Git @('rev-parse', '--verify', '--quiet', 'refs/heads/main') -AllowFailure | Out-Null
        if ($script:GitCode -eq 0) { Invoke-Git @('checkout', '--quiet', 'main') | Out-Null }
        else { Invoke-Git @('checkout', '--quiet', '-b', 'main', '--track', 'origin/main') | Out-Null }
    }
    $ahead = "$(Invoke-Git @('rev-list', '--count', 'origin/main..main') | Select-Object -Last 1)".Trim()
    if ($ahead -ne '0') { throw "main in this folder holds $ahead commit(s) that GitHub's main lacks; the folder is on main and nothing else was changed" }
    Invoke-Git @('merge', '--ff-only', '--quiet', 'origin/main') | Out-Null
    $commit = "$(Invoke-Git @('rev-parse', 'HEAD') | Select-Object -Last 1)".Trim()
    $remote = "$(Invoke-Git @('rev-parse', 'origin/main') | Select-Object -Last 1)".Trim()
    if ($commit -ne $remote) { throw "The folder is at $commit, not at GitHub's main $remote" }
    $record.source = [ordered]@{ commit = $commit; branch_before = $branchBefore; head_before = $headBefore }
    Say "  On main at $($commit.Substring(0, 7)) (it was on $branchBefore at $($headBefore.Substring(0, 7)))."
    # A newer copy of this file came with main: it runs instead, from the folder.
    $installed = Join-Path $Repository 'tools/update.ps1'
    $theirs = if (Test-Path -LiteralPath $installed) { [IO.File]::ReadAllText($installed) } else { '' }
    # Compared without line-end differences: a Windows checkout writes CRLF, git show writes the stored LF.
    if ($mine.Replace("`r`n", "`n") -ne $theirs.Replace("`r`n", "`n")) {
        if ($Relaunched -or -not $theirs) { throw 'The update file in the folder is not the one running, after it was started again: nothing else was changed' }
        Say '  main brings a newer update file: it runs now.'
        if ($transcribing) { Stop-Transcript | Out-Null; $transcribing = $false }
        if ($awake) { Set-KeepAwake $false | Out-Null; $awake = $false }
        $arguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $installed, '-Project', $Project, '-Repository', $Repository,
            '-EnvFile', $EnvFile, '-BackupRoot', $BackupRoot, '-Relaunched')
        if ($Model) { $arguments += '-Model' }
        & (Get-Process -Id $PID).Path @arguments
        exit $LASTEXITCODE
    }
    Import-Module (Join-Path $Repository 'tools/lib/Pilot.psm1') -Force

    $stage = 'preflight'
    Say '[2/9] Read-only preflight'
    $compose = New-PilotCompose -Project $Project -EnvFile $EnvFile
    # A secret compose.yaml names that the folder lacks is created first, as tools/setup-local.ps1 creates each. An
    # existing secret is never read, changed, deleted or printed (the retired services' files stay too); a folder whose
    # env file names another secret directory is left to its owner.
    if (-not (Get-EnvValue -Path $compose.env_file -Name 'ASL_SECRET_DIR')) {
        $secretsBefore = @(Get-ChildItem -LiteralPath (Join-Path $Repository 'secrets') -File -ErrorAction SilentlyContinue).Count
        & (Join-Path $Repository 'tools/setup-local.ps1') | Out-Null
        $secretsAfter = @(Get-ChildItem -LiteralPath (Join-Path $Repository 'secrets') -File).Count
        if ($secretsAfter -gt $secretsBefore) { Say "  Created $($secretsAfter - $secretsBefore) missing secret file(s) under secrets/." }
    }
    $database = Get-EnvValue -Path $compose.env_file -Name 'ASL_DB_NAME' -Default 'asl'
    $version = (Invoke-Native @('version', '--format', '{{.Server.Version}}')) -join ''
    if ($LASTEXITCODE -ne 0) { throw "Docker does not answer: start Docker Desktop and run the update again ($version)" }
    $config = (Invoke-App -Arguments @('config', '--format', 'json')) -join "`n" | ConvertFrom-Json
    $services = [ordered]@{}
    foreach ($property in $config.services.PSObject.Properties) {
        $environment = @{}
        $connects = $false
        if ($property.Value.environment) {
            foreach ($entry in $property.Value.environment.PSObject.Properties) {
                if ($entry.Name -match '^ASL_[A-Z]+_ENABLED$') { $environment[$entry.Name] = "$($entry.Value)" }
                if ($entry.Name -eq 'ASL_DB_HOST') { $connects = $true }
            }
        }
        # database: the service connects to the main database.
        $services[$property.Name] = @{ build = [bool]$property.Value.build; flags = $environment; database = $connects }
    }
    foreach ($required in @('postgres', 'api', 'web', 'migrate')) { if (-not $services.Contains($required)) { throw "compose.yaml has no service $required" } }
    # The settings each service would be created with now. Unreadable, only a changed image recreates a service.
    $hashes = @{}
    $hashLines = Invoke-App -Arguments @('config', '--hash', '*') -AllowFailure
    if ($LASTEXITCODE -eq 0) {
        foreach ($line in $hashLines) { if ("$line" -match '^(\S+) ([0-9a-f]{64})$') { $hashes[$Matches[1]] = $Matches[2] } }
    }
    if (-not $hashes.Count) { Say '  NOTE: Compose did not give its config hashes: only a changed image recreates a service.' }
    $running = Get-Running
    # What a stopped run's migration stop left stopped is this run's to start again: each in the container it has until
    # its built image replaces it. One that is running again is an ordinary running service.
    $named = @(Get-LeftStopped | Where-Object { $services.Contains($_) -and $services[$_].database })
    foreach ($service in $named) {
        if (-not $running.Contains($service)) { throw "Service $service, which the stopped update left stopped, has no container: nothing was changed" }
    }
    $left = @($named | Where-Object { $running[$_].status -notin @('running', 'restarting') })
    foreach ($service in $left) { $stoppedIds[$service] = $running[$service].container }
    $stopped = @($left)
    foreach ($required in @('postgres', 'api', 'web')) {
        if ($required -in $left) { continue }
        if (-not $running.Contains($required) -or $running[$required].status -ne 'running') { throw "Service $required is not running: start the app first (docker compose up -d)" }
    }
    if ('api' -notin $left) { Test-ApiReady }
    # A flag the env file now renders otherwise than the running container has would change with the update.
    foreach ($service in $running.Keys) {
        foreach ($flag in $running[$service].flags.Keys) {
            $rendered = $services[$service].flags[$flag]
            if ($null -ne $rendered -and "$rendered" -cne "$($running[$service].flags[$flag])") {
                throw "The env file sets $flag for $service otherwise than its running container has it: the update would change it. Nothing was changed"
            }
        }
    }
    $schemaBefore = Invoke-Psql 'SELECT version_num FROM alembic_version'
    $previous = Get-PreviousCommit
    $record.steps.preflight = [ordered]@{ docker = $version; schema = $schemaBefore; previous_commit = $previous
        left_stopped = @($left); running = [ordered]@{} }
    foreach ($service in $running.Keys) { $record.steps.preflight.running[$service] = [ordered]@{ image = $running[$service].image; status = $running[$service].status } }
    Say "  Schema $schemaBefore; $($running.Count) service(s) with a container."
    if ($left.Count) { Say "  Left stopped by the stopped update, started again on their new images by this one: $($left -join ', ')" }

    $stage = 'backup'
    Say '[3/9] Protected backup and rollback tags'
    Wait-QuietTime -Minutes 10 -What 'the backup'
    $backup = New-ProtectedBackup -Compose $compose -BackupRoot $BackupRoot -Label 'update' -Database $database -RequireRoom
    $record.steps.backup = [ordered]@{ path = $backup.path; sha256 = $backup.sha256; bytes = $backup.bytes }
    Say "  Backup $($backup.path) sha256 $($backup.sha256)"
    $keepTags = Get-LastRecordFailed
    $tags = [ordered]@{}
    foreach ($service in $running.Keys) {
        if (-not $services[$service].build) { continue }
        $tag = "$Project-$($service):before-update"
        $existing = Get-ImageId $tag
        if ($existing -and $keepTags) { $tags[$service] = [ordered]@{ tag = $tag; image = $existing; moved = $false }; continue }
        Invoke-Native @('tag', $running[$service].image, $tag) | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Could not create the rollback tag $tag" }
        $tags[$service] = [ordered]@{ tag = $tag; image = $running[$service].image; moved = $true }
    }
    $record.steps.rollback_tags = $tags
    if ($keepTags) { Say '  The last update stopped early: its rollback tags are kept, so they still name the release before it.' }

    $stage = 'build'
    Say '[4/9] Build (a few minutes)'
    Wait-QuietTime -Minutes 15 -What 'the build'
    $buildable = @($services.Keys | Where-Object { $services[$_].build })
    Invoke-App -Arguments (@('build', '--quiet') + $buildable) | Out-Null
    foreach ($service in $buildable) {
        $built[$service] = Get-ImageId "$Project-$service"
        if (-not $built[$service]) { throw "Image $Project-$service was not built" }
    }
    $record.steps.built = $built

    $stage = 'migrate'
    Say '[5/9] Forward migrations'
    $heads = @(Invoke-App -Arguments @('run', '--rm', '--no-deps', 'migrate', 'alembic', '-c', '/app/alembic.ini', 'heads') |
            ForEach-Object { if ("$_" -match '^(\S+) \(head\)') { $Matches[1] } })
    if ($heads.Count -ne 1) { throw "The built code does not name one head revision ($($heads -join ', '))" }
    $head = $heads[0]
    $accepts = @(Invoke-App -Arguments @('run', '--rm', '--no-deps', 'migrate', 'python', '-c',
            "from app.db import ACCEPTED_REVISIONS; print('ACCEPTS ' + ' '.join(sorted(ACCEPTED_REVISIONS)))") |
            ForEach-Object { if ("$_" -match '^ACCEPTS (.+)$') { $Matches[1] -split ' ' } })
    if (-not $accepts.Count) { throw 'Could not read which schemas the built api accepts' }
    $record.steps.migrate = [ordered]@{ before = $schemaBefore; head = $head; api_accepts_before = ($schemaBefore -in $accepts) }
    $record.steps.recreated = [ordered]@{}
    $expand = $schemaBefore -in $accepts
    if ($expand) {
        Say '  The new api reads the schema as it is: api and web first'
        foreach ($service in @('api', 'web')) { Update-Service $service }
    }
    if ($schemaBefore -eq $head) {
        Say "  No migration: the schema is already $head"
    } else {
        Wait-QuietTime -What 'the migration'
        $stage = 'migrate'
        $migrated = $false
        $output = @()
        $command = @('run', '--rm', '--no-deps', 'migrate', 'python', '-m', 'app.migrate', $head)
        # A migration the new api needs first: its writers stop first (see the header).
        $halt = -not $expand
        try {
            if ($halt) {
                $record.steps.migration_stop = [ordered]@{ stopped = @() }
                Stop-Writers
                $stage = 'migrate'
            }
            for ($attempt = 1; $attempt -le 3 -and -not $migrated; $attempt++) {
                $output = Invoke-App -Arguments $command -AllowFailure
                $migrated = ((Get-Schema) -eq $head)
                if (-not $migrated -and $attempt -lt 3) { Start-Sleep -Seconds (5 * $attempt) }
            }
            $record.steps.migrate.attempts = $attempt - 1
            $record.steps.migrate.output = @($output | Select-Object -Last 2)
            if (-not $migrated) { throw "The migration to $head did not apply: $(($output | Select-Object -Last 2) -join ' ')" }
        } catch {
            if ($halt) { Undo-Writers $_.Exception.Message }
            throw
        }
        Say "  Migrated $schemaBefore -> $head"
    }
    $record.steps.migrate.after = Get-Schema

    $stage = 'recreate'
    Say '[6/9] Recreate the services whose image changed'
    $others = @($running.Keys | Where-Object { $_ -notin $mainOrder -and $_ -notin $lastOrder })
    foreach ($service in @($mainOrder + $others + $lastOrder)) { Update-Service $service }
    if (-not $replaced.Count) { Say '  Every running service already runs its built image' }
    elseif ($current.Count) { Say "  Already on their built images: $($current -join ', ')" }

    $stage = 'verify'
    Say '[7/9] Verify'
    $after = Get-Running
    $problems = @()
    $head2 = "$(Invoke-Git @('rev-parse', 'HEAD') | Select-Object -Last 1)".Trim()
    if ($head2 -ne $commit) { $problems += "the folder moved to $head2 during the update" }
    foreach ($service in $running.Keys) {
        if (($running[$service].status -ne 'running' -and $service -notin $left) -or -not $built.Contains($service)) { continue }
        if (-not $after.Contains($service)) { $problems += "$service has no container"; continue }
        if ($after[$service].status -ne 'running') { $problems += "$service is $($after[$service].status)" }
        if ($after[$service].image -ne $built[$service]) { $problems += "$service does not run its built image" }
    }
    Test-ApiReady
    $schemaAfter = Get-Schema
    if ($schemaAfter -ne $head) { $problems += "the schema is $schemaAfter, not $head" }
    $reconcile = @(Invoke-PilotCompose -Compose $compose -Arguments @('exec', '-T', 'api', 'python', '-c',
            "from app import accounting; print('RECONCILE ' + accounting.reconcile()['status'])") |
            ForEach-Object { if ("$_" -match '^RECONCILE (\S+)$') { $Matches[1] } })
    if ($reconcile.Count -ne 1 -or $reconcile[0] -ne 'OK') { $problems += "the reconciliation is not OK ($($reconcile -join ' '))" }
    $fetch = "Promise.all([" + (($pages | ForEach-Object { "'$_'" }) -join ',') + "].map(p => fetch('http://127.0.0.1:3000' + p)" +
        ".then(r => p + '=' + r.status).catch(() => p + '=ERR'))).then(s => console.log('PAGES ' + s.join(' ')))"
    $answers = @(Invoke-PilotCompose -Compose $compose -Arguments @('exec', '-T', 'web', 'node', '-e', $fetch) |
            ForEach-Object { if ("$_" -match '^PAGES (.+)$') { $Matches[1] -split ' ' } })
    $bad = @($pages | Where-Object { "$_=200" -notin $answers })
    if ($bad.Count) { $problems += "page(s) not answering: $($bad -join ', ') ($($answers -join ' '))" }
    $record.steps.verify = [ordered]@{ schema = $schemaAfter; reconciliation = ($reconcile -join ' '); pages = $answers; problems = $problems }
    if ($problems.Count) { throw "The check after the update failed: $($problems -join '; ')" }
    Say "  Schema $schemaAfter, api ready, reconciliation OK, pages answer."
    $stage = 'read-out'
    Show-ReadOut

    $stage = 'record'
    Say '[8/9] Record, and what this update changes'
    $out = Save-Record 'COMPLETE'
    $range = @($commit)
    if ($previous -and $previous -ne $commit) {
        Invoke-Git @('merge-base', '--is-ancestor', $previous, $commit) -AllowFailure | Out-Null
        if ($script:GitCode -eq 0) { $range = @(Invoke-Git @('rev-list', '--first-parent', '--max-count=30', "$previous..$commit") | ForEach-Object { "$_".Trim() }) }
    } elseif ($previous -eq $commit) { $range = @() }
    if (-not $range.Count) { Say '  The same commit as the last update: nothing new.' }
    foreach ($item in $range) {
        $message = @(Invoke-Git @('log', '-1', '--format=%B', $item))
        $note = @(Get-ReleaseNote $message)
        # A merge of a pull request names it on its first line and gives its title after that.
        $lines = @($message | ForEach-Object { "$_".Trim() } | Where-Object { $_ })
        $title = if ($lines.Count -gt 1 -and $lines[0] -like 'Merge pull request *') { $lines[1] } elseif ($lines.Count) { $lines[0] } else { $item }
        Say "  - $title"
        foreach ($line in $note) { Say "      $line" }
    }
    Say "  Record: $out"

    $stage = 'github'
    Say '[9/9] Tidy: merged branches, old backups and old images'
    try {
        $tidy = Remove-MergedBranches
        $record.steps.github = $tidy
        Say "  Deleted on GitHub: $(if ($tidy.deleted_on_github.Count) { $tidy.deleted_on_github -join ', ' } else { 'none' })"
        if ($tidy.deleted_here.Count) { Say "  Deleted in this folder: $($tidy.deleted_here -join ', ')" }
        foreach ($item in $tidy.failed) { Say "  NOT deleted: $item" }
        if ($tidy.unmerged_here.Count) { Say "  In this folder with work main does not have (kept): $($tidy.unmerged_here -join ', ')" }
    } catch {
        $record.steps.github = "not done: $($_.Exception.Message)"
        Say "  NOT done: $($_.Exception.Message). The update itself is complete."
    }
    Say '  Old backups and images'
    try {
        $leftovers = Remove-OldLeftovers
        $record.steps.leftovers = $leftovers
        Say "  Deleted $($leftovers.dumps_deleted.Count) old backup(s) ($([math]::Round($leftovers.bytes_freed / 1GB, 1)) GB); removed $($leftovers.images_removed.Count) old image(s)."
        foreach ($item in $leftovers.images_left) { Say "  Kept (in use or refused): $item" }
    } catch {
        $record.steps.leftovers = "not done: $($_.Exception.Message)"
        Say "  NOT done: $($_.Exception.Message). The update itself is complete."
    }
    Save-Record 'COMPLETE' | Out-Null
    Say "DONE: the app runs $($commit.Substring(0, 7)). Nothing else is needed."
} catch {
    $failure = $_.Exception.Message
    $out = $null
    try { $out = Save-Record 'FAILED' $failure } catch { $out = $null }
    Say "STOPPED at '$stage': $failure"
    if ($replaced.Count) { Say "Replaced before the stop: $($replaced -join ', '). The others run as before." }
    else { Say 'No running service was replaced.' }
    $again = @()
    if ($record.steps.Contains('migration_stop') -and $record.steps.migration_stop.Contains('started_again')) { $again += @($record.steps.migration_stop.started_again) }
    $down = @($stopped | Where-Object { $_ -notin $replaced -and $_ -notin $again })
    if ($down.Count) { Say "Stopped by the update and not started again: $($down -join ', '). The next update starts them on its new images." }
    if ($compose -and $database -and $stage -notin @('folder', 'preflight')) {
        try { Say "Schema now: $(Get-Schema)" } catch { Say 'Schema now: not read' }
    }
    if ($backup) { Say "Backup: $($backup.path) sha256 $($backup.sha256)" }
    if ($out) { Say "Record: $out" }
    Say 'Tell Claude in the project thread; the fix comes as a new update.'
    if ($transcribing) { Stop-Transcript | Out-Null; $transcribing = $false }
    if ($awake) { Set-KeepAwake $false | Out-Null }
    exit 1
}
if ($transcribing) { Stop-Transcript | Out-Null }
if ($awake) { Set-KeepAwake $false | Out-Null }
exit 0
