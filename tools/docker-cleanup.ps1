param(
    [ValidatePattern('^[a-z0-9][a-z0-9_-]{1,62}$')]
    [string]$Project = 'adaptive-spot-lab',
    # The owner's app folder (it holds compose.yaml and the env file). Default: the nearest folder above this file
    # that holds compose.yaml.
    [string]$Repository = '',
    [string]$EnvFile = '',
    [string]$BackupRoot = '',
    # Docker Desktop's data disk. Default: %LOCALAPPDATA%\Docker\wsl\disk\docker_data.vhdx.
    [string]$Vhdx = '',
    # How many earlier database backups (*.dump under the backup root) stay, besides the one this run takes.
    [ValidateRange(2, 50)]
    [int]$KeepBackups = 3,
    # Lists what a run would do and changes nothing (no administrator prompt, no backup, no Docker stop).
    [switch]$DryRun,
    # Internal: the helper this file starts with administrator rights; it only runs diskpart when told to.
    [switch]$Compactor,
    # Internal: the hidden watchdog (no administrator rights) that starts Docker Desktop again if this window is
    # closed while Docker is stopped.
    [switch]$Watchdog,
    [string]$Signal = '',
    [int]$ParentId = 0
)

# Docker clean-up for the owner's PC (ExecPlan 0034), started by docker-cleanup.cmd. It changes only this app's
# own leftovers, each by its exact name, and never prunes. In this order:
# 1. Checks, read-only: Docker Desktop runs and its CLI answers, the data disk exists, the app runs. Windows then
#    asks once for administrator rights, which only the compaction (diskpart) uses; a No changes nothing.
# 2. Waits by itself while the clock is near the day's reference and reading (23:55 to 00:10 UTC; ExecPlan 0061),
#    with room for the step: 10 minutes for the backup, an hour for the stop of Docker and the compaction.
# 3. A protected backup of the main database, as the update file takes it.
# 4. Removes this app's images that no current service of compose.yaml uses (old test and tool images, old rollback
#    tags such as :pre-m7; never :latest or :before-update of a current service), the untagged images of this app
#    and of its old test stacks (Compose projects <project>-test and asl-m<N>-...), and
#    two leftover volumes of old test runs. Each by exact name or id, never with -f: a volume or an image layer
#    something still uses stays, and the run says so (an image with several tags only loses the tag named).
# 5. Trims the Docker disk's free space (fstrim inside Docker's VM), stops Docker Desktop (and WSL when the disk
#    stays in use), compacts the data disk with diskpart (attach read-only, compact vdisk, detach: Microsoft's
#    compact vdisk reference) and starts Docker Desktop again. The app's containers come back by their restart
#    policy; the run waits for each container that ran before.
# 6. Deletes database backups older than the newest $KeepBackups (the one this run took stays too), and the old PC
#    test-run folders .cache\m2, m3, m3dev, m4, m6 and m7 (their results are recorded in the documents).
# 7. Prints the disk size before and after, and writes a JSON record beside the backups.
# Other projects' containers, images and volumes, and Docker's build cache, are not touched.
# Windows PowerShell 5.1 compatible; ASCII only.
$ErrorActionPreference = 'Stop'

function Say([string]$Text) { Write-Host $Text }

function Invoke-Native {
    # Windows PowerShell 5.1 turns native stderr into error records; keep them as text.
    param([string]$File, [string[]]$Arguments)
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $output = @(& $File @Arguments 2>&1 | ForEach-Object { "$_" }) } finally { $ErrorActionPreference = $saved }
    return $output
}

# ---- The administrator helper: waits for the go, runs diskpart once, reports, exits ------------------------
if ($Compactor) {
    $go = Join-Path $Signal 'go'
    $done = Join-Path $Signal 'done.txt'
    while (-not (Test-Path -LiteralPath $go)) {
        if ($ParentId -and -not (Get-Process -Id $ParentId -ErrorAction SilentlyContinue)) { exit 2 }
        Start-Sleep -Seconds 2
    }
    $script = Join-Path $Signal 'compact.txt'
    $undo = Join-Path $Signal 'detach.txt'
    [IO.File]::WriteAllLines($script, [string[]]@("select vdisk file=`"$Vhdx`"", 'attach vdisk readonly', 'compact vdisk',
        'detach vdisk', 'exit'), (New-Object Text.ASCIIEncoding))
    [IO.File]::WriteAllLines($undo, [string[]]@("select vdisk file=`"$Vhdx`"", 'detach vdisk noerr', 'exit'),
        (New-Object Text.ASCIIEncoding))
    $output = Invoke-Native 'diskpart.exe' @('/s', $script)
    $code = $LASTEXITCODE
    # A failed compact leaves the disk attached: detach it whatever happened.
    Invoke-Native 'diskpart.exe' @('/s', $undo) | Out-Null
    [IO.File]::WriteAllLines($done, [string[]](@("exit=$code") + @($output | Where-Object { "$_".Trim() })), (New-Object Text.ASCIIEncoding))
    exit 0
}

function Test-FileFree([string]$Path) {
    try { $stream = [IO.File]::Open($Path, 'Open', 'Read', 'None'); $stream.Close(); return $true } catch { return $false }
}

function Get-DesktopStatus {
    $lines = Invoke-Native 'docker' @('desktop', 'status')
    if ($LASTEXITCODE -ne 0) { return 'unknown' }
    $text = ($lines -join ' ').ToLowerInvariant()
    if ($text -match 'running') { return 'running' }
    if ($text -match 'stopped') { return 'stopped' }
    return 'unknown'
}

# ---- The watchdog: if the main window ends while Docker is stopped, it starts Docker Desktop once the disk is free --
if ($Watchdog) {
    while ($ParentId -and (Get-Process -Id $ParentId -ErrorAction SilentlyContinue)) { Start-Sleep -Seconds 10 }
    # The main window removes the signal folder when it finished by itself: nothing to do.
    if (-not (Test-Path -LiteralPath $Signal)) { exit 0 }
    if (Test-Path -LiteralPath (Join-Path $Signal 'go')) {
        $deadline = [DateTime]::UtcNow.AddHours(8)
        while (-not (Test-Path -LiteralPath (Join-Path $Signal 'done.txt')) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Seconds 15 }
        $deadline = [DateTime]::UtcNow.AddMinutes(30)
        while (-not (Test-FileFree $Vhdx) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Seconds 10 }
    }
    if ((Get-DesktopStatus) -ne 'running') { Invoke-Native 'docker' @('desktop', 'start', '--timeout', '600') | Out-Null }
    Remove-Item -LiteralPath $Signal -Recurse -Force -ErrorAction SilentlyContinue
    exit 0
}

function Find-Repository {
    $folder = $PSScriptRoot
    while ($folder) {
        if (Test-Path -LiteralPath (Join-Path $folder 'compose.yaml')) { return $folder }
        $parent = Split-Path -Parent $folder
        if (-not $parent -or $parent -eq $folder) { break }
        $folder = $parent
    }
    throw 'The app folder (with compose.yaml) was not found above this file'
}

function Test-QuietTime {
    # Not near the day's reference and reading (ExecPlan 0061): the engine takes the day's reference in the first five
    # minutes after 00:00 UTC and reads the rule from 00:05, so a step begins at or after 00:10 UTC and ends, with the
    # minutes it needs, by 23:55 UTC. The same in tools/update.ps1; tools/m8/update-model.ps1 tests both.
    param([DateTime]$At, [int]$Minutes)
    $minute = $At.TimeOfDay.TotalMinutes
    return ($minute -ge 10 -and $minute + $Minutes -le 1435)
}

function Wait-QuietTime {
    param([int]$Minutes = 10)
    $said = $false
    while ($true) {
        if (Test-QuietTime ([DateTime]::UtcNow) $Minutes) { return }
        if (-not $said) {
            Say "  Waiting for a quiet time: the day's reference and reading run from 00:00 to 00:10 UTC (now $([DateTime]::UtcNow.ToString('HH:mm')) UTC)..."
            $said = $true
        }
        Start-Sleep -Seconds 30
    }
}

function Get-ProjectContainers {
    # Each container of this app with its state; nothing when Docker does not answer.
    $lines = Invoke-Native 'docker' @('ps', '-a', '--filter', "label=com.docker.compose.project=$Project", '--format',
        '{{.Names}}|{{.State}}')
    if ($LASTEXITCODE -ne 0) { return @() }
    $result = @()
    foreach ($line in $lines) {
        $parts = "$line".Split('|')
        if ($parts.Count -eq 2) { $result += [pscustomobject]@{ name = $parts[0]; state = $parts[1] } }
    }
    return $result
}

function Get-RemovalPlan {
    # Current services: every service compose.yaml defines for the update file's profiles.
    $profiles = @('market', 'execution')
    $arguments = @('compose', '-f', (Join-Path $Repository 'compose.yaml'), '-p', $Project, '--env-file', $EnvFile)
    foreach ($name in $profiles) { $arguments += @('--profile', $name) }
    $lines = Invoke-Native 'docker' ($arguments + @('config', '--services'))
    $code = $LASTEXITCODE
    $services = @($lines | ForEach-Object { "$_".Trim() } | Where-Object { $_ -match '^[a-z0-9][a-z0-9_-]*$' })
    if ($code -ne 0 -or $services.Count -lt 4) { throw "Could not read the app's services from compose.yaml" }
    $keep = @{}
    foreach ($service in $services) { $keep["$Project-$service"] = $true }
    $lines = Invoke-Native 'docker' @('image', 'ls', '--format', '{{.Repository}}|{{.Tag}}|{{.ID}}|{{.Size}}')
    if ($LASTEXITCODE -ne 0) { throw "Could not list the images: $($lines -join ' ')" }
    $images = @()
    foreach ($line in $lines) {
        $parts = "$line".Split('|')
        if ($parts.Count -ne 4) { continue }
        $repository = $parts[0]; $tag = $parts[1]
        if (-not $repository.StartsWith("$Project-") -or $tag -eq '<none>') { continue }
        if ($keep.ContainsKey($repository) -and ($tag -eq 'latest' -or $tag -eq 'before-update')) { continue }
        $images += [pscustomobject]@{ name = "${repository}:$tag"; size = $parts[3] }
    }
    # Untagged images built by this app's Compose projects: the app itself, its old test project
    # (<project>-test) and the old isolated test stacks (asl-m<N>-...). Other projects' images never match.
    $lines = Invoke-Native 'docker' @('image', 'ls', '-q', '--no-trunc', '--filter', 'dangling=true')
    if ($LASTEXITCODE -ne 0) { throw "Could not list the untagged images: $($lines -join ' ')" }
    $ids = @($lines | ForEach-Object { "$_".Trim() } | Where-Object { $_ -match '^sha256:[0-9a-f]{64}$' } | Select-Object -Unique)
    $dangling = @()
    if ($ids.Count) {
        # No quotes in the template: Windows PowerShell 5.1 drops them from native arguments. The labels print as
        # map[com.docker.compose.project:<name> ...].
        $lines = Invoke-Native 'docker' (@('image', 'inspect', '--format', '{{.Id}}|{{.Config.Labels}}') + $ids)
        if ($LASTEXITCODE -ne 0) { throw "Could not read the untagged images' labels: $(($lines | Select-Object -Last 2) -join ' ')" }
        foreach ($line in $lines) {
            $parts = "$line".Trim().Split('|', 2)
            if ($parts.Count -ne 2 -or $parts[0] -notmatch '^sha256:[0-9a-f]{64}$') { continue }
            if ($parts[1] -notmatch '(?:^map\[|\s)com\.docker\.compose\.project:([a-z0-9_-]+)(?:\s|\]$)') { continue }
            $owner = $Matches[1]
            if ($owner -eq $Project -or $owner -eq "$Project-test" -or $owner -match '^asl-m[0-9]+-') { $dangling += $parts[0] }
        }
        $dangling = @($dangling | Select-Object -Unique)
    }
    $volumes = @()
    foreach ($name in @("$Project-test_postgres_data", "$Project-pnpm-cache")) {
        Invoke-Native 'docker' @('volume', 'inspect', $name) | Out-Null
        if ($LASTEXITCODE -ne 0) { continue }
        $users = @(Invoke-Native 'docker' @('ps', '-a', '-q', '--filter', "volume=$name") | Where-Object { "$_".Trim() })
        if ($users.Count -eq 0) { $volumes += $name }
    }
    return [pscustomobject]@{ images = $images; dangling = $dangling; volumes = $volumes }
}

function Get-FilePlan {
    $dumps = @()
    if (Test-Path -LiteralPath $BackupRoot) {
        $dumps = @(Get-ChildItem -LiteralPath $BackupRoot -Directory | ForEach-Object {
            Get-ChildItem -LiteralPath $_.FullName -File | Where-Object { $_.Name -like '*.dump' }
        } | Sort-Object LastWriteTimeUtc -Descending)
    }
    $folders = @()
    foreach ($name in @('m2', 'm3', 'm3dev', 'm4', 'm6', 'm7')) {
        $path = Join-Path (Join-Path $Repository '.cache') $name
        if (Test-Path -LiteralPath $path) { $folders += $path }
    }
    return [pscustomobject]@{ old = @($dumps | Select-Object -Skip $KeepBackups); folders = $folders }
}

function Format-Gb([long]$Bytes) { return '{0:N1} GB' -f ($Bytes / 1GB) }

# ---- The clean-up ------------------------------------------------------------------------------------------
if (-not $Repository) { $Repository = Find-Repository }
$Repository = (Resolve-Path -LiteralPath $Repository).Path
if (-not $EnvFile) { $EnvFile = Join-Path $Repository '.env' }
if (-not $BackupRoot) { $BackupRoot = Join-Path $Repository '.cache\deployments' }
if (-not $Vhdx) {
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is not set: pass -Vhdx' }
    $Vhdx = Join-Path $env:LOCALAPPDATA 'Docker\wsl\disk\docker_data.vhdx'
}
foreach ($name in @('DOCKER_HOST', 'DOCKER_CONTEXT')) {
    if ([Environment]::GetEnvironmentVariable($name, 'Process')) { throw "$name is set in this shell: run the clean-up from a shell without it" }
}

Say 'Docker clean-up for Adaptive Spot Lab'
Say '[1/7] Checks (read-only)'
if (-not (Test-Path -LiteralPath $EnvFile)) { throw "The app's env file was not found: $EnvFile" }
if (-not (Test-Path -LiteralPath $Vhdx)) { throw "Docker's data disk was not found at $Vhdx" }
Invoke-Native 'docker' @('version', '--format', '{{.Server.Version}}') | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Docker does not answer: start Docker Desktop and run the clean-up again' }
$desktop = Get-DesktopStatus
if ($desktop -ne 'running') { throw "The Docker Desktop command (docker desktop status) did not report running ($desktop): nothing was changed" }
$before = (Get-Item -LiteralPath $Vhdx).Length
$running = @(Get-ProjectContainers | Where-Object { $_.state -eq 'running' })
if ($running.Count -eq 0) { throw 'None of the app containers runs: start the app first. Nothing was changed' }
$plan = Get-RemovalPlan
$files = Get-FilePlan
$oldBytes = [long](($files.old | Measure-Object -Property Length -Sum).Sum)
$record = [ordered]@{ started_utc = [DateTime]::UtcNow.ToString('o'); project = $Project; dry_run = [bool]$DryRun
    vhdx = $Vhdx; vhdx_bytes_before = $before; running_before = @($running | ForEach-Object { $_.name }) }
Say "  Docker's disk file: $(Format-Gb $before) ($Vhdx)."
Say "  App containers running: $($running.Count)."
Say "  To remove: $($plan.images.Count) old image tag(s), $($plan.dangling.Count) untagged image(s) of this app, $($plan.volumes.Count) leftover volume(s)."
foreach ($image in $plan.images) { Say "    image $($image.name) ($($image.size))" }
foreach ($volume in $plan.volumes) { Say "    volume $volume" }
Say "  Backups: the newest $KeepBackups stay, with the one this run takes; $($files.old.Count) older ($(Format-Gb $oldBytes)) go."
foreach ($dump in $files.old) { Say "    backup $($dump.FullName)" }
foreach ($folder in $files.folders) { Say "    test-run folder $folder" }
if ($DryRun) {
    Say 'Dry run: nothing was changed.'
    exit 0
}

# The one administrator prompt, before anything changes. The helper only waits until the disk is free.
$signal = Join-Path $env:TEMP "asl-docker-cleanup-$([Guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $signal -Force | Out-Null
Say '  Windows now asks for permission to make changes: choose Yes (only the disk compaction uses it).'
$helperArguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Minimized', '-File', "`"$PSCommandPath`"",
    '-Compactor', '-Vhdx', "`"$Vhdx`"", '-Signal', "`"$signal`"", '-ParentId', "$PID")
try {
    $helper = Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList $helperArguments -Verb RunAs -WindowStyle Minimized -PassThru
} catch {
    throw 'Windows did not give administrator rights: nothing was changed'
}

function Test-HelperEnded {
    try { return $helper.HasExited } catch { return -not (Get-Process -Id $helper.Id -ErrorAction SilentlyContinue) }
}

$stopped = $false
$go = $false
$done = Join-Path $signal 'done.txt'
$exitCode = 0
try {
    Say '[2/7] Waiting for a quiet minute'
    Wait-QuietTime -Minutes 10

    Say '[3/7] Protected backup of the database'
    Import-Module (Join-Path $Repository 'tools\lib\Pilot.psm1') -Force
    $compose = New-PilotCompose -Project $Project -EnvFile $EnvFile
    $backup = New-ProtectedBackup -Compose $compose -BackupRoot $BackupRoot -Label 'docker-cleanup' -RequireRoom
    $record.backup = [ordered]@{ path = $backup.path; sha256 = $backup.sha256; bytes = $backup.bytes }
    Say "  Backup $($backup.path) sha256 $($backup.sha256)"

    Say "[4/7] Removing this app's old images and volumes (by exact name)"
    $removed = @(); $left = @()
    foreach ($name in @($plan.images | ForEach-Object { $_.name }) + $plan.dangling) {
        $output = Invoke-Native 'docker' @('image', 'rm', $name)
        if ($LASTEXITCODE -eq 0) { $removed += $name } else { $left += "${name}: $(($output | Select-Object -Last 1))" }
    }
    foreach ($volume in $plan.volumes) {
        $output = Invoke-Native 'docker' @('volume', 'rm', $volume)
        if ($LASTEXITCODE -eq 0) { $removed += "volume $volume" } else { $left += "volume ${volume}: $(($output | Select-Object -Last 1))" }
    }
    $record.removed = $removed
    $record.not_removed = $left
    Say "  Removed $($removed.Count); left $($left.Count) that something still uses or that Docker refused."
    foreach ($line in $left) { Say "    left: $line" }

    Say "[5/7] Shrinking Docker's disk file (the app stops for a while)"
    # fstrim tells the disk which blocks are free, so that the compaction can give them back.
    $hadBusybox = @(Invoke-Native 'docker' @('image', 'ls', '-q', 'busybox:1.37') | Where-Object { "$_".Trim() }).Count -gt 0
    $trim = Invoke-Native 'docker' @('run', '--rm', '--privileged', '--pid=host', 'busybox:1.37', 'nsenter', '-t', '1', '-m', '--',
        'fstrim', '-av')
    $record.fstrim = [ordered]@{ exit = $LASTEXITCODE; output = @($trim | Select-Object -Last 5) }
    if ($LASTEXITCODE -eq 0) { Say "  fstrim: $(($trim | Select-Object -Last 3) -join '; ')" } else { Say '  fstrim was not available; the compaction still runs.' }
    if (-not $hadBusybox) { Invoke-Native 'docker' @('image', 'rm', 'busybox:1.37') | Out-Null }
    if ($helper.HasExited) { throw 'The administrator helper ended early: Docker was not stopped' }
    Wait-QuietTime -Minutes 60
    # A hidden watchdog starts Docker again if this window is closed while Docker is stopped.
    $watchdogArguments = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-File', "`"$PSCommandPath`"",
        '-Watchdog', '-Vhdx', "`"$Vhdx`"", '-Signal', "`"$signal`"", '-ParentId', "$PID")
    Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList $watchdogArguments -WindowStyle Hidden | Out-Null
    Say '  DO NOT CLOSE THIS WINDOW until it says the clean-up is done; it prints a line every 5 minutes.'
    $stopped = $true
    $output = Invoke-Native 'docker' @('desktop', 'stop', '--timeout', '300')
    if ($LASTEXITCODE -ne 0) { throw "Docker Desktop did not stop: $(($output | Select-Object -Last 2) -join ' ')" }
    $deadline = [DateTime]::UtcNow.AddSeconds(60)
    while (-not (Test-FileFree $Vhdx) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Seconds 5 }
    if (-not (Test-FileFree $Vhdx)) {
        Say '  The disk file is still in use: stopping WSL (other WSL programs start again when next used).'
        Invoke-Native 'wsl.exe' @('--shutdown') | Out-Null
        $deadline = [DateTime]::UtcNow.AddSeconds(90)
        while (-not (Test-FileFree $Vhdx) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Seconds 5 }
    }
    if (-not (Test-FileFree $Vhdx)) { throw 'The disk file is still in use after Docker and WSL stopped: it was not compacted' }
    Say '  Compacting (10 to 30 minutes for a large file)...'
    $started = [DateTime]::UtcNow
    New-Item -ItemType File -Path (Join-Path $signal 'go') -Force | Out-Null
    $go = $true
    # No deadline: Docker must not start while diskpart has the disk; the helper always reports when it ends.
    $next = [DateTime]::UtcNow.AddMinutes(5)
    while (-not (Test-Path -LiteralPath $done) -and -not (Test-HelperEnded)) {
        Start-Sleep -Seconds 5
        if ([DateTime]::UtcNow -ge $next) {
            Say "  Still compacting ($([math]::Round(([DateTime]::UtcNow - $started).TotalMinutes)) minutes so far)..."
            $next = [DateTime]::UtcNow.AddMinutes(5)
        }
    }
    Start-Sleep -Seconds 2
    if (-not (Test-Path -LiteralPath $done)) { throw 'The compaction did not report back' }
    $result = @([IO.File]::ReadAllLines($done))
    $record.compact = [ordered]@{ result = $result[0]; minutes = [math]::Round(([DateTime]::UtcNow - $started).TotalMinutes, 1)
        output = @($result | Select-Object -Skip 1 | Select-Object -Last 6) }
    if ($result[0] -ne 'exit=0') { Say "  The compaction failed ($($result[0])): $(($result | Select-Object -Last 3) -join ' ')"; $exitCode = 1 }
    else { Say "  Compacted in $($record.compact.minutes) minutes." }
} catch {
    Say "  STOPPED: $($_.Exception.Message)"
    $record.error = $_.Exception.Message
    $exitCode = 1
} finally {
    if ($stopped) {
        Say '[6/7] Starting Docker Desktop again'
        if ($go) {
            # Never start Docker while the helper may still hold the disk.
            while (-not (Test-Path -LiteralPath $done) -and -not (Test-HelperEnded)) { Start-Sleep -Seconds 5 }
            $deadline = [DateTime]::UtcNow.AddMinutes(30)
            while (-not (Test-FileFree $Vhdx) -and [DateTime]::UtcNow -lt $deadline) { Start-Sleep -Seconds 10 }
        }
        $output = Invoke-Native 'docker' @('desktop', 'start', '--timeout', '600')
        if ($LASTEXITCODE -ne 0) { Say "  Docker Desktop did not report a start: $(($output | Select-Object -Last 2) -join ' ')" }
        $deadline = [DateTime]::UtcNow.AddMinutes(10)
        $missing = @($running | ForEach-Object { $_.name })
        while ($missing.Count -and [DateTime]::UtcNow -lt $deadline) {
            Start-Sleep -Seconds 10
            $up = @{}
            foreach ($container in @(Get-ProjectContainers)) { if ($container.state -eq 'running') { $up[$container.name] = $true } }
            $missing = @($missing | Where-Object { -not $up.ContainsKey($_) })
        }
        $record.not_running_after = $missing
        if ($missing.Count) {
            Say "  NOT RUNNING after 10 minutes: $($missing -join ', '). Open Docker Desktop; if they stay down, run update-app.cmd."
            $exitCode = 1
        } else {
            Say "  All $($running.Count) app containers run again."
        }
    }
    Remove-Item -LiteralPath $signal -Recurse -Force -ErrorAction SilentlyContinue
}

if ($exitCode -eq 0) {
    Say '[7/7] Deleting old backups and old test-run folders'
    $deleted = 0; $freed = [long]0
    $failed = @(); $folders = @()
    foreach ($dump in $files.old) {
        try {
            Remove-Item -LiteralPath $dump.FullName -Force
            $freed += $dump.Length
            $deleted++
            $sha = "$($dump.FullName).sha256"
            if (Test-Path -LiteralPath $sha) { Remove-Item -LiteralPath $sha -Force }
            $parent = Split-Path -Parent $dump.FullName
            if (-not @(Get-ChildItem -LiteralPath $parent -Force).Count) { Remove-Item -LiteralPath $parent -Force }
        } catch { $failed += "$($dump.FullName): $($_.Exception.Message)" }
    }
    foreach ($folder in $files.folders) {
        # cmd's rd handles the long paths of old node_modules trees that Remove-Item in 5.1 trips on.
        Invoke-Native 'cmd.exe' @('/d', '/c', 'rd', '/s', '/q', $folder) | Out-Null
        if (Test-Path -LiteralPath $folder) { $failed += "${folder}: not fully deleted" } else { $folders += $folder }
    }
    $record.backups_deleted = $deleted
    $record.backup_bytes_freed = $freed
    $record.folders_deleted = $folders
    $record.not_deleted = $failed
    foreach ($line in $failed) { Say "  Not deleted: $line" }
    Say "  Deleted $deleted old backup(s) ($(Format-Gb $freed)) and $($folders.Count) old test-run folder(s)."
} else {
    Say '[7/7] Old backups and folders kept: the run did not finish cleanly.'
}

$after = (Get-Item -LiteralPath $Vhdx).Length
$record.vhdx_bytes_after = $after
$record.finished_utc = [DateTime]::UtcNow.ToString('o')
$record.status = if ($exitCode -eq 0) { 'COMPLETE' } else { 'FAILED' }
if (Test-Path -LiteralPath $BackupRoot) {
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    ($record | ConvertTo-Json -Depth 6) | Set-Content -LiteralPath (Join-Path $BackupRoot "docker-cleanup-$stamp.json") -Encoding UTF8
}
Say ''
Say "Docker's disk file: $(Format-Gb $before) before, $(Format-Gb $after) after."
exit $exitCode
