# Changelog

All notable changes to the DVM Miner will be documented in this file.

## [1.0.1] - 2024-12-XX

### Fixed
- **Node ID Persistence**: Fixed critical issue where node ID was regenerating on every connection. Node ID now persists across all connections and restarts.
- **Shared Module Import Path**: Fixed import path for shared protocol module in release packages. Now correctly finds shared module in all environments.

### Verified
- **No Sui Client Dependencies**: Confirmed lightweight build with no Sui client, keystore, or signing dependencies. Only uses `sui_address` as a string field.
- **Default Referral Address**: Verified default referral address `f5e3a292-b3fc-480e-93c6-b475cffd6c18` is correctly set in all locations.

### Technical Details
- `load_config()` now checks if node_id exists before generating, and immediately saves it back to config file
- `save_config()` ensures node_id is never empty when saving
- Shared module path logic fixed to work in both release packages and development environment
- All three platform packages (Windows, macOS, Linux) verified and tested

## [1.0.0] - 2024-12-XX

### Added
- Initial release of DVM Miner - Clean Version
- Interactive setup wizard for first-time configuration
- RAM commitment selection (2GB to 128GB)
- Sui wallet address validation and setup
- Referral program integration
- Cross-platform support (Windows, macOS, Linux)
- Automatic virtual environment setup
- Self-contained shared protocol module
- Referral information file generation
- Status command to view miner configuration and statistics

### Features
- Lightweight build with no external Sui client dependencies
- Persistent configuration storage
- Automatic reconnection to coordinator
- Vector storage and search capabilities
- PoRAM (Proof of RAM) challenge support
- Heartbeat monitoring
- Background autosave functionality

