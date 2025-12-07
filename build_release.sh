#!/bin/bash
# Build Release Packages for All Platforms
# Run this script to create release packages

set -e

echo "============================================"
echo "  DVM Miner - Release Builder"
echo "============================================"
echo ""

VERSION="v1.0.0"
BASEDIR=$(pwd)

# Clean function
clean_dir() {
    if [ -d "$1" ]; then
        rm -rf "$1"
    fi
}

# Clean previous builds
echo "Cleaning previous builds..."
clean_dir "dvm-miner-windows-x64-$VERSION"
clean_dir "dvm-miner-macos-$VERSION"
clean_dir "dvm-miner-linux-x64-$VERSION"
rm -f "dvm-miner-windows-x64-$VERSION.zip"
rm -f "dvm-miner-macos-$VERSION.tar.gz"
rm -f "dvm-miner-linux-x64-$VERSION.tar.gz"

# Windows Release
echo ""
echo "Building Windows release..."
mkdir -p "dvm-miner-windows-x64-$VERSION"
rsync -av --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' --exclude '.gitignore' --exclude 'RELEASE.md' --exclude 'build_release.ps1' --exclude 'build_release.sh' --exclude '*.zip' --exclude '*.tar.gz' ./ "dvm-miner-windows-x64-$VERSION/"
find "dvm-miner-windows-x64-$VERSION" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find "dvm-miner-windows-x64-$VERSION" -type f -name "*.pyc" -delete
zip -r "dvm-miner-windows-x64-$VERSION.zip" "dvm-miner-windows-x64-$VERSION" > /dev/null
echo "✓ Windows release created: dvm-miner-windows-x64-$VERSION.zip"

# macOS Release
echo ""
echo "Building macOS release..."
mkdir -p "dvm-miner-macos-$VERSION"
rsync -av --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' --exclude '.gitignore' --exclude 'RELEASE.md' --exclude 'build_release.ps1' --exclude 'build_release.sh' --exclude '*.zip' --exclude '*.tar.gz' ./ "dvm-miner-macos-$VERSION/"
find "dvm-miner-macos-$VERSION" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find "dvm-miner-macos-$VERSION" -type f -name "*.pyc" -delete
tar -czf "dvm-miner-macos-$VERSION.tar.gz" "dvm-miner-macos-$VERSION"
echo "✓ macOS release created: dvm-miner-macos-$VERSION.tar.gz"

# Linux Release
echo ""
echo "Building Linux release..."
mkdir -p "dvm-miner-linux-x64-$VERSION"
rsync -av --exclude '__pycache__' --exclude '*.pyc' --exclude '.git' --exclude '.gitignore' --exclude 'RELEASE.md' --exclude 'build_release.ps1' --exclude 'build_release.sh' --exclude '*.zip' --exclude '*.tar.gz' ./ "dvm-miner-linux-x64-$VERSION/"
find "dvm-miner-linux-x64-$VERSION" -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find "dvm-miner-linux-x64-$VERSION" -type f -name "*.pyc" -delete
tar -czf "dvm-miner-linux-x64-$VERSION.tar.gz" "dvm-miner-linux-x64-$VERSION"
echo "✓ Linux release created: dvm-miner-linux-x64-$VERSION.tar.gz"

echo ""
echo "============================================"
echo "  Release packages created successfully!"
echo "============================================"
echo ""
echo "Files created:"
echo "  - dvm-miner-windows-x64-$VERSION.zip"
echo "  - dvm-miner-macos-$VERSION.tar.gz"
echo "  - dvm-miner-linux-x64-$VERSION.tar.gz"
echo ""
echo "Next steps:"
echo "  1. Test each package on its respective platform"
echo "  2. Create a GitHub release at:"
echo "     https://github.com/RemNetwork/dvm-miner-testnet.01/releases"
echo "  3. Upload all three files to the release"
echo ""

