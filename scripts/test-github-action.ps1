# Simulate GitHub Actions TypeScript CI Build Step

Write-Host "🧪 Simulating GitHub Actions Build Step..." -ForegroundColor Cyan
Write-Host ""

# Clean everything first
Write-Host "🧹 Cleaning environment..." -ForegroundColor Yellow
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force packages/*/node_modules -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force packages/*/dist -ErrorAction SilentlyContinue

# Fresh install
Write-Host "📦 Installing dependencies (npm ci)..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ npm install failed" -ForegroundColor Red
    exit 1
}

# Build all packages
Write-Host "🔨 Building all packages..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

# Test encoder-cli specifically (as GitHub Actions does)
Write-Host "🧪 Testing encoder-cli CLI functionality..." -ForegroundColor Yellow
Push-Location packages/encoder-cli

Write-Host "  Running: node dist/cli.js --help"
node dist/cli.js --help
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CLI help command failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "  Running: node dist/cli.js generate --type venue --output test-venue.json"
node dist/cli.js generate --type venue --output test-venue.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CLI generate command failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Clean up
Remove-Item test-venue.json -ErrorAction SilentlyContinue
Pop-Location

Write-Host ""
Write-Host "✅ All tests passed! GitHub Actions should work." -ForegroundColor Green 