#!/bin/bash
# ============================================
# DVM Miner - Linux/Mac Starter Script
# ============================================

# Change to the script's directory
cd "$(dirname "$0")"

echo ""
echo "============================================"
echo "  DVM Miner - Clean Version"
echo "============================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "Found Python: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Install/upgrade dependencies
echo "Installing/updating dependencies..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Start the miner
echo ""
echo "Starting DVM Miner..."
echo ""
python3 entry_point.py start

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "Miner stopped with an error."
    read -p "Press Enter to exit..."
fi

