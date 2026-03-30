param(
    [string]$CredentialsPath = (Join-Path $PSScriptRoot "credentials.json"),
    [string]$OutputPath = (Join-Path $PSScriptRoot ".env")
)

if (-not (Test-Path $CredentialsPath)) {
    Write-Error "credentials.json not found at $CredentialsPath"
    exit 1
}

try {
    $content = Get-Content -Path $CredentialsPath -Raw -Encoding UTF8
    $credentials = $content | ConvertFrom-Json -ErrorAction Stop
}
catch {
    Write-Error "Failed to parse credentials.json: $($_.Exception.Message)"
    exit 1
}

if (-not $credentials.database) {
    Write-Error "credentials.json must include a top-level 'database' object"
    exit 1
}

$db = $credentials.database
$requiredKeys = @("user", "password", "name", "port")

foreach ($key in $requiredKeys) {
    if (-not ($db.PSObject.Properties.Name -contains $key)) {
        Write-Error "credentials.json missing database.$key"
        exit 1
    }
}

$user = [string]$db.user
$password = [string]$db.password
$name = [string]$db.name
$port = [int]$db.port

$encodedUser = [System.Uri]::EscapeDataString($user)
$encodedPassword = [System.Uri]::EscapeDataString($password)
$databaseUrl = "postgresql://${encodedUser}:${encodedPassword}@db:${port}/${name}"

$lines = @(
    "DB_USER=$user",
    "DB_PASSWORD=$password",
    "DB_NAME=$name",
    "DB_PORT=$port",
    "DATABASE_URL=$databaseUrl"
)

Set-Content -Path $OutputPath -Value ($lines -join "`n") -Encoding UTF8
Write-Host "Generated $OutputPath from $CredentialsPath"
