# Release Instructions

This document explains how to create releases for Windows, macOS, and Linux.

## Prerequisites

- All code is tested and working
- README.md is up to date
- Version number is correct

## Creating Releases

### For All Platforms

1. **Clean the repository:**
   ```bash
   # Remove any cache files
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

2. **Create release packages:**

#### Windows Release

```bash
# On Windows
# Create a clean copy
xcopy /E /I /Y miner_rem_lite dvm-miner-windows-x64-v1.0.0

# Remove unnecessary files
cd dvm-miner-windows-x64-v1.0.0
del /S /Q __pycache__
del /S /Q *.pyc
del /S /Q .git
del /S /Q .gitignore
del /S /Q RELEASE.md

# Create zip
cd ..
powershell Compress-Archive -Path dvm-miner-windows-x64-v1.0.0 -DestinationPath dvm-miner-windows-x64-v1.0.0.zip
```

#### macOS Release

```bash
# On macOS/Linux
# Create a clean copy
cp -r miner_rem_lite dvm-miner-macos-v1.0.0

# Remove unnecessary files
cd dvm-miner-macos-v1.0.0
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
rm -rf .git .gitignore RELEASE.md

# Create tar.gz
cd ..
tar -czf dvm-miner-macos-v1.0.0.tar.gz dvm-miner-macos-v1.0.0
```

#### Linux Release

```bash
# On Linux
# Create a clean copy
cp -r miner_rem_lite dvm-miner-linux-x64-v1.0.0

# Remove unnecessary files
cd dvm-miner-linux-x64-v1.0.0
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
rm -rf .git .gitignore RELEASE.md

# Create tar.gz
cd ..
tar -czf dvm-miner-linux-x64-v1.0.0.tar.gz dvm-miner-linux-x64-v1.0.0
```

## GitHub Release

1. Go to https://github.com/RemNetwork/dvm-miner-testnet.01/releases
2. Click "Draft a new release"
3. Tag version: `v1.0.0`
4. Release title: `DVM Miner v1.0.0`
5. Description:
   ```
   # DVM Miner v1.0.0
   
   Official release of DVM Miner for Windows, macOS, and Linux.
   
   ## Downloads
   
   - **Windows**: [dvm-miner-windows-x64-v1.0.0.zip](dvm-miner-windows-x64-v1.0.0.zip)
   - **macOS**: [dvm-miner-macos-v1.0.0.tar.gz](dvm-miner-macos-v1.0.0.tar.gz)
   - **Linux**: [dvm-miner-linux-x64-v1.0.0.tar.gz](dvm-miner-linux-x64-v1.0.0.tar.gz)
   
   ## Quick Start
   
   1. Download the package for your platform
   2. Extract the archive
   3. Run `start.bat` (Windows), `start.sh` (macOS/Linux)
   4. Follow the setup prompts
   
   See README.md for full documentation.
   ```
6. Upload all three release files
7. Publish release

## Release Checklist

- [ ] Code is tested and working
- [ ] README.md is complete and accurate
- [ ] All three platform packages created
- [ ] Packages tested on each platform
- [ ] GitHub release created with all files
- [ ] Release notes are clear and helpful

