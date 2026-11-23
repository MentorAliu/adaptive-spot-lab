$ErrorActionPreference = 'Stop'

# Creates the main app's missing Docker secrets under secrets/ (Windows PowerShell 5.1 compatible; ASCII only).
# Existing values are never overwritten or printed.
$repository = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$secretDirectory = Join-Path $repository 'secrets'
# The secrets compose.yaml names (ExecPlan 0060: the agents' and the evaluation worker's are no longer used; an
# existing file of theirs is left as it is).
$names = @(
    'api_internal_key', 'postgres_password', 'api_db_password', 'market_worker_password', 'execution_db_password'
)

function New-SecretHex {
    $bytes = New-Object byte[] 32
    $generator = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
    return (-join ($bytes | ForEach-Object { $_.ToString('x2') }))
}

New-Item -ItemType Directory -Path $secretDirectory -Force | Out-Null
foreach ($name in $names) {
    $path = Join-Path $secretDirectory $name
    # Compose creates a missing secret file as an empty directory when a service using it starts; never treat that
    # directory as a secret.
    if (Test-Path -LiteralPath $path -PathType Container) {
        throw "Secret path $path is a directory (Docker creates one for a missing secret file); remove the empty directory and rerun"
    }
    if (-not (Test-Path -LiteralPath $path)) { [IO.File]::WriteAllText($path, (New-SecretHex)) }
}

Write-Output "Local Docker secrets are available in $secretDirectory"
