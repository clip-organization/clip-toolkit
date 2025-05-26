# Script to commit, push, and monitor GitHub Actions
param(
    [string]$CommitMessage = "Test CI/CD fixes",
    [switch]$SkipCommit = $false
)

# Function to check for uncommitted changes
function Test-UncommittedChanges {
    $status = git status --porcelain
    return $status.Length -gt 0
}

Write-Host "🚀 GitHub Actions Test & Monitor" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if we need to commit
if (-not $SkipCommit) {
    if (Test-UncommittedChanges) {
        Write-Host "📝 Found uncommitted changes" -ForegroundColor Yellow
        
        # Show changes
        Write-Host "`nChanges to be committed:" -ForegroundColor Yellow
        git status --short
        
        # Commit and push
        Write-Host "`n📤 Committing and pushing..." -ForegroundColor Cyan
        git add -A
        git commit -m "$CommitMessage"
        git push
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to push changes" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✅ Changes pushed successfully" -ForegroundColor Green
        
        # Wait a moment for GitHub to process
        Write-Host "⏳ Waiting for GitHub to process push..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    } else {
        Write-Host "✅ No uncommitted changes" -ForegroundColor Green
    }
}

# Now monitor the workflow
Write-Host "`n🔍 Checking workflow status..." -ForegroundColor Cyan

# Get the latest run
$workflow = "TypeScript CI"
$latestRun = gh run list --workflow="$workflow" --limit 1 --json databaseId,status,conclusion,headBranch | ConvertFrom-Json | Select-Object -First 1

if ($latestRun) {
    Write-Host "📋 Latest workflow run:" -ForegroundColor Yellow
    Write-Host "  Run ID: $($latestRun.databaseId)"
    Write-Host "  Branch: $($latestRun.headBranch)"
    Write-Host "  Status: $($latestRun.status)"
    
    # If running, watch it
    if ($latestRun.status -eq "in_progress" -or $latestRun.status -eq "queued") {
        Write-Host "`n👀 Watching workflow run..." -ForegroundColor Yellow
        Write-Host "   (Press Ctrl+C to stop watching)" -ForegroundColor Gray
        
        # Use gh run watch which shows live progress
        gh run watch $latestRun.databaseId --exit-status
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ Workflow completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "`n❌ Workflow failed!" -ForegroundColor Red
            
            # Get failed jobs
            Write-Host "`n📋 Failed jobs and errors:" -ForegroundColor Red
            $jobs = gh run view $latestRun.databaseId --json jobs | ConvertFrom-Json | Select-Object -ExpandProperty jobs
            
            foreach ($job in $jobs) {
                if ($job.conclusion -eq "failure") {
                    Write-Host "`n❌ Job: $($job.name)" -ForegroundColor Red
                    
                    # Get annotations (errors/warnings)
                    $annotations = gh api "/repos/{owner}/{repo}/check-runs/$($job.databaseId)/annotations" | ConvertFrom-Json
                    
                    if ($annotations) {
                        foreach ($annotation in $annotations) {
                            Write-Host "  - $($annotation.message)" -ForegroundColor Red
                            if ($annotation.path) {
                                Write-Host "    File: $($annotation.path):$($annotation.start_line)" -ForegroundColor Gray
                            }
                        }
                    }
                }
            }
            
            Write-Host "`n📝 View full logs:" -ForegroundColor Yellow
            Write-Host "  gh run view $($latestRun.databaseId) --log-failed" -ForegroundColor Cyan
        }
    } else {
        # Show conclusion
        if ($latestRun.conclusion -eq "success") {
            Write-Host "✅ Last run completed: SUCCESS" -ForegroundColor Green
        } else {
            Write-Host "❌ Last run completed: $($latestRun.conclusion)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "❌ No workflow runs found" -ForegroundColor Red
}

Write-Host "`n📊 Recent workflow history:" -ForegroundColor Cyan
gh run list --workflow="$workflow" --limit 5 