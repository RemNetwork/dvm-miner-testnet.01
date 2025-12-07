# DVM Miner - Official Release

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight, easy-to-use miner for the DVM (Decentralized Vector Machine) network. Earn Rem tokens by contributing your RAM to the network.

## 🚀 Quick Start

### Windows

1. **Download** the latest Windows release: `dvm-miner-windows-x64-v1.0.0.zip`
2. **Extract** the zip file
3. **Double-click** `start.bat`
4. Follow the setup prompts (first time only)

### macOS

1. **Download** the latest macOS release: `dvm-miner-macos-v1.0.0.tar.gz`
2. **Extract** the archive:
   ```bash
   tar -xzf dvm-miner-macos-v1.0.0.tar.gz
   cd dvm-miner-macos-v1.0.0
   ```
3. **Run** the start script:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Linux

1. **Download** the latest Linux release: `dvm-miner-linux-x64-v1.0.0.tar.gz`
2. **Extract** the archive:
   ```bash
   tar -xzf dvm-miner-linux-x64-v1.0.0.tar.gz
   cd dvm-miner-linux-x64-v1.0.0
   ```
3. **Run** the start script:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

## 📋 Requirements

- **Python 3.8 or higher** ([Download here](https://www.python.org/downloads/))
- **Internet connection**
- **Sui wallet address** (for receiving mining rewards)

### Getting a Sui Wallet

If you don't have a Sui wallet, you can create one using:
- **Sui Wallet** (Browser Extension): [Chrome Web Store](https://chrome.google.com/webstore)
- **Phantom Wallet** (Sui Network): [phantom.app](https://phantom.app)
- Any other Sui-compatible wallet

## 🎯 First Time Setup

When you run the miner for the first time, you'll be guided through a simple setup:

1. **RAM Commitment**: Choose how much RAM (2-128 GB) you want to commit to the network
   - More RAM = Higher potential rewards
   - Make sure you have enough free RAM on your system

2. **SUI Wallet Address**: Enter your Sui wallet address (0x...)
   - This is where you'll receive your mining rewards
   - Must be a valid Sui address (66 characters, starts with 0x)

3. **Referral ID** (optional): If someone referred you, enter their referral ID
   - Press Enter to use the default referral
   - This helps support the network

After setup, your configuration is saved and the miner starts automatically!

## 💰 Referral Program

**Earn 10% Extra Rem Tokens for Life!**

When you start mining, you'll receive a unique **Referral ID**. Share this ID with others:

1. When someone sets up their miner using your Referral ID
2. You automatically earn **10% of their mining rewards**
3. This benefit lasts for the **lifetime** of their mining activity!

Your Referral ID is automatically saved in `referral_info.txt` in your data directory.

### How to Use Your Referral ID

1. Find your Referral ID in `referral_info.txt` (created after first run)
2. Share it with friends, family, or on social media
3. When they set up their miner, they enter your ID during setup
4. You start earning 10% of their rewards automatically!

## 📁 Configuration

Your miner configuration is saved in:
- **Windows**: `C:\Users\<YourUsername>\.dvm_miner\config.json`
- **Linux/Mac**: `~/.dvm_miner/config.json`

You can edit this file directly if needed, or delete it to run setup again.

## 🔧 Usage

### Normal Usage

**Just run the start script** - it handles everything:
- Windows: Double-click `start.bat` or run `.\start.ps1` in PowerShell
- Linux/Mac: Run `./start.sh`

The miner will:
- Load your saved configuration
- Connect to the DVM network
- Start mining automatically

### Advanced Commands

If you want to run commands directly (after activating the virtual environment):

**Start Mining:**
```bash
python entry_point.py start
```

**Check Status:**
```bash
python entry_point.py status
```

## 🛠️ Troubleshooting

### Python Not Found

**Windows:**
- Make sure Python 3.8+ is installed
- During installation, check "Add Python to PATH"
- Or manually add Python to your system PATH

**Linux/Mac:**
- Install Python 3.8+ using your package manager
- On Mac: `brew install python3`
- On Ubuntu/Debian: `sudo apt install python3 python3-pip`

### Virtual Environment Issues

If you encounter virtual environment errors:
1. Delete the `venv` folder
2. Run the start script again
3. It will recreate the virtual environment

### Connection Issues

- Check your internet connection
- Ensure the coordinator URL is accessible
- Check if your firewall is blocking the connection
- Try running as administrator (Windows) or with sudo (Linux/Mac) if needed

### RAM Allocation Errors

If you get errors about RAM allocation:
- Make sure you have enough free RAM
- Reduce the RAM commitment in your config
- Close other memory-intensive applications

## 📊 Monitoring

The miner runs continuously and:
- Connects to the DVM network coordinator
- Receives and stores vector data
- Responds to search queries
- Sends periodic heartbeats

You can check your miner status anytime using:
```bash
python entry_point.py status
```

## 🔒 Security

- Your Sui wallet address is stored locally only
- No private keys are stored or transmitted
- All communication is encrypted via WebSocket (WSS)
- The miner only uses the RAM you specify

## 📝 License

This project is licensed under the MIT License.

## 🤝 Support

For issues, questions, or contributions:
- **GitHub Issues**: [Report an issue](https://github.com/RemNetwork/dvm-miner-testnet.01/issues)
- **Documentation**: Check the main DVM documentation

## 🎉 Getting Started Checklist

- [ ] Download the release for your platform
- [ ] Extract the archive
- [ ] Ensure Python 3.8+ is installed
- [ ] Have a Sui wallet address ready
- [ ] Run the start script
- [ ] Complete the setup (RAM, wallet address, referral)
- [ ] Start earning Rem tokens!

---

**Happy Mining! 🚀**
