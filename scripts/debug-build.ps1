#!/usr/bin/env pwsh

Write-Host "🔍 Debugging TypeScript Build Issues" -ForegroundColor Blue
Write-Host "====================================" -ForegroundColor Blue

Write-Host ""
Write-Host "📦 Checking package structure..." -ForegroundColor Yellow
Get-ChildItem -Path "packages" -Recurse -Filter "tsconfig*.json" | Sort-Object FullName | ForEach-Object { Write-Host "  $($_.FullName)" }

Write-Host ""
Write-Host "🏗️ Checking build outputs..." -ForegroundColor Yellow
Get-ChildItem -Path "packages" -Recurse -Directory -Name "dist" | ForEach-Object {
    $distPath = "packages/$_"
    Write-Host "  $distPath/dist:"
    $items = Get-ChildItem -Path "$distPath/dist" -ErrorAction SilentlyContinue | Select-Object -First 5
    if ($items) {
        $items | ForEach-Object { Write-Host "    $($_.Name)" }
    } else {
        Write-Host "    (empty or missing)"
    }
}

Write-Host ""
Write-Host "🔗 Checking project references..." -ForegroundColor Yellow
$references = Select-String -Path "packages/*/tsconfig*.json" -Pattern "references" -ErrorAction SilentlyContinue
if ($references) {
    $references | ForEach-Object { Write-Host "  $($_.Filename): $($_.Line.Trim())" }
} else {
    Write-Host "  No references found"
}

Write-Host ""
Write-Host "⚙️ Running clean build..." -ForegroundColor Yellow
npm run clean
npm run build:verbose

Write-Host ""
Write-Host "✅ Build completed. Check output above for errors." -ForegroundColor Green 