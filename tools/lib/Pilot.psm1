# Shared helpers for the update file and the Docker clean-up (Compose calls and the backup).
# Windows PowerShell 5.1 compatible; ASCII only. Every Compose call names its project and
# env file explicitly. Nothing here removes volumes, prunes, or reads secret values.

# A tool's own 'Stop' reaches these functions only when the tool is started with powershell -File,
# where it runs in the global scope. Called by its path from a session, they would print an error
# and the tool would go on. Set here, an error in them stops the tool in both.
$ErrorActionPreference = 'Stop'

function New-PilotCompose {
    param([Parameter(Mandatory = $true)][string]$Project, [Parameter(Mandatory = $true)][string]$EnvFile)
    if (-not (Test-Path -LiteralPath $EnvFile)) { throw "Env file not found: $EnvFile" }
    $file = Join-Path (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path 'compose.yaml'
    return @{ project = $Project; env_file = (Resolve-Path -LiteralPath $EnvFile).Path; file = $file }
}

function Get-EnvValue {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = '')
    # Reads one KEY=VALUE line; no other line is returned or printed.
    foreach ($line in [IO.File]::ReadAllLines($Path)) {
        if ($line -match "^\s*$([regex]::Escape($Name))\s*=\s*(.*)$") { return $Matches[1].Trim() }
    }
    return $Default
}

function Invoke-PilotCompose {
    param([Parameter(Mandatory = $true)][hashtable]$Compose, [Parameter(Mandatory = $true)][string[]]$Arguments,
        [switch]$AllowFailure)
    $command = @('compose', '-f', $Compose.file, '-p', $Compose.project, '--env-file', $Compose.env_file) + $Arguments
    # Windows PowerShell 5.1 turns native stderr into error records; keep them as text.
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = @(& docker @command 2>&1 | ForEach-Object { "$_" })
        $code = $LASTEXITCODE
    } finally { $ErrorActionPreference = $saved }
    if ($code -ne 0 -and -not $AllowFailure) { throw "docker compose $($Arguments -join ' ') failed ($code): $output" }
    return $output
}

function Protect-Path {
    param([Parameter(Mandatory = $true)][string]$Path)
    # Owner-only ACL on the backup directory (inheritance removed).
    $account = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    $saved = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { & icacls $Path /inheritance:r /grant:r "${account}:(OI)(CI)F" | Out-Null } finally { $ErrorActionPreference = $saved }
    if ($LASTEXITCODE -ne 0) { throw "Could not restrict the ACL of $Path" }
}

function New-ProtectedBackup {
    # -Database: the database name the caller already read from the env file; read here when not given.
    # -RequireRoom: refuse when the disk the database lives on has less free space than the database's
    # size plus one GiB. The dump is written inside the database container before it is copied out.
    param([Parameter(Mandatory = $true)][hashtable]$Compose, [Parameter(Mandatory = $true)][string]$BackupRoot,
        [Parameter(Mandatory = $true)][string]$Label, [string[]]$Tables = @(), [switch]$DataOnly, [string]$Database = '',
        [switch]$RequireRoom)
    if (-not $Database) { $Database = Get-EnvValue -Path $Compose.env_file -Name 'ASL_DB_NAME' -Default 'asl' }
    if ($RequireRoom) {
        $space = Invoke-PilotCompose -Compose $Compose -Arguments @('exec', '-T', 'postgres', 'df', '-Pk', '/var/lib/postgresql/data')
        $columns = @("$($space | Select-Object -Last 1)".Trim() -split '\s+')
        if ($columns.Count -lt 4 -or $columns[3] -notmatch '^\d+$') { throw 'Could not read the free space of the disk the database lives on' }
        $size = "$(Invoke-PilotCompose -Compose $Compose -Arguments @('exec', '-T', 'postgres', 'psql', '-X', '-U', 'asl', '-d', $Database,
            '-At', '-v', 'ON_ERROR_STOP=1', '-c', 'SELECT pg_database_size(current_database())') | Select-Object -Last 1)".Trim()
        if ($size -notmatch '^\d+$') { throw 'Could not read the size of the database' }
        if ([long]$columns[3] * 1024 -lt [long]$size + 1GB) {
            throw "Not enough free space for a dump of the database: $([math]::Round([long]$columns[3] / 1MB, 1)) GiB free, database $([math]::Round([long]$size / 1GB, 1)) GiB"
        }
    }
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
    $directory = Join-Path $BackupRoot "$Label-$stamp"
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    Protect-Path -Path $directory
    $dump = @('exec', '-T', 'postgres', 'pg_dump', '-U', 'asl', '-d', $Database, '-Fc', '-f', '/tmp/pilot-backup.dump')
    if ($DataOnly) { $dump += '--data-only' }
    foreach ($table in $Tables) { $dump += @('-t', $table) }
    $target = Join-Path $directory "$Database.dump"
    $removed = $false
    try {
        Invoke-PilotCompose -Compose $Compose -Arguments $dump | Out-Null
        $container = (Invoke-PilotCompose -Compose $Compose -Arguments @('ps', '-q', 'postgres') | Select-Object -Last 1).Trim()
        $saved = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try { & docker cp "${container}:/tmp/pilot-backup.dump" $target 2>&1 | Out-Null } finally { $ErrorActionPreference = $saved }
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $target)) { throw 'Backup copy failed' }
    } finally {
        # The dump leaves the database container whether or not it was written completely or copied out.
        Invoke-PilotCompose -Compose $Compose -Arguments @('exec', '-T', 'postgres', 'rm', '-f', '/tmp/pilot-backup.dump') -AllowFailure | Out-Null
        $removed = ($LASTEXITCODE -eq 0)
    }
    if (-not $removed) { throw 'The dump could not be removed from the database container (/tmp/pilot-backup.dump)' }
    $sha = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
    "$sha  $(Split-Path -Leaf $target)" | Set-Content -LiteralPath "$target.sha256" -Encoding ASCII
    return @{ path = $target; sha256 = $sha; bytes = (Get-Item -LiteralPath $target).Length }
}

Export-ModuleMember -Function New-PilotCompose, Get-EnvValue, Invoke-PilotCompose, Protect-Path, New-ProtectedBackup
