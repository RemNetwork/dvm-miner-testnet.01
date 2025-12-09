# GitHub Release v1.0.1 - Instructions

## Release Title
**DVM Miner v1.0.1 - Critical Fixes Release**

## Release Tag
`v1.0.1`

## Release Description

```markdown
## 🎉 DVM Miner v1.0.1 - Critical Fixes Release

This release includes critical fixes that improve stability and reliability of the DVM Miner.

### 🔧 Critical Fixes

**Node ID Persistence** - Fixed issue where node ID was regenerating on every connection. Your miner now maintains the same identity across all connections and restarts.

**Shared Module Import Path** - Fixed import errors in release packages. All platforms now work correctly out of the box.

### ✅ Verified Improvements

- No Sui client dependencies (lightweight build)
- Default referral address correctly set
- All three platforms tested and verified

### 📦 Downloads

- **Windows**: [dvm-miner-windows-x64-v1.0.1.zip](dvm-miner-windows-x64-v1.0.1.zip)
- **macOS**: [dvm-miner-macos-v1.0.1.tar.gz](dvm-miner-macos-v1.0.1.tar.gz)
- **Linux**: [dvm-miner-linux-x64-v1.0.1.tar.gz](dvm-miner-linux-x64-v1.0.1.tar.gz)

### 🔄 Upgrading

If upgrading from v1.0.0, simply download the new version and run the start script. Your existing configuration will be automatically upgraded.

### 📋 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

---

**Installation**: Extract the archive and run `start.bat` (Windows) or `./start.sh` (Linux/Mac)

**Requirements**: Python 3.8+ and a Sui wallet address

**Documentation**: See [README.md](README.md) for full documentation
```

## Files to Upload

1. **dvm-miner-windows-x64-v1.0.1.zip**
2. **dvm-miner-macos-v1.0.1.tar.gz**
3. **dvm-miner-linux-x64-v1.0.1.tar.gz**

## Steps to Create Release

1. **Build the release packages** (if not already done):
   ```powershell
   .\build_release.ps1
   ```

2. **Go to GitHub Releases**:
   - Navigate to: https://github.com/RemNetwork/dvm-miner-testnet.01/releases
   - Click "Draft a new release"

3. **Fill in the release form**:
   - **Tag version**: `v1.0.1`
   - **Release title**: `DVM Miner v1.0.1 - Critical Fixes Release`
   - **Description**: Copy the markdown from above
   - **Target**: `main` branch (or your default branch)

4. **Upload the three release files**:
   - Drag and drop or browse to upload:
     - `dvm-miner-windows-x64-v1.0.1.zip`
     - `dvm-miner-macos-v1.0.1.tar.gz`
     - `dvm-miner-linux-x64-v1.0.1.tar.gz`

5. **Publish the release**:
   - Check "Set as the latest release" if this is the latest
   - Click "Publish release"

## Release Checklist

- [x] Version updated to 1.0.1 in build scripts
- [x] CHANGELOG.md created with version history
- [x] README.md updated with version 1.0.1
- [x] RELEASE_NOTES_v1.0.1.md created
- [x] All three release packages built
- [x] Code verified and tested
- [ ] Release packages uploaded to GitHub
- [ ] Release published on GitHub

## Notes

- The release description above is ready to copy-paste into GitHub
- All three platform packages are ready for upload
- Documentation is complete and up-to-date
- This is a patch release (1.0.0 → 1.0.1) with critical fixes

