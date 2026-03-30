function datahub {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]] $Arguments
    )

    if ($Arguments.Count -eq 0) {
        Write-Host "Usage: datahub <init|push|log|query> [args]"
        return
    }

    $command = $Arguments[0]
    $rest = @()
    if ($Arguments.Count -gt 1) {
        $rest = $Arguments[1..($Arguments.Count - 1)]
    }

    if ($command -eq "push") {
        if ($rest.Count -eq 0 -or $rest[0].StartsWith("-")) {
            $rest = @("http://localhost:8000") + $rest
        }
    } elseif ($command -eq "log") {
        if ($rest.Count -eq 0) {
            $rest = @("http://localhost:8000")
        }
    } elseif ($command -eq "query") {
        if ($rest.Count -eq 0) {
            Write-Host "Usage: datahub query \"metric operator value\""
            return
        }
        if (-not $rest[0].StartsWith("http://") -and -not $rest[0].StartsWith("https://")) {
            $rest = @("http://localhost:8000") + $rest
        }
    }

    docker compose exec -w /app/live_demo_workspace dev-env python -m cli.main $command @rest
}

Write-Host "Loaded datahub alias for /app/live_demo_workspace"
Write-Host "Example: datahub init"
Write-Host 'Example: datahub push -m "Initial demo snapshot"'
Write-Host "Example: datahub log"
Write-Host 'Example: datahub query "row_count == 9"'
