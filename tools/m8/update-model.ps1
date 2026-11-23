param(
    [Parameter(Mandatory = $true)][string]$Repository,
    # An existing directory of the caller; a folder 'update-model' is made in it and removed again.
    [Parameter(Mandatory = $true)][string]$Work,
    [string]$Only = '',
    # Print what each run of the update file said, for a scenario that fails.
    [switch]$Show
)

# tools/update.ps1 against a MODEL of the owner's installation (ExecPlan 0031 section 5, S8), as
# tools/m7/deploy-model.ps1 is for tools/m7-deploy.ps1. No Docker command runs: every directory that holds a
# docker executable is taken out of this process's PATH first, and a PowerShell function named docker answers
# instead, from a small model (services, containers, image names, the schema, the account). Git is real: each scenario
# builds a scratch "GitHub" (a bare repository) and the owner's folder (a clone of it) holding the update file, its
# module and tools/setup-local.ps1 byte for byte, and the update file runs from that folder, in this process, with
# -Model (no wait near midnight, no keep-awake call).
# The model is the spot app as the owner's PC runs it since 2026-11-12 (ExecPlan 0061): schema 0041_spot, the api,
# the web and the two workers running, no container or network of a retired service. The release brings a
# HYPOTHETICAL contract migration, 0042_model, which the new api needs first (no such migration exists).
# What it shows: the folder put on main or left alone with its changed files named; the backup, tags, builds; the
# workers stopped before a migration the new api needs first, and started again by their ids when it does not apply;
# the migration and the recreations in their order; a stop that is never reported as success, the services a stopped
# run left stopped started on their new images by the next; the read-out of the spot app; the record, the release
# note, and which branches and backups step 9 deletes and keeps (never the before-futures copy); no step of the paths
# ExecPlan 0061 removed (the futures account's preflight, the clean start, the retired services, the sign-in starter);
# and the quiet window of tools/update.ps1 and tools/docker-cleanup.ps1 (23:55 to 00:10 UTC).
# What it does not show: anything about Docker, Compose or PostgreSQL; the first real run is the PC's update.
# The last line of output is one JSON document; the exit code is 1 when an expectation did not hold.
# Windows PowerShell 5.1 compatible; ASCII only.
$ErrorActionPreference = 'Stop'
$separator = [IO.Path]::PathSeparator
$realGit = (Get-Command git -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
$env:PATH = (($env:PATH -split [regex]::Escape("$separator")) | Where-Object {
        $entry = $_
        $holds = $true
        try {
            $holds = (-not $entry) -or (Test-Path -LiteralPath (Join-Path $entry 'docker')) -or (Test-Path -LiteralPath (Join-Path $entry 'docker.exe')) -or
                (Test-Path -LiteralPath (Join-Path $entry 'docker.cmd'))
        } catch { $holds = $true }
        -not $holds }) -join "$separator"
if (Get-Command docker -CommandType Application -ErrorAction SilentlyContinue) { throw 'A real docker is still reachable from this process: nothing is run.' }
foreach ($file in @('tools/update.ps1', 'tools/lib/Pilot.psm1', 'tools/setup-local.ps1', 'tools/docker-cleanup.ps1')) {
    if (-not (Test-Path -LiteralPath (Join-Path $Repository $file) -PathType Leaf)) { throw "$file was not found." }
}
if (-not (Test-Path -LiteralPath $Work -PathType Container)) { throw 'The work directory does not exist.' }
$work = Join-Path (Resolve-Path -LiteralPath $Work).Path 'update-model'
if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
New-Item -ItemType Directory -Path $work | Out-Null
if (-not (Get-Command git -CommandType Application -ErrorAction SilentlyContinue)) {
    # On Linux git and docker share /usr/bin: git alone comes back through a link of its own.
    New-Item -ItemType Directory -Path (Join-Path $work 'bin') | Out-Null
    New-Item -ItemType SymbolicLink -Path (Join-Path $work 'bin/git') -Target $realGit | Out-Null
    $env:PATH = (Join-Path $work 'bin') + "$separator" + $env:PATH
}

$project = 'asl-model-update'
# The schema the PC runs, and the release's head: a HYPOTHETICAL contract migration (no such migration exists).
$S9 = '0041_spot'
$S10 = '0042_model'
$envFile = Join-Path $work 'model.env'
[IO.File]::WriteAllText($envFile, "ASL_DB_NAME=asl_model`nASL_MARKET_ENABLED=1`nASL_EXECUTION_ENABLED=1`n")
# The services of the release, as the model's compose config renders them: build, and the flags each container is
# created with.
$serviceFlags = [ordered]@{
    'postgres' = $null
    'migrate' = @{}; 'api' = @{}; 'web' = @{}; 'market-worker' = @{ ASL_MARKET_ENABLED = '1' }
    'execution-worker' = @{ ASL_EXECUTION_ENABLED = '1' }
}
$runningServices = @('postgres', 'api', 'web', 'market-worker', 'execution-worker')
$pageList = @('/', '/trades', '/backtest', '/settings')
# The services compose.yaml gives ASL_DB_HOST: the ones that connect to the main database.
$databaseServices = @('migrate', 'api', 'market-worker', 'execution-worker')
$mainDatabase = 'asl_model'
# The read-out of the spot app after the update, as the PC's read (SYNTHETIC values).
$feedRead = '{"status": "CONNECTED", "reason": null, "written": "14:02:11", "instrument": "TRADING, usable", "clock": true, "history": true, "days": 3009, "first_day": "2017-08-17", "last_day": "2026-11-11", "candles": 2880}'
$accountRead = '{"funded": true, "cash": "9959.88", "btc": "0", "run": {"seq": 1, "state": "RUNNING", "causes": []}, "reading": {"day": "2026-11-12", "result": "CASH", "action": "NO_CHANGE", "outcome": "NO_CHANGE", "target": "0", "codes": []}, "fills": 0, "backtest": {"computed": "2026-11-12 14:03", "days": 3009, "first_day": "2017-08-17", "last_day": "2026-11-11"}, "funding": "POSTED"}'
$fundedRead = '{"funded": true, "cash": "10000.00", "btc": "0", "run": {"seq": 1, "state": "RUNNING", "causes": []}, "reading": null, "fills": 0, "backtest": null, "funding": "POSTED"}'
$unfundedRead = '{"funded": false, "cash": "0.00", "btc": "0", "run": null, "reading": null, "fills": 0, "backtest": null, "funding": null}'

function global:Start-Sleep { }
function global:icacls { $global:LASTEXITCODE = 0 }

function New-ModelId { return 'sha256:' + (-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })) }

function New-ModelHash { return (-join ((1..64) | ForEach-Object { '{0:x}' -f (Get-Random -Maximum 16) })) }

function New-ModelContainer {
    # A container of this project with Compose's labels.
    param([string]$Service, [string]$Image, [string]$Hash, [string]$Status = 'running')
    $flags = $serviceFlags[$Service]
    $environment = @('PATH=/usr/local/bin:/usr/bin')
    if ($flags) { foreach ($key in $flags.Keys) { $environment += "$key=$($flags[$key])" } }
    $global:ModelClock++
    $started = ([DateTime]::new(2026, 11, 13, 12, 0, 0, [DateTimeKind]::Utc)).AddSeconds($global:ModelClock).ToString('o')
    return @{ id = (New-ModelId).Substring(7); service = $Service; image = $Image; status = $Status; restarts = '0'; started = $started; env = $environment
        hash = $Hash; oneoff = 'False'; project = $project }
}

function Reset-Model {
    # The spot app at 0041, as on the owner's PC; this release's builds give other images.
    $global:ModelClock = 0
    $old = @{}
    $new = @{}
    # Compose's config hash of each service, as compose.yaml and the env file render it.
    $hashes = @{}
    foreach ($service in $serviceFlags.Keys) { $old[$service] = New-ModelId; $new[$service] = New-ModelId; $hashes[$service] = New-ModelHash }
    $names = @{}
    foreach ($service in $old.Keys) { $names["$project-$service"] = $old[$service] }
    $containers = @{}
    foreach ($service in $runningServices) { $containers[$service] = @(New-ModelContainer $service $old[$service] $hashes[$service]) }
    $global:Model = @{ schema = $S9; head = $S10; accepts = $S10; old = $old; new = $new; names = $names; containers = $containers
        calls = New-Object System.Collections.Generic.List[string]; hashes = $hashes
        failMigration = $false; migrations = 0; reconcile = 'OK'; pages = '200'; lease = 'true'
        # What the read-out reads after the update; accountAfterApi is what the account reads once the new api has
        # started (ExecPlan 0042: it funds an account nothing has funded).
        feed = $feedRead; account = $accountRead; accountAfterApi = ''; archive = '{"tables": 131, "retired": 1}'
        # The web's health check reads the home page, which reads the api. ExecPlan 0042's web signs nobody in and the
        # api before it answers 401, so a new web's --wait fails while the api runs its old image, as on the owner's PC
        # on 2026-10-25.
        webNeedsNewApi = $true
        # stoppedBy and startedBy note each service Compose stopped and each container started by its id;
        # runningAtMigration the services with a running container when the migration applied.
        stoppedBy = New-Object System.Collections.Generic.List[string]; startedBy = New-Object System.Collections.Generic.List[string]
        recreated = New-Object System.Collections.Generic.List[string]; migratedAt = -1; runningAtMigration = @()
        # crashOnUp names a service whose new container exits at once; refuseStart one whose container Docker will not
        # start again.
        crashOnUp = ''; refuseStart = ''
        # Leftovers the tidy step meets: an old rollback tag, a retired service's image, an image a container still
        # uses (Docker refuses it), another project's image, and one untagged build of this app.
        extraImages = @("$project-api:pre-m7", "$project-agent-worker:latest", "$project-web-tools:latest", 'other-app-web:latest')
        inUse = @("$project-web-tools:latest"); dangling = @('sha256:' + ('ab' * 32)); removedImages = New-Object System.Collections.Generic.List[string] }
}

function Get-ModelConfig {
    $services = [ordered]@{}
    foreach ($service in $serviceFlags.Keys) {
        if ($null -eq $serviceFlags[$service]) { $services[$service] = @{ image = 'postgres:17.11-alpine3.24' }; continue }
        $environment = @{} + $serviceFlags[$service]
        if ($service -in $databaseServices) { $environment['ASL_DB_HOST'] = 'postgres' }
        $services[$service] = @{ build = @{ context = '.'; target = 'runtime' }; environment = $environment }
    }
    return (@{ services = $services } | ConvertTo-Json -Depth 6)
}

function Find-ModelContainer {
    param([string]$Id)
    foreach ($service in @($global:Model.containers.Keys)) {
        foreach ($container in $global:Model.containers[$service]) { if ($container.id -eq $Id -or $Id -like "$($container.id)*") { return $container } }
    }
    return $null
}

function Get-ModelRunning {
    # The services with a running container of this project, postgres aside, sorted.
    $m = $global:Model
    return @(@($m.containers.Keys) | Where-Object { $_ -ne 'postgres' -and @($m.containers[$_] | Where-Object { $_.status -eq 'running' }).Count } | Sort-Object)
}

function Get-ModelSql {
    # psql's answer on the main database. Only the statements the update file of ExecPlan 0061 makes have an answer:
    # any other (the futures account's check, the clean start's renames) is an error of the model, so a scenario fails.
    param([string]$Sql, [string]$On)
    $m = $global:Model
    if ($On -ne $mainDatabase) { throw "The model has no database $On" }
    if ($Sql -match "to_regclass\('public\.alembic_version'\)") { if ($m.schema) { return 'f' } else { return 't' } }
    if ($Sql -match 'FROM alembic_version') { return $m.schema }
    if ($Sql -match 'FROM execution_lease') { return $m.lease }
    if ($Sql -match 'pg_database_size') { return '1048576' }
    if ($Sql -match 'FROM spot_feed_state s WHERE s\.id = 1$') { return $m.feed }
    if ($Sql -match 'FROM account_state a WHERE a\.id = 1$') { return $m.account }
    if ($Sql -match 'FROM archive\.moved_objects') { return $m.archive }
    throw "The model has no answer for: $Sql"
}

function global:docker {
    $a = @($args | ForEach-Object { "$_" })
    $m = $global:Model
    $global:LASTEXITCODE = 0
    if ($a[0] -eq 'compose') {
        $i = 1
        while ($i -lt $a.Count -and $a[$i] -in @('-f', '-p', '--env-file', '--profile')) { $i += 2 }
        $sub = $a[$i]
        $rest = @($a | Select-Object -Skip ($i + 1))
        # Noted without the file, project, env file and profile options: 'compose <command> <arguments>'.
        $m.calls.Add((@('compose', $sub) + $rest) -join ' ')
        switch ($sub) {
            'config' {
                if ($rest -contains '--hash') { return @($m.hashes.Keys | ForEach-Object { "$_ $($m.hashes[$_])" }) }
                return (Get-ModelConfig)
            }
            'ps' { return $m.containers['postgres'][0].id }
            'build' {
                foreach ($service in @($rest | Where-Object { $_ -notlike '--*' })) { $m.names["$project-$service"] = $m.new[$service] }
                return 'built'
            }
            'exec' {
                $service = $rest[1]
                $command = @($rest | Select-Object -Skip 2)
                if ($service -eq 'postgres' -and $command[0] -eq 'psql') {
                    $on = $command[[array]::IndexOf($command, '-d') + 1]
                    return (Get-ModelSql $command[-1] $on)
                }
                if ($service -eq 'postgres' -and $command[0] -eq 'df') {
                    return @('Filesystem 1024-blocks Used Available Capacity Mounted on', 'overlay 100000000 1000 90000000 1% /var/lib/postgresql/data')
                }
                if ($service -eq 'postgres') { return '' }  # pg_dump, rm
                if ($service -eq 'api' -and ($command -join ' ') -match 'RECONCILE') { return "RECONCILE $($m.reconcile)" }
                if ($service -eq 'api') { return '' }  # ready
                if ($service -eq 'web') { return ('PAGES ' + (($pageList | ForEach-Object { "$_=$($m.pages)" }) -join ' ')) }
                throw "The model has no answer for exec in $service"
            }
            'run' {
                $words = @($rest | Where-Object { $_ -notin @('--rm', '--no-deps') })
                $service = $words[0]
                $line = ($words -join ' ')
                if ($service -eq 'migrate' -and $line -match 'alembic .* heads') { return "$($m.head) (head)" }
                if ($service -eq 'migrate' -and $line -match 'ACCEPTED_REVISIONS') { return "ACCEPTS $($m.accepts)" }
                if ($service -eq 'migrate' -and $line -match ' -m app\.migrate( |$)') {
                    if ($words -contains '--keep-logins') { throw 'The model has no --keep-logins since ExecPlan 0061' }
                    $m.migrations++
                    if ($m.failMigration) { $global:LASTEXITCODE = 1; return 'psycopg.errors.LockNotAvailable: lock timeout' }
                    $m.runningAtMigration = @(Get-ModelRunning)
                    $m.schema = $m.head
                    $m.migratedAt = $m.calls.Count
                    return 'VERIFIED: migration completed in 1 bounded attempt(s).'
                }
                throw "The model has no answer for run $line"
            }
            'stop' {
                foreach ($service in @($rest | Where-Object { $_ -notlike '--*' })) {
                    $m.containers[$service][0].status = 'exited'
                    $m.stoppedBy.Add($service)
                }
                return ''
            }
            'start' {
                # As on the owner's PC on 2026-10-24: Compose refuses a service whose one-shot migrate dependency has no
                # container ('run --rm' never leaves one).
                foreach ($service in @($rest | Where-Object { $_ -notlike '--*' })) {
                    if ($service -in $databaseServices) {
                        $global:LASTEXITCODE = 1
                        return "$service is missing dependency migrate"
                    }
                    $m.containers[$service][0].status = 'running'
                }
                return ''
            }
            'up' {
                $service = $rest[-1]
                $container = New-ModelContainer $service $m.names["$project-$service"] $m.hashes[$service]
                if ($m.crashOnUp -eq $service) { $container.status = 'exited' }
                $m.containers[$service] = @($container)
                $m.recreated.Add($service)
                if ($service -eq 'api' -and $m.accountAfterApi) { $m.account = $m.accountAfterApi }
                if ($service -eq 'web' -and $rest -contains '--wait' -and $m.webNeedsNewApi -and $m.containers['api'][0].image -ne $m.new['api']) {
                    $global:LASTEXITCODE = 1
                    return "container $project-web-1 is unhealthy"
                }
                return ''
            }
        }
        throw "The model has no answer for compose $sub"
    }
    $m.calls.Add(($a -join ' '))
    if ($a[0] -eq 'version') { return '28.5.1' }
    if ($a[0] -eq 'start' -and $a.Count -eq 2) {
        # docker start by a container's full id: the container it was, on the image it had.
        $container = Find-ModelContainer $a[1]
        if (-not $container -or $a[1] -ne $container.id) { $global:LASTEXITCODE = 1; return "Error response from daemon: No such container: $($a[1])" }
        if ($m.refuseStart -eq $container.service) { $global:LASTEXITCODE = 1; return "Error response from daemon: cannot start container $($a[1])" }
        $container.status = 'running'
        $m.startedBy.Add($container.service)
        return $a[1]
    }
    if ($a[0] -eq 'ps') {
        # Docker's filters: every label filter must hold (by exact value), and without -a only running containers
        # are listed.
        $filters = @($a | Where-Object { $_ -like 'label=*' } | ForEach-Object { $_.Substring(6) })
        $all = @()
        foreach ($service in @($m.containers.Keys)) { $all += @($m.containers[$service]) }
        $listed = @($all | Where-Object {
                $container = $_
                $unmet = @($filters | Where-Object {
                        $pair = $_.Split('=', 2)
                        $value = $null
                        if ($pair[0] -eq 'com.docker.compose.project') { $value = $container.project }
                        if ($pair[0] -eq 'com.docker.compose.service') { $value = $container.service }
                        if ($pair[0] -eq 'com.docker.compose.oneoff') { $value = $container.oneoff }
                        $value -cne $pair[1]
                    })
                ($a -contains '-a' -or $container.status -eq 'running') -and -not $unmet.Count
            })
        return @($listed | ForEach-Object { $_.id })
    }
    if ($a[0] -eq 'inspect') {
        $container = Find-ModelContainer $a[-1]
        if (-not $container) { $global:LASTEXITCODE = 1; return "Error: No such object: $($a[-1])" }
        if ($a[2] -like '*Config.Env*') { return (ConvertTo-Json -InputObject @($container.env) -Compress) }
        if ($a[2] -like '*Config.Labels*') { return (@{ 'com.docker.compose.config-hash' = $container.hash } | ConvertTo-Json -Compress) }
        return "$($container.id)|$($container.image)|$($container.status)|$($container.restarts)|$($container.started)"
    }
    if ($a[0] -eq 'image' -and $a[1] -eq 'inspect') {
        $name = $a[-1]
        if ($m.names.Contains($name)) { return $m.names[$name] }
        $global:LASTEXITCODE = 1
        return "Error response from daemon: No such image: $name"
    }
    if ($a[0] -eq 'image' -and $a[1] -eq 'ls' -and $a -contains 'dangling=true') { return $m.dangling }
    if ($a[0] -eq 'image' -and $a[1] -eq 'ls') {
        $tagged = @($m.names.Keys | Where-Object { $_ -notlike 'sha256:*' } | ForEach-Object {
                if ($_ -match ':') { $_.Replace(':', '|') } else { "$_|latest" } })
        return @($tagged + @($m.extraImages | ForEach-Object { $_.Replace(':', '|') }))
    }
    if ($a[0] -eq 'image' -and $a[1] -eq 'rm') {
        if ($m.inUse -contains $a[2]) { $global:LASTEXITCODE = 1; return "Error response from daemon: conflict: unable to remove $($a[2]) (in use)" }
        $m.removedImages.Add($a[2])
        return "Untagged: $($a[2])"
    }
    if ($a[0] -eq 'tag') { $m.names[$a[2]] = $(if ($a[1] -like 'sha256:*') { $a[1] } else { $m.names[$a[1]] }); return '' }
    if ($a[0] -eq 'cp') { [IO.File]::WriteAllText($a[2], 'model dump'); return '' }
    # Containers and networks removed or stopped by id (the retired services' path of ExecPlan 0060) have no answer:
    # the update file of ExecPlan 0061 makes no such call.
    throw "The model has no answer for docker $($a -join ' ')"
}

function Invoke-ModelGit {
    param([string]$Directory, [string[]]$Arguments)
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $out = @(& git -C $Directory -c user.name=model -c user.email=model@example.invalid -c init.defaultBranch=main @Arguments 2>&1 | ForEach-Object { "$_" }) }
    finally { $ErrorActionPreference = $saved }
    if ($LASTEXITCODE -ne 0) { throw "git $($Arguments -join ' ') failed in ${Directory}: $($out -join ' ')" }
    return $out
}

function New-ModelGit {
    # A scratch GitHub and the owner's folder. main: a start, then two pull requests merged with merge commits
    # (the second carries a release note). Branches: merged-pr (merged), fresh (a new branch at a main commit),
    # unmerged (a commit main lacks), codex/side (merged; the folder stands on it at an older commit).
    param([string]$Name)
    $root = Join-Path $work $Name
    $seed = Join-Path $root 'seed'
    $hub = Join-Path $root 'github.git'
    $folder = Join-Path $root 'folder'
    New-Item -ItemType Directory -Path (Join-Path $seed 'tools/lib') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $Repository 'tools/update.ps1') -Destination (Join-Path $seed 'tools/update.ps1')
    # The update runs it to create a secret file compose.yaml names that the folder lacks (ExecPlan 0049).
    Copy-Item -LiteralPath (Join-Path $Repository 'tools/setup-local.ps1') -Destination (Join-Path $seed 'tools/setup-local.ps1')
    $module = [IO.File]::ReadAllText((Join-Path $Repository 'tools/lib/Pilot.psm1'))
    if (-not $IsWindows -and $PSVersionTable.PSEdition -eq 'Core') {
        # Off Windows there is no Windows account to restrict the backup folder to: the scratch copy skips that
        # one step, as the M7 model's runs did (docs/archive/COMMANDS.md). The update file itself is copied unchanged.
        $marker = "function Protect-Path {`n    param([Parameter(Mandatory = `$true)][string]`$Path)`n"
        if (-not $module.Replace("`r`n", "`n").Contains($marker)) { throw 'Protect-Path was not found in Pilot.psm1.' }
        $module = $module.Replace("`r`n", "`n").Replace($marker, $marker + "    return`n")
    }
    [IO.File]::WriteAllText((Join-Path $seed 'tools/lib/Pilot.psm1'), $module)
    [IO.File]::WriteAllText((Join-Path $seed 'compose.yaml'), "services: {}`n")
    [IO.File]::WriteAllText((Join-Path $seed 'app.txt'), "release 1`n")
    Invoke-ModelGit $root @('init', '--quiet', 'seed') | Out-Null
    Invoke-ModelGit $seed @('add', '-A') | Out-Null
    Invoke-ModelGit $seed @('commit', '--quiet', '-m', 'start') | Out-Null
    Invoke-ModelGit $seed @('branch', 'fresh') | Out-Null
    Invoke-ModelGit $seed @('checkout', '--quiet', '-b', 'codex/side') | Out-Null
    [IO.File]::WriteAllText((Join-Path $seed 'side.txt'), "side`n")
    Invoke-ModelGit $seed @('add', '-A') | Out-Null
    Invoke-ModelGit $seed @('commit', '--quiet', '-m', 'side work') | Out-Null
    Invoke-ModelGit $seed @('checkout', '--quiet', 'main') | Out-Null
    Invoke-ModelGit $seed @('merge', '--quiet', '--no-ff', 'codex/side', '-m', 'Merge pull request #1 from owner/codex/side', '-m', 'Side work') | Out-Null
    Invoke-ModelGit $seed @('checkout', '--quiet', '-b', 'merged-pr') | Out-Null
    [IO.File]::WriteAllText((Join-Path $seed 'app.txt'), "release 2`n")
    Invoke-ModelGit $seed @('commit', '--quiet', '-am', 'the agents check themselves') | Out-Null
    Invoke-ModelGit $seed @('checkout', '--quiet', 'main') | Out-Null
    Invoke-ModelGit $seed @('merge', '--quiet', '--no-ff', 'merged-pr', '-m', 'Merge pull request #2 from owner/merged-pr', '-m',
        "M8 update 1: hands-off agents`n`nRelease note:`n- The agents check themselves after a change.`n- One switch on the Agents page.`n`nCo-Authored-By: Model <model@example.invalid>") | Out-Null
    Invoke-ModelGit $seed @('checkout', '--quiet', '-b', 'unmerged') | Out-Null
    [IO.File]::WriteAllText((Join-Path $seed 'draft.txt'), "draft`n")
    Invoke-ModelGit $seed @('add', '-A') | Out-Null
    Invoke-ModelGit $seed @('commit', '--quiet', '-m', 'unfinished') | Out-Null
    Invoke-ModelGit $seed @('checkout', '--quiet', 'main') | Out-Null
    Invoke-ModelGit $root @('clone', '--quiet', '--bare', 'seed', 'github.git') | Out-Null
    Invoke-ModelGit $root @('clone', '--quiet', 'github.git', 'folder') | Out-Null
    # The folder stands on codex/side, as the owner's folder stood on another branch on 2026-10-19.
    Invoke-ModelGit $folder @('checkout', '--quiet', '-b', 'codex/side', 'origin/codex/side') | Out-Null
    return @{ root = $root; hub = $hub; folder = $folder; seed = $seed }
}

function Invoke-Update {
    param([hashtable]$Git, [switch]$Relaunched)
    $arguments = @{ Project = $project; Repository = $Git.folder; EnvFile = $envFile; BackupRoot = (Join-Path $Git.root 'backups'); Model = $true }
    if ($Relaunched) { $arguments.Relaunched = $true }
    $global:LASTEXITCODE = 0
    $output = @(& (Join-Path $Git.folder 'tools/update.ps1') @arguments *>&1 | ForEach-Object { "$_" })
    if ($Show) { [Console]::Error.WriteLine("----- exit $LASTEXITCODE`n" + ($output -join "`n")) }
    return @{ code = $LASTEXITCODE; text = ($output -join "`n") }
}

function Get-Records {
    param([hashtable]$Git, [string]$Name)
    return @(Get-ChildItem -LiteralPath (Join-Path $Git.root 'backups') -Recurse -File -Filter $Name -ErrorAction SilentlyContinue |
            ForEach-Object { Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json })
}

$results = [ordered]@{}
$failed = @()
function Expect {
    param([string]$Scenario, [string]$What, [bool]$Holds)
    if (-not $results.Contains($Scenario)) { $results[$Scenario] = [ordered]@{} }
    $results[$Scenario][$What] = $Holds
    if (-not $Holds) { $script:failed += "${Scenario}: $What" }
}

# The calls in the model's log ('compose <command> <arguments>' for Compose, the docker arguments otherwise): the
# index of each call that matches, in order. Callers wrap it in @().
function Get-At {
    param([string]$Pattern)
    $calls = $global:Model.calls
    for ($i = 0; $i -lt $calls.Count; $i++) { if ($calls[$i] -match $Pattern) { $i } }
}

function Get-FirstAt {
    # The index of the first call that matches; an error when none does.
    param([string]$Pattern)
    $found = @(Get-At $Pattern)
    if (-not $found.Count) { throw "No call matches $Pattern" }
    return $found[0]
}

function Get-LastAt {
    # The index of the last call that matches; an error when none does.
    param([string]$Pattern)
    $found = @(Get-At $Pattern)
    if (-not $found.Count) { throw "No call matches $Pattern" }
    return $found[-1]
}


# The migration, as the update runs it in the migrate service.
$migrateCall = '^compose run --rm --no-deps migrate python -m app\.migrate '
# What no run of the update file of ExecPlan 0061 says or does: the paths it removed.
$removedWords = 'futures account is flat|Bitcoin futures account|empty database|clean start|Retired |retired container|sign-in-claude|Logins kept'

$scenarios = [ordered]@{
    update = {
        # The owner's PC since 2026-11-12: the spot app at 0041; the new api reads only the release's head, so the
        # migration comes first, with the writers stopped before it.
        $git = New-ModelGit 'update'
        Reset-Model
        $m = $global:Model
        # Five older backups, as earlier updates left them, and the futures app's clean start's copy (ExecPlan 0039
        # section 5.1), older than all of them: the owner's to delete, never the tidy step's.
        $oldDumps = @()
        foreach ($day in 1..5) {
            $folder = Join-Path $git.root "backups/update-2026100${day}T120000Z"
            New-Item -ItemType Directory -Path $folder -Force | Out-Null
            $dump = Join-Path $folder 'asl.dump'
            [IO.File]::WriteAllText($dump, 'old dump'); [IO.File]::WriteAllText("$dump.sha256", 'hash')
            (Get-Item -LiteralPath $dump).LastWriteTimeUtc = [DateTime]::new(2026, 10, $day, 12, 0, 0, [DateTimeKind]::Utc)
            $oldDumps += $dump
        }
        $copies = Join-Path $git.root 'backups/before-futures'
        New-Item -ItemType Directory -Path $copies -Force | Out-Null
        $copy = Join-Path $copies 'asl.dump'
        [IO.File]::WriteAllText($copy, 'before the futures app'); [IO.File]::WriteAllText("$copy.sha256", 'hash')
        (Get-Item -LiteralPath $copy).LastWriteTimeUtc = [DateTime]::new(2026, 9, 1, 12, 0, 0, [DateTimeKind]::Utc)
        $run = Invoke-Update $git
        $head = "$(Invoke-ModelGit $git.folder @('rev-parse', 'HEAD'))".Trim()
        $remoteMain = "$(Invoke-ModelGit $git.folder @('rev-parse', 'origin/main'))".Trim()
        $records = @(Get-Records $git 'update.json')
        Expect 'update' 'exit 0 and DONE' ($run.code -eq 0 -and $run.text -cmatch 'DONE: the app runs \S+\. Nothing else is needed')
        Expect 'update' 'the folder on main at origin/main' ("$(Invoke-ModelGit $git.folder @('rev-parse', '--abbrev-ref', 'HEAD'))".Trim() -eq 'main' -and $head -eq $remoteMain)
        Expect 'update' 'the missing secret files created first, as tools/setup-local.ps1 creates them' (
            $run.text -match 'Created 5 missing secret file\(s\) under secrets/' -and
            @(Get-ChildItem -LiteralPath (Join-Path $git.folder 'secrets') -File).Count -eq 5)
        Expect 'update' 'the preflight says the schema and the services, nothing of the futures app' ($run.text -match "Schema $S9; 5 service\(s\) with a container\." -and
            $records.Count -eq 1 -and $records[0].steps.preflight.schema -eq $S9 -and
            $null -eq $records[0].steps.preflight.futures_account -and $null -eq $records[0].steps.preflight.clean_start)
        Expect 'update' 'migrated to the head once' ($m.schema -eq $S10 -and $m.migrations -eq 1 -and $run.text -match "Migrated $S9 -> $S10")
        $migration = Get-FirstAt $migrateCall
        Expect 'update' 'the migration, by app.migrate and the head alone, before the first recreation' (
            $migration -lt (Get-FirstAt '^compose up ') -and $m.calls[$migration] -ceq "compose run --rm --no-deps migrate python -m app.migrate $S10")
        Expect 'update' 'the two workers stopped by Compose before the migration, nothing after' (
            (@($m.stoppedBy) -join ',') -eq 'execution-worker,market-worker' -and
            -not (@(Get-At '^compose stop ') | Where-Object { $_ -gt $migration }))
        Expect 'update' 'only the old api and web ran while it migrated' ((@($m.runningAtMigration) -join ',') -eq 'api,web')
        Expect 'update' 'the stop said and recorded' (
            $run.text -match 'Stopped for the migration: execution-worker, market-worker' -and
            (@($records[0].steps.migration_stop.stopped) -join ',') -eq 'execution-worker,market-worker' -and
            $null -eq $records[0].steps.migration_stop.started_again -and $null -eq $records[0].steps.migration_stop.retired_stopped)
        $expected = @('api', 'web', 'market-worker', 'execution-worker')
        Expect 'update' 'every running service recreated once, in order, each running its new image' ((@($m.recreated) -join ',') -eq ($expected -join ',') -and
            -not ($expected | Where-Object { $m.containers[$_][0].status -ne 'running' -or $m.containers[$_][0].image -ne $m.new[$_] }) -and
            $run.text -match 'execution-worker recreated on its new image \(it holds the execution lease')
        Expect 'update' 'nothing started again by id, postgres never recreated or built' ($m.startedBy.Count -eq 0 -and
            -not ($m.calls | Where-Object { $_ -match '^compose (up|build) .*\bpostgres\b' }))
        Expect 'update' 'no container or network stopped or removed by id; nothing removed or forced but images' (
            -not ($m.calls | Where-Object { $_ -match '^(container|network) ' -or ($_ -match '^image (rm|stop|kill)' -and $_ -match ' (-f|--force)( |$)') -or
                    $_ -match 'prune|--remove-orphans|^volume |^(rm|kill|stop) |^compose down' }) -and
            -not ($runningServices | Where-Object { -not $m.containers.Contains($_) }))
        Expect 'update' 'none of the removed paths said or recorded' ($run.text -cnotmatch $removedWords -and
            $null -eq $records[0].steps.retired -and $null -eq $records[0].steps.clean_start -and $null -eq $records[0].steps.claude_starter)
        Expect 'update' 'rollback tags name the old images' (-not ($expected | Where-Object { $m.names["$project-$($_):before-update"] -ne $m.old[$_] }))
        Expect 'update' 'a COMPLETE record with the commit and backup' ($records.Count -eq 1 -and $records[0].status -eq 'COMPLETE' -and
            $records[0].source.commit -eq $head -and $records[0].steps.backup.sha256 -match '^[0-9a-f]{64}$')
        Expect 'update' 'the check said in its words' ($run.text -match "Schema $S10, api ready, reconciliation OK, pages answer\.")
        Expect 'update' 'the spot app read out' (
            $run.text -match 'Bitcoin spot feed: CONNECTED, newest write at 14:02:11 UTC, BTCUSDT TRADING, usable, clock checked; 3009 daily candles \(2017-08-17 to 2026-11-11\); 2880 one-minute candles' -and
            $run.text -match 'Spot account: 9959\.88 USDT and 0 BTC; run #1 RUNNING; 0 trade\(s\)' -and
            $run.text -match "The rule's newest reading: 2026-11-12 CASH \(target 0% in Bitcoin\): NO_CHANGE" -and
            $run.text -match 'Backtest: computed at 2026-11-12 14:03 UTC on 3009 days \(2017-08-17 to 2026-11-11\); its page is Backtest' -and
            $run.text -match 'Archive: 131 table\(s\) of the futures app kept read-only; 1 futures run\(s\) retired by the switch' -and
            $records[0].steps.read_out.account.run.seq -eq 1 -and $records[0].steps.read_out.feed.days -eq 3009 -and
            $records[0].steps.read_out.archive.tables -eq 131)
        Expect 'update' 'the release note printed' ($run.text -match 'The agents check themselves after a change' -and $run.text -match 'M8 update 1: hands-off agents' -and
            $run.text -notmatch 'Co-Authored-By')
        $remote = @(Invoke-ModelGit $git.hub @('branch', '--format=%(refname:short)'))
        Expect 'update' 'merged branches deleted on GitHub' ('merged-pr' -notin $remote -and 'codex/side' -notin $remote)
        Expect 'update' 'main, a fresh branch and unmerged work kept' ('main' -in $remote -and 'fresh' -in $remote -and 'unmerged' -in $remote)
        Expect 'update' 'old backups pruned to the newest three, with their hashes' (
            -not (@($oldDumps | Select-Object -First 3) | Where-Object { (Test-Path -LiteralPath $_) -or (Test-Path -LiteralPath "$_.sha256") }) -and
            -not (@($oldDumps | Select-Object -Skip 3) | Where-Object { -not (Test-Path -LiteralPath $_) }) -and
            (Test-Path -LiteralPath $records[0].steps.backup.path))
        Expect 'update' 'the before-futures copy kept, older than every backup' ((Test-Path -LiteralPath $copy) -and (Test-Path -LiteralPath "$copy.sha256") -and
            -not (@($records[0].steps.leftovers.dumps_deleted) | Where-Object { $_ -like "*before-futures*" }))
        $removed = @($m.removedImages)
        Expect 'update' 'unused images of this app removed by exact name, current and foreign ones kept' (
            $removed -contains "$project-api:pre-m7" -and $removed -contains "$project-agent-worker:latest" -and $removed -contains $m.dangling[0] -and
            $removed -notcontains 'other-app-web:latest' -and $removed -notcontains "$project-web-tools:latest" -and
            -not ($removed | Where-Object { $_ -match "^$([regex]::Escape($project))-(.+):(latest|before-update)$" -and $serviceFlags.Contains($Matches[1]) }) -and
            -not ($m.calls | Where-Object { $_ -match '^image rm (.+ )?(-f|--force)( |$)' -or $_ -match 'prune' }))
        Expect 'update' 'an image in use is reported, not forced' ($run.text -match ('Kept \(in use or refused\): ' + [regex]::Escape("$project-web-tools:latest")))
        $local = @(Invoke-ModelGit $git.folder @('branch', '--format=%(refname:short)'))
        Expect 'update' 'the merged local branch deleted' ('codex/side' -notin $local -and 'main' -in $local)
        # A second run with nothing new: no service is recreated or stopped, and the record says the same commit.
        $m.recreated.Clear()
        $calls = $m.calls.Count
        $again = Invoke-Update $git
        $later = @($m.calls | Select-Object -Skip $calls)
        Expect 'update' 'a second run recreates, stops and migrates nothing' ($again.code -eq 0 -and $m.recreated.Count -eq 0 -and $again.text -match 'nothing new' -and
            $again.text -match "No migration: the schema is already $S10" -and
            -not ($later | Where-Object { $_ -match '^compose stop ' -or $_ -match $migrateCall }) -and $m.migrations -eq 1)
    }
    dirty = {
        $git = New-ModelGit 'dirty'
        Reset-Model
        [IO.File]::WriteAllText((Join-Path $git.folder 'app.txt'), "edited by hand`n")
        $before = "$(Invoke-ModelGit $git.folder @('rev-parse', 'HEAD'))".Trim()
        $run = Invoke-Update $git
        Expect 'dirty' 'exit 1, the file named' ($run.code -eq 1 -and $run.text -match 'uncommitted changes in 1 tracked file' -and $run.text -match 'app\.txt')
        Expect 'dirty' 'no docker call' ($global:Model.calls.Count -eq 0)
        Expect 'dirty' 'the folder unchanged' ("$(Invoke-ModelGit $git.folder @('rev-parse', '--abbrev-ref', 'HEAD'))".Trim() -eq 'codex/side' -and
            "$(Invoke-ModelGit $git.folder @('rev-parse', 'HEAD'))".Trim() -eq $before)
        Expect 'dirty' 'no success claimed' ($run.text -cnotmatch 'DONE:' -and @(Get-Records $git 'update-failed.json').Count -eq 1)
    }
    early = {
        # A run that stops before it sets rollback tags leaves them alone: the next run tags what runs then.
        $git = New-ModelGit 'early'
        Reset-Model
        $m = $global:Model
        $first = Invoke-Update $git
        $installed = $m.new.Clone()
        [IO.File]::WriteAllText((Join-Path $git.folder 'app.txt'), "edited by hand`n")
        $stopped = Invoke-Update $git
        Invoke-ModelGit $git.folder @('checkout', '--quiet', '--', 'app.txt') | Out-Null
        foreach ($service in @($m.new.Keys)) { $m.new[$service] = New-ModelId }
        $next = Invoke-Update $git
        Expect 'early' 'the tags move to what ran after a stop before them' ($first.code -eq 0 -and $stopped.code -eq 1 -and $next.code -eq 0 -and
            $m.names["$project-api:before-update"] -eq $installed['api'] -and $next.text -notmatch 'rollback tags are kept')
    }
    ahead = {
        $git = New-ModelGit 'ahead'
        Reset-Model
        Invoke-ModelGit $git.folder @('checkout', '--quiet', 'main') | Out-Null
        [IO.File]::WriteAllText((Join-Path $git.folder 'local.txt'), "local`n")
        Invoke-ModelGit $git.folder @('add', '-A') | Out-Null
        Invoke-ModelGit $git.folder @('commit', '--quiet', '-m', 'a local commit') | Out-Null
        $run = Invoke-Update $git
        Expect 'ahead' 'exit 1 before any docker call' ($run.code -eq 1 -and $run.text -match "holds 1 commit\(s\) that GitHub's main lacks" -and $global:Model.calls.Count -eq 0)
    }
    migration = {
        # The migration does not apply (it rolls back whole): the workers stopped for it start again in their containers,
        # by their ids, so that the app runs as before; the next run completes.
        $git = New-ModelGit 'migration'
        Reset-Model
        $m = $global:Model
        $m.failMigration = $true
        $run = Invoke-Update $git
        $stoppedForIt = @('execution-worker', 'market-worker')
        Expect 'migration' 'exit 1 at the migration after three tries, never DONE' ($run.code -eq 1 -and $run.text -match "STOPPED at 'migrate'" -and
            $run.text -match "The migration to $S10 did not apply" -and $m.migrations -eq 3 -and $run.text -cnotmatch 'DONE:')
        Expect 'migration' 'nothing replaced, and said so' ($m.recreated.Count -eq 0 -and $run.text -match 'No running service was replaced')
        Expect 'migration' 'each worker stopped for it started again by its id, in the order they stopped' (
            (@($m.startedBy) -join ',') -eq ($stoppedForIt -join ',') -and
            @(Get-At '^start [0-9a-f]{64}$').Count -eq 2 -and -not ($m.calls | Where-Object { $_ -match '^compose start ' }) -and
            (Get-FirstAt '^start ') -gt (Get-LastAt $migrateCall))
        Expect 'migration' 'each on its old image and running, as before' (
            -not ($stoppedForIt | Where-Object { $m.containers[$_][0].status -ne 'running' -or $m.containers[$_][0].image -ne $m.old[$_] }) -and
            $run.text -match 'The containers stopped for the migration were started again, so the app runs as before' -and
            $run.text -notmatch 'not started again')
        Expect 'migration' 'the schema as it was' ($m.schema -eq $S9 -and $run.text -match "Schema now: $S9")
        $records = @(Get-Records $git 'update-failed.json')
        Expect 'migration' 'a FAILED record beside the backup says what was stopped and started again' ($records.Count -eq 1 -and $records[0].status -eq 'FAILED' -and
            $records[0].stage -eq 'migrate' -and $records[0].steps.backup.sha256 -match '^[0-9a-f]{64}$' -and
            (@($records[0].steps.migration_stop.started_again) -join ',') -eq ($stoppedForIt -join ','))
        # Fixed forward: the next run keeps the first run's rollback tags and finishes the rest.
        $m.failMigration = $false
        # The next run takes its backup in a stamp folder of its own (stamps are to the second).
        [Threading.Thread]::Sleep(1100)  # Start-Sleep is the model clock here
        # Three backups that sort newer than both runs' own: the pruning reaches the stopped run's backup, which stays.
        foreach ($minute in 1..3) {
            $folder = Join-Path $git.root "backups/later-$minute"
            New-Item -ItemType Directory -Path $folder -Force | Out-Null
            [IO.File]::WriteAllText((Join-Path $folder 'asl.dump'), 'later dump')
            (Get-Item -LiteralPath (Join-Path $folder 'asl.dump')).LastWriteTimeUtc = [DateTime]::UtcNow.AddHours($minute)
        }
        $run2 = Invoke-Update $git
        Expect 'migration' 'the next run completes and keeps the old tags, nothing left stopped' ($run2.code -eq 0 -and $m.schema -eq $S10 -and
            $m.names["$project-api:before-update"] -eq $m.old['api'] -and $run2.text -match 'rollback tags are kept' -and
            $run2.text -notmatch 'Left stopped by the stopped update')
        $completed = @(Get-Records $git 'update.json')
        Expect 'migration' 'the stopped run''s backup is kept by the tidy step' ($completed.Count -eq 1 -and
            $completed[0].steps.backup.path -ne $records[0].steps.backup.path -and (Test-Path -LiteralPath $records[0].steps.backup.path))
    }
    undofail = {
        # The migration does not apply and Docker will not start the market worker's container again: the stop says so,
        # and the record names what was started before it. The next run starts the market worker on its new image.
        $git = New-ModelGit 'undofail'
        Reset-Model
        $m = $global:Model
        $m.failMigration = $true
        $m.refuseStart = 'market-worker'
        $run = Invoke-Update $git
        $records = @(Get-Records $git 'update-failed.json')
        Expect 'undofail' 'exit 1, the failed start named, never DONE' ($run.code -eq 1 -and $run.text -match "STOPPED at 'migrate'" -and
            $run.text -match 'Starting the containers stopped for the migration again failed too \(docker start of the container of market-worker failed' -and
            $run.text -match 'started again before that: execution-worker(\n|$)' -and $run.text -cnotmatch 'DONE:')
        Expect 'undofail' 'the record says what was started again' ($records.Count -eq 1 -and
            (@($records[0].steps.migration_stop.started_again) -join ',') -eq 'execution-worker' -and
            $m.containers['market-worker'][0].status -eq 'exited')
        $m.failMigration = $false
        $m.refuseStart = ''
        [Threading.Thread]::Sleep(1100)
        $next = Invoke-Update $git
        $done = @(Get-Records $git 'update.json')
        Expect 'undofail' 'the next run names the market worker as left stopped and starts it on its new image' ($next.code -eq 0 -and $m.schema -eq $S10 -and
            $next.text -match 'Left stopped by the stopped update, started again on their new images by this one: market-worker' -and
            (@($m.recreated) -join ',') -eq 'api,web,market-worker,execution-worker' -and
            -not (@('market-worker', 'execution-worker') | Where-Object { $m.containers[$_][0].status -ne 'running' -or $m.containers[$_][0].image -ne $m.new[$_] }) -and
            $done.Count -eq 1 -and (@($done[0].steps.preflight.left_stopped) -join ',') -eq 'market-worker' -and
            (@($done[0].steps.migration_stop.stopped) -join ',') -eq 'execution-worker')
    }
    expand = {
        # A release whose new api reads the schema that is there: the api and then the web first, nothing stopped, then
        # the migration and the workers.
        $git = New-ModelGit 'expand'
        Reset-Model
        $m = $global:Model
        $m.accepts = "$S9 $S10"
        $run = Invoke-Update $git
        $migration = Get-FirstAt $migrateCall
        Expect 'expand' 'exit 0, the api and then the web before the migration' ($run.code -eq 0 -and (@($m.recreated) -join ',') -eq 'api,web,market-worker,execution-worker' -and
            @(@(Get-At '^compose up ') | Where-Object { $_ -lt $migration }).Count -eq 2 -and $run.text -match 'The new api reads the schema as it is: api and web first')
        Expect 'expand' 'nothing stopped for the migration' ($m.stoppedBy.Count -eq 0 -and -not (@(Get-At '^container stop ') | Where-Object { $_ -lt $migration }) -and
            $run.text -notmatch 'Stopped for the migration' -and $null -eq @(Get-Records $git 'update.json')[0].steps.migration_stop)
    }
    halfway = {
        # The migration applied, then the market worker's new container exits: the run stops with the execution worker
        # still stopped for the migration, and says so. The next run starts both on their new images, with no migration.
        $git = New-ModelGit 'halfway'
        Reset-Model
        $m = $global:Model
        $m.crashOnUp = 'market-worker'
        $run = Invoke-Update $git
        Expect 'halfway' 'exit 1 at the market worker after the migration, the execution worker named as not started again' (
            $run.code -eq 1 -and $run.text -match "STOPPED at 'recreate market-worker'" -and $m.schema -eq $S10 -and
            $run.text -match 'Service market-worker is exited after it was recreated' -and
            $run.text -match 'Stopped by the update and not started again: execution-worker\. The next update starts them on its new images' -and
            $m.containers['execution-worker'][0].status -eq 'exited' -and $m.containers['execution-worker'][0].image -eq $m.old['execution-worker'] -and
            $run.text -cnotmatch 'DONE:')
        $m.crashOnUp = ''
        [Threading.Thread]::Sleep(1100)
        $calls = $m.calls.Count
        $m.recreated.Clear()
        $next = Invoke-Update $git
        $records = @(Get-Records $git 'update.json')
        Expect 'halfway' 'the next run starts both on their new images, with no migration and no stop' (
            $next.code -eq 0 -and $next.text -match 'Nothing else is needed' -and (@($m.recreated) -join ',') -eq 'market-worker,execution-worker' -and
            -not (@('market-worker', 'execution-worker') | Where-Object { $m.containers[$_][0].status -ne 'running' -or $m.containers[$_][0].image -ne $m.new[$_] }) -and
            -not (@($m.calls | Select-Object -Skip $calls) | Where-Object { $_ -match '^compose stop ' -or $_ -match $migrateCall }) -and
            $next.text -match 'Left stopped by the stopped update, started again on their new images by this one' -and
            $records.Count -eq 1 -and (@($records[0].steps.preflight.left_stopped | Sort-Object) -join ',') -eq 'execution-worker,market-worker')
    }
    readings = {
        # The read-out as the rule trades, refuses, and waits for its day's candle, and as the feed has lost its clock.
        $git = New-ModelGit 'readings'
        Reset-Model
        $m = $global:Model
        $m.account = '{"funded": true, "cash": "9348.12", "btc": "0.0061", "run": {"seq": 1, "state": "RUNNING", "causes": []}, "reading": {"day": "2026-11-13", "result": "LONG", "action": "BUY", "outcome": "FILLED", "target": "0.061", "codes": []}, "fills": 1, "backtest": {"computed": "2026-11-13 00:20", "days": 3010, "first_day": "2017-08-17", "last_day": "2026-11-12"}, "funding": "POSTED"}'
        $run = Invoke-Update $git
        Expect 'readings' 'a buy read out' ($run.code -eq 0 -and $run.text -match 'Spot account: 9348\.12 USDT and 0\.0061 BTC; run #1 RUNNING; 1 trade\(s\)' -and
            $run.text -match "The rule's newest reading: 2026-11-13 LONG \(target 6\.1% in Bitcoin\): FILLED \(BUY\)")
        $m.account = '{"funded": true, "cash": "9348.12", "btc": "0.0061", "run": {"seq": 2, "state": "PAUSED", "causes": ["OWNER", "DAILY_LOSS"]}, "reading": {"day": "2026-11-14", "result": "LONG", "action": "BUY", "outcome": "REFUSED", "target": "0.05", "codes": ["RUN_NOT_RUNNING"]}, "fills": 1, "backtest": null, "funding": "POSTED"}'
        $again = Invoke-Update $git
        Expect 'readings' 'a paused run and a refusal read out with their causes and codes' ($again.code -eq 0 -and
            $again.text -match 'run #2 PAUSED \(OWNER, DAILY_LOSS\); 1 trade\(s\)' -and
            $again.text -match "The rule's newest reading: 2026-11-14 LONG \(target 5% in Bitcoin\): REFUSED \(BUY\): RUN_NOT_RUNNING" -and
            $again.text -match 'Backtest: not computed yet')
        $m.account = '{"funded": true, "cash": "9348.12", "btc": "0.0061", "run": {"seq": 2, "state": "RUNNING", "causes": []}, "reading": {"day": "2026-11-15", "result": "WARMUP", "action": null, "outcome": "NOT_READABLE", "target": null, "codes": []}, "fills": 1, "backtest": null, "funding": "POSTED"}'
        $m.feed = '{"status": "UNAVAILABLE", "reason": "CLOCK_UNVERIFIED", "written": "00:31:07", "instrument": "TRADING, usable", "clock": false, "history": true, "days": 3011, "first_day": "2017-08-17", "last_day": "2026-11-13", "candles": 4320}'
        $third = Invoke-Update $git
        Expect 'readings' 'a day not readable yet and a feed without its clock read out' ($third.code -eq 0 -and
            $third.text -match "The rule's newest reading: 2026-11-15 not readable yet; the engine tries again every 15 minutes" -and
            $third.text -match 'Bitcoin spot feed: UNAVAILABLE \(CLOCK_UNVERIFIED\), newest write at 00:31:07 UTC, BTCUSDT TRADING, usable, clock not checked yet; 3011 daily candles \(2017-08-17 to 2026-11-13\); 4320 one-minute candles')
    }
    stoppedweb = {
        # The owner's PC after the first try of ExecPlan 0042 on 2026-10-25 (the update file of 416cef8): it replaced the
        # web before the api, and the new web's health check failed against the old api, so the run stopped at
        # 'recreate web' before the migration. The web runs its new image; every other service its old one; the account
        # not funded. This run replaces the api first, then finds the web on its built image, migrates, and completes.
        $git = New-ModelGit 'stoppedweb'
        Reset-Model
        $m = $global:Model
        $m.accepts = "$S9 $S10"
        $m.account = $unfundedRead
        $m.accountAfterApi = $fundedRead
        $m.containers['web'] = @(New-ModelContainer 'web' $m.new['web'] $m.hashes['web'])
        $tags = [ordered]@{}
        foreach ($service in @('api', 'web', 'market-worker', 'execution-worker')) {
            $m.names["$project-$($service):before-update"] = $m.old[$service]
            $tags[$service] = [ordered]@{ tag = "$project-$($service):before-update"; image = $m.old[$service]; moved = $true }
        }
        $first = Join-Path $git.root 'backups/update-20261025T140852Z'
        New-Item -ItemType Directory -Path $first -Force | Out-Null
        [IO.File]::WriteAllText((Join-Path $first 'asl_model.dump'), 'first try dump')
        $old = [ordered]@{ started_utc = '2026-10-25T14:08:45.4800000Z'; project = $project; status = 'FAILED'; model = $false
            steps = [ordered]@{
                preflight = [ordered]@{ schema = $S9; clean_start = $false; left_stopped = @() }
                backup = [ordered]@{ path = (Join-Path $first 'asl_model.dump'); sha256 = 'hash'; bytes = 14 }
                rollback_tags = $tags
                migrate = [ordered]@{ before = $S9; head = $S10; api_accepts_before = $true }
                recreated = [ordered]@{} }
            stage = 'recreate web'; services_replaced = @('web')
            message = "docker compose up -d --no-deps --no-build --force-recreate --wait web failed (1): container $project-web-1 is unhealthy" }
        $old | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $first 'update-failed.json') -Encoding UTF8
        $run = Invoke-Update $git
        $records = @(Get-Records $git 'update.json')
        Expect 'stoppedweb' 'exit 0 and DONE, the account funded by the app' ($run.code -eq 0 -and
            $run.text -match 'Nothing else is needed' -and $run.text -match 'Spot account: 10000\.00 USDT and 0 BTC; run #1 RUNNING; 0 trade\(s\)')
        Expect 'stoppedweb' 'the api replaced first, before the migration; the web left on the image the stopped run gave it' (
            $m.recreated.Count -ge 1 -and $m.recreated[0] -eq 'api' -and $m.recreated -notcontains 'web' -and
            @(@(Get-At '^compose up .* api$') | Where-Object { $_ -lt $m.migratedAt }).Count -eq 1 -and
            $m.containers['web'][0].image -eq $m.new['web'] -and $run.text -match 'Already on their built images: web')
        Expect 'stoppedweb' 'migrated, every service on its new image' ($m.schema -eq $S10 -and
            -not ($tags.Keys | Where-Object { $m.containers[$_][0].image -ne $m.new[$_] }))
        Expect 'stoppedweb' 'the rollback tags kept on the release before the stopped run' (
            -not ($tags.Keys | Where-Object { $m.names["$project-$($_):before-update"] -ne $m.old[$_] }) -and
            $run.text -match 'The last update stopped early: its rollback tags are kept' -and $records.Count -eq 1 -and
            $records[0].status -eq 'COMPLETE')
    }
    settings = {
        # The release's schema already there; a release that changes only a service's settings (compose.yaml or the env
        # file), not its image. An account not funded yet and a feed that has written nothing are read out as such.
        $git = New-ModelGit 'settings'
        Reset-Model
        $m = $global:Model
        $m.schema = $S10
        $m.new['market-worker'] = $m.old['market-worker']
        $m.hashes['market-worker'] = New-ModelHash
        $m.account = $unfundedRead
        $m.feed = '{"status": "STARTING", "reason": null, "written": null, "instrument": null, "clock": false, "history": false, "days": 0, "first_day": null, "last_day": null, "candles": 0}'
        $run = Invoke-Update $git
        Expect 'settings' 'an account not funded and a feed that has written nothing read out' (
            $run.text -match 'Spot account: not funded yet \(the api has not added its starting contribution\)' -and
            $run.text -match 'Bitcoin spot feed: STARTING, nothing written yet, BTCUSDT not checked yet, clock not checked yet; no daily candle yet, the daily history still filling; 0 one-minute candles' -and
            $run.text -match "The rule's newest reading: none yet" -and $run.text -match 'Backtest: not computed yet')
        Expect 'settings' 'exit 0 and the service recreated with its new settings, no migration and nothing stopped' ($run.code -eq 0 -and 'market-worker' -in $m.recreated -and
            $run.text -match 'market-worker recreated with its new settings' -and $m.containers['market-worker'][0].hash -eq $m.hashes['market-worker'] -and
            $m.migrations -eq 0 -and $m.stoppedBy.Count -eq 0 -and $run.text -match "No migration: the schema is already $S10")
        $m.recreated.Clear()
        $again = Invoke-Update $git
        Expect 'settings' 'a second run recreates nothing' ($again.code -eq 0 -and $m.recreated.Count -eq 0)
    }
    quiet = {
        # ExecPlan 0061: the quiet window of both tools, from their own text (Test-QuietTime). A step begins at or after
        # 00:10 UTC and ends, with the minutes it declares, by 23:55 UTC.
        foreach ($file in @('tools/update.ps1', 'tools/docker-cleanup.ps1')) {
            $text = [IO.File]::ReadAllText((Join-Path $Repository $file)).Replace("`r`n", "`n")
            $found = [regex]::Match($text, '(?ms)^function Test-QuietTime \{.*?^\}')
            if (-not $found.Success) { Expect 'quiet' "$file has Test-QuietTime" $false; continue }
            . ([scriptblock]::Create($found.Value))
            $day = [DateTime]::new(2026, 11, 13, 0, 0, 0, [DateTimeKind]::Utc)
            $cases = @(
                @(0, 0, 2, $false), @(0, 5, 2, $false), @(0, 9.98, 2, $false), @(0, 10, 2, $true), @(12, 0, 15, $true),
                @(23, 53, 2, $true), @(23, 53.02, 2, $false), @(23, 55, 0, $true), @(23, 56, 0, $false), @(23, 40, 15, $true),
                @(23, 41, 15, $false), @(22, 55, 60, $true), @(22, 56, 60, $false), @(0, 10, 60, $true))
            $wrong = @()
            foreach ($case in $cases) {
                $at = $day.AddHours($case[0]).AddMinutes($case[1])
                if ((Test-QuietTime $at $case[2]) -ne $case[3]) { $wrong += "$($at.ToString('HH:mm:ss')) +$($case[2]) min" }
            }
            Expect 'quiet' "$file waits from 23:55 to 00:10 UTC with the step's room" ($wrong.Count -eq 0)
            if ($wrong.Count) { [Console]::Error.WriteLine("$file wrong at: $($wrong -join '; ')") }
        }
    }
    pages = {
        $git = New-ModelGit 'pages'
        Reset-Model
        $global:Model.pages = '500'
        $run = Invoke-Update $git
        Expect 'pages' 'exit 1, the pages named' ($run.code -eq 1 -and $run.text -match 'not answering' -and $run.text -match '/backtest' -and
            $run.text -cnotmatch 'DONE:')
    }
    relaunch = {
        # A copy of the update file that differs from main's, started again by an older run: it stops at once.
        $git = New-ModelGit 'relaunch'
        Reset-Model
        $copy = Join-Path $git.root 'old-update.ps1'
        Copy-Item -LiteralPath (Join-Path $Repository 'tools/update.ps1') -Destination $copy
        Add-Content -LiteralPath $copy -Value '# an older copy'
        $global:LASTEXITCODE = 0
        $output = @(& $copy -Project $project -Repository $git.folder -EnvFile $envFile -BackupRoot (Join-Path $git.root 'backups') -Model -Relaunched *>&1 |
                ForEach-Object { "$_" }) -join "`n"
        Expect 'relaunch' 'exit 1 before any docker call' ($LASTEXITCODE -eq 1 -and $output -match 'not the one running' -and $global:Model.calls.Count -eq 0)
    }
}

foreach ($name in $scenarios.Keys) {
    if ($Only -and $name -ne $Only) { continue }
    try { & $scenarios[$name] } catch { Expect $name "ran without an error ($($_.Exception.Message))" $false }
}
Remove-Item -LiteralPath $work -Recurse -Force
$report = [ordered]@{ results = $results; failed = $failed }
Write-Output ($report | ConvertTo-Json -Depth 5 -Compress)
if ($failed.Count) { exit 1 }
exit 0
