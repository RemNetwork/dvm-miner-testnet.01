# GitHub Release Setup Guide

This guide will help you publish the DVM Miner to GitHub.

## Repository
https://github.com/RemNetwork/dvm-miner-testnet.01

## Step 1: Prepare the Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial release: DVM Miner v1.0.0"
   ```

2. **Add Remote**:
   ```bash
   git remote add origin https://github.com/RemNetwork/dvm-miner-testnet.01.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Build Release Packages

### On Windows:
```powershell
.\build_release.ps1
```

### On Linux/macOS:
```bash
chmod +x build_release.sh
./build_release.sh
```

This will create:
- `dvm-miner-windows-x64-v1.0.0.zip`
- `dvm-miner-macos-v1.0.0.tar.gz` (or .zip on Windows)
- `dvm-miner-linux-x64-v1.0.0.tar.gz` (or .zip on Windows)

## Step 3: Create GitHub Release

1. Go to: https://github.com/RemNetwork/dvm-miner-testnet.01/releases
2. Click **"Draft a new release"**
3. Fill in:
   - **Tag version**: `v1.0.0`
   - **Release title**: `DVM Miner v1.0.0`
   - **Description**: Copy from below

### Release Description Template:

```markdown
# DVM Miner v1.0.0

Official release of DVM Miner for Windows, macOS, and Linux.

## 🚀 Quick Start

1. Download the package for your platform
2. Extract the archive
3. Run `start.bat` (Windows) or `start.sh` (macOS/Linux)
4. Follow the setup prompts

## 📦 Downloads

- **Windows x64**: [dvm-miner-windows-x64-v1.0.0.zip](dvm-miner-windows-x64-v1.0.0.zip)
- **macOS**: [dvm-miner-macos-v1.0.0.tar.gz](dvm-miner-macos-v1.0.0.tar.gz)
- **Linux x64**: [dvm-miner-linux-x64-v1.0.0.tar.gz](dvm-miner-linux-x64-v1.0.0.tar.gz)

## ✨ Features

- ✅ Easy one-click setup
- ✅ Automatic dependency management
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Referral program (earn 10% extra rewards)
- ✅ Lightweight and efficient

## 📋 Requirements

- Python 3.8 or higher
- Internet connection
- Sui wallet address

## 📖 Documentation

See [README.md](README.md) for full documentation and troubleshooting.

## 🎉 Getting Started

1. Download the release for your platform
2. Extract and run the start script
3. Complete the setup (RAM, wallet address)
4. Start earning Rem tokens!

---

**Happy Mining! 🚀**
```

4. **Upload Files**: Drag and drop all three release files
5. Check **"Set as the latest release"**
6. Click **"Publish release"**

## Step 4: Verify Release

1. Visit the release page
2. Test downloading each package
3. Verify all files are accessible
4. Check that README.md is visible in the repository

## Notes

- Make sure `.gitignore` is committed to exclude cache files
- The release packages should NOT include `.git` folder
- Test each package on its respective platform before release
- Update version numbers in build scripts for future releases

