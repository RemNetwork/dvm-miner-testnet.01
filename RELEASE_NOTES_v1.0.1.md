# Release Notes - v1.0.1

## 🎉 What's New

This release includes critical fixes that improve stability and reliability of the DVM Miner.

## 🔧 Critical Fixes

### Node ID Persistence
**Fixed**: Node ID was regenerating on every connection, causing issues with tracking and rewards.

**What changed:**
- Node ID now persists across all connections and restarts
- Configuration is automatically saved when node ID is generated
- Your miner will maintain the same identity throughout its lifetime

**Impact**: This ensures consistent tracking of your miner and prevents any issues with reward distribution.

### Shared Module Import Path
**Fixed**: Import errors in release packages due to incorrect shared module path resolution.

**What changed:**
- Fixed path resolution for shared protocol module
- Works correctly in both release packages and development environments
- All three platforms (Windows, macOS, Linux) verified

**Impact**: Eliminates import errors and ensures the miner runs correctly out of the box.

## ✅ Verified Improvements

### No Sui Client Dependencies
- Confirmed lightweight build with no external Sui dependencies
- Only uses `sui_address` as a string field (user provides it)
- No keystore or signing dependencies required

### Default Referral Address
- Verified default referral address is correctly set in all locations
- Users can press Enter during setup to use the default

## 📦 Installation

Download the appropriate package for your platform:

- **Windows**: `dvm-miner-windows-x64-v1.0.1.zip`
- **macOS**: `dvm-miner-macos-v1.0.1.tar.gz`
- **Linux**: `dvm-miner-linux-x64-v1.0.1.tar.gz`

Extract and run the start script - no additional configuration needed!

## 🔄 Upgrading from v1.0.0

If you're upgrading from v1.0.0:

1. **Backup your config** (optional but recommended):
   - Windows: `C:\Users\<YourUsername>\.dvm_miner\config.json`
   - Linux/Mac: `~/.dvm_miner/config.json`

2. **Download and extract** the new version

3. **Run the start script** - your existing configuration will be automatically upgraded

4. **Verify your node ID** - it should remain the same (this is the fix!)

## 🐛 Known Issues

None at this time. If you encounter any issues, please report them on [GitHub Issues](https://github.com/RemNetwork/dvm-miner-testnet.01/issues).

## 📝 Technical Details

### Files Modified
- `dvm_miner/config.py` - Node ID persistence logic
- `dvm_miner/node.py` - Fixed shared module import path

### Testing
- All three platform packages tested and verified
- Node ID persistence confirmed across multiple restarts
- Import paths verified in release packages

## 🙏 Thank You

Thank you for using DVM Miner! Your feedback helps us improve the software.

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md) for complete version history.

