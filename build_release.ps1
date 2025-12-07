# Build Release Packages for All Platforms
# Run this script to create release packages

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  DVM Miner - Release Builder" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$version = "v1.0.0"
$baseDir = Get-Location

# Clean function
function Clean-Directory {
    param($dir)
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
    }
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Clean-Directory "dvm-miner-windows-x64-$version"
Clean-Directory "dvm-miner-macos-$version"
Clean-Directory "dvm-miner-linux-x64-$version"

# Windows Release
Write-Host "`nBuilding Windows release..." -ForegroundColor Green
New-Item -ItemType Directory -Path "dvm-miner-windows-x64-$version" | Out-Null
Copy-Item -Recurse -Exclude "__pycache__","*.pyc",".git",".gitignore","RELEASE.md","build_release.ps1","build_release.sh" -Path "." -Destination "dvm-miner-windows-x64-$version"
Get-ChildItem -Path "dvm-miner-windows-x64-$version" -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path "dvm-miner-windows-x64-$version" -Recurse -Include "*.pyc" | Remove-Item -Force
Compress-Archive -Path "dvm-miner-windows-x64-$version" -DestinationPath "dvm-miner-windows-x64-$version.zip" -Force
Write-Host "✓ Windows release created: dvm-miner-windows-x64-$version.zip" -ForegroundColor Green

# macOS Release
Write-Host "`nBuilding macOS release..." -ForegroundColor Green
New-Item -ItemType Directory -Path "dvm-miner-macos-$version" | Out-Null
Copy-Item -Recurse -Exclude "__pycache__","*.pyc",".git",".gitignore","RELEASE.md","build_release.ps1","build_release.sh" -Path "." -Destination "dvm-miner-macos-$version"
Get-ChildItem -Path "dvm-miner-macos-$version" -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path "dvm-miner-macos-$version" -Recurse -Include "*.pyc" | Remove-Item -Force
Compress-Archive -Path "dvm-miner-macos-$version" -DestinationPath "dvm-miner-macos-$version.zip" -Force
Write-Host "✓ macOS release created: dvm-miner-macos-$version.zip" -ForegroundColor Green

# Linux Release
Write-Host "`nBuilding Linux release..." -ForegroundColor Green
New-Item -ItemType Directory -Path "dvm-miner-linux-x64-$version" | Out-Null
Copy-Item -Recurse -Exclude "__pycache__","*.pyc",".git",".gitignore","RELEASE.md","build_release.ps1","build_release.sh" -Path "." -Destination "dvm-miner-linux-x64-$version"
Get-ChildItem -Path "dvm-miner-linux-x64-$version" -Recurse -Include "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Path "dvm-miner-linux-x64-$version" -Recurse -Include "*.pyc" | Remove-Item -Force
Compress-Archive -Path "dvm-miner-linux-x64-$version" -DestinationPath "dvm-miner-linux-x64-$version.zip" -Force
Write-Host "✓ Linux release created: dvm-miner-linux-x64-$version.zip" -ForegroundColor Green

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "  Release packages created successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files created:" -ForegroundColor Yellow
Write-Host "  - dvm-miner-windows-x64-$version.zip" -ForegroundColor White
Write-Host "  - dvm-miner-macos-$version.zip" -ForegroundColor White
Write-Host "  - dvm-miner-linux-x64-$version.zip" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test each package on its respective platform" -ForegroundColor White
Write-Host "  2. Create a GitHub release at:" -ForegroundColor White
Write-Host "     https://github.com/RemNetwork/dvm-miner-testnet.01/releases" -ForegroundColor Cyan
Write-Host "  3. Upload all three zip files to the release" -ForegroundColor White
Write-Host ""

