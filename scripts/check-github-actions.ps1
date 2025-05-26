# Script to check GitHub Actions status
param(
    [string]$WorkflowName = "TypeScript CI",
    [int]$MaxWaitMinutes = 10
)

Write-Host "🔍 Checking GitHub Actions status for: $WorkflowName" -ForegroundColor Cyan

# Get the latest workflow run
$latestRun = gh run list --workflow="$WorkflowName" --limit 1 --json databaseId,status,conclusion,headBranch,event | ConvertFrom-Json | Select-Object -First 1

if (-not $latestRun) {
    Write-Host "❌ No workflow runs found" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Latest run:" -ForegroundColor Yellow
Write-Host "  ID: $($latestRun.databaseId)"
Write-Host "  Branch: $($latestRun.headBranch)"
Write-Host "  Event: $($latestRun.event)"
Write-Host "  Status: $($latestRun.status)"

# If the workflow is in progress, wait for it
if ($latestRun.status -eq "in_progress" -or $latestRun.status -eq "queued") {
    Write-Host "⏳ Workflow is running. Waiting for completion..." -ForegroundColor Yellow
    
    # Watch the workflow
    gh run watch $latestRun.databaseId --exit-status
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "✅ Workflow completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "❌ Workflow failed!" -ForegroundColor Red
        
        # Show failed jobs
        Write-Host "`n📋 Failed jobs:" -ForegroundColor Red
        gh run view $latestRun.databaseId --json jobs | ConvertFrom-Json | Select-Object -ExpandProperty jobs | Where-Object { $_.conclusion -eq "failure" } | ForEach-Object {
            Write-Host "  - $($_.name)" -ForegroundColor Red
        }
        
        # Option to view logs
        Write-Host "`n📝 View logs with:" -ForegroundColor Yellow
        Write-Host "  gh run view $($latestRun.databaseId) --log-failed" -ForegroundColor Cyan
    }
} else {
    # Show the conclusion if already completed
    if ($latestRun.conclusion -eq "success") {
        Write-Host "✅ Last run was successful!" -ForegroundColor Green
    } else {
        Write-Host "❌ Last run failed with: $($latestRun.conclusion)" -ForegroundColor Red
    }
}

# Show recent runs
Write-Host "`n📊 Recent runs:" -ForegroundColor Cyan
gh run list --workflow="$WorkflowName" --limit 5 