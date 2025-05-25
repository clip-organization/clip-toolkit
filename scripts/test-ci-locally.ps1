# Script to test GitHub Actions workflow locally on Windows

Write-Host "🧪 Testing GitHub Actions workflow locally..." -ForegroundColor Cyan
Write-Host "This simulates what happens in the CI pipeline"
Write-Host ""

# Function to run a step
function Run-Step {
    param(
        [string]$StepName,
        [string]$Command
    )
    
    Write-Host "▶ Running: $StepName" -ForegroundColor Yellow
    Write-Host "  Command: $Command"
    
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0 -or $null -eq $LASTEXITCODE) {
            Write-Host "✓ $StepName passed" -ForegroundColor Green
            Write-Host ""
            return $true
        } else {
            Write-Host "✗ $StepName failed" -ForegroundColor Red
            Write-Host ""
            return $false
        }
    } catch {
        Write-Host "✗ $StepName failed with error: $_" -ForegroundColor Red
        Write-Host ""
        return $false
    }
}

# Clean environment
Write-Host "🧹 Cleaning environment..." -ForegroundColor Cyan
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force packages/*/node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force packages/*/dist -ErrorAction SilentlyContinue

# Setup
Run-Step "Install dependencies" "npm ci"

# Lint
Write-Host "🔍 Testing lint job..." -ForegroundColor Cyan
foreach ($package in @("encoder-cli", "decoder-lib", "validator-core")) {
    Run-Step "Lint $package" "cd packages/$package; npm run lint; cd ../.."
}

# Type checking
Write-Host "📝 Testing type checking..." -ForegroundColor Cyan
Run-Step "TypeScript build (all packages)" "npm run build"

# Test
Write-Host "🧪 Testing test job..." -ForegroundColor Cyan
foreach ($package in @("encoder-cli", "decoder-lib", "validator-core")) {
    Run-Step "Test $package" "cd packages/$package; npm test; cd ../.."
}

# Build individual packages (like GitHub Actions does)
Write-Host "🏗️ Testing individual package builds..." -ForegroundColor Cyan
foreach ($package in @("encoder-cli", "decoder-lib", "validator-core")) {
    # Clean first
    Remove-Item -Recurse -Force "packages/$package/dist" -ErrorAction SilentlyContinue
    
    # Build all (to ensure dependencies are built)
    Run-Step "Build for $package" "npm run build"
    
    # Check if dist exists
    if (Test-Path "packages/$package/dist") {
        Write-Host "✓ $package has dist directory" -ForegroundColor Green
    } else {
        Write-Host "✗ $package missing dist directory" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Local CI test complete!" -ForegroundColor Cyan
Write-Host "If all steps passed, your GitHub Actions workflow should succeed." 