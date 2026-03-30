param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Args
)

if ($Args.Count -eq 0) {
    Write-Host "Usage: datahub <init|push|log|query> [args]"
    Write-Host 'Tip (cmd): use double quotes, e.g. datahub push -m "initial demo"'
    exit 1
}

$command = $Args[0]
$rest = @()
if ($Args.Count -gt 1) {
    $rest = $Args[1..($Args.Count - 1)]
}

$remoteUrl = if ($env:DATAHUB_REMOTE_URL) { $env:DATAHUB_REMOTE_URL } else { "http://localhost:8000" }

if ($command -eq "push") {
    if ($rest.Count -eq 0 -or $rest[0].StartsWith("-")) {
        $rest = @($remoteUrl) + $rest
    }
}
elseif ($command -eq "log") {
    if ($rest.Count -eq 0) {
        $rest = @($remoteUrl)
    }
}
elseif ($command -eq "query") {
    if ($rest.Count -eq 0) {
        Write-Host 'Usage: datahub query "metric operator value"'
        exit 1
    }

    if ($rest[0].StartsWith("http://") -or $rest[0].StartsWith("https://")) {
        if ($rest.Count -eq 1) {
            Write-Host 'Usage: datahub query <remote_url> "metric operator value"'
            exit 1
        }
        $queryExpr = ($rest[1..($rest.Count - 1)] -join " ")
        $rest = @($rest[0], $queryExpr)
    }
    else {
        $queryExpr = ($rest -join " ")
        $rest = @($remoteUrl, $queryExpr)
    }
}

& docker compose exec -w /app/live_demo_workspace dev-env python -m cli.main $command @rest
exit $LASTEXITCODE
