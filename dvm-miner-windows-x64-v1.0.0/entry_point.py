"""Main entry point for DVM Miner.

Users should run start.bat (Windows) or start.sh (Linux/Mac) instead of this file directly.
This file is called by the start scripts.
"""

import sys
from pathlib import Path

# Add the current directory to sys.path so dvm_miner can be imported
current_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(current_dir))

from dvm_miner.cli import cli

if __name__ == "__main__":
    cli()

