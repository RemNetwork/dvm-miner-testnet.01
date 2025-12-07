"""Miner CLI commands."""

import json
import sys
import uuid
from pathlib import Path

import click

from dvm_miner.config import MinerConfig, load_config, save_config
from dvm_miner.node import MinerNode


def validate_sui_address(address: str) -> bool:
    """Validate Sui address format."""
    if not address.startswith("0x"):
        return False
    if len(address) != 66:
        return False
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


@click.group()
def cli():
    """DVM Miner CLI - Clean Version"""
    pass


@cli.command()
@click.option(
    "--data-dir",
    type=click.Path(),
    default=None,
    help="Data directory for miner"
)
def start(data_dir: str):
    """Start the miner node with interactive setup."""
    # Determine data directory
    if data_dir is None:
        data_dir = str(Path.home() / ".dvm_miner")
    else:
        data_dir = str(Path(data_dir).expanduser())
    
    data_path = Path(data_dir)
    config_path = data_path / "config.json"
    
    # Interactive setup if config doesn't exist
    if not config_path.exists():
        click.echo("\n" + "="*60)
        click.echo("🚀 Welcome to DVM Miner Setup!")
        click.echo("="*60 + "\n")
        
        # 1. Ask for RAM commitment (2GB to 128GB)
        while True:
            try:
                ram_input = click.prompt(
                    "How much RAM (in GB) do you want to commit? (2-128)",
                    type=int,
                    default=4
                )
                if 2 <= ram_input <= 128:
                    max_ram_gb = ram_input
                    break
                else:
                    click.echo("❌ Please enter a value between 2 and 128 GB")
            except click.Abort:
                click.echo("\nSetup cancelled.")
                return
            except ValueError:
                click.echo("❌ Please enter a valid number")
        
        # 2. Ask for SUI wallet address
        click.echo("\n" + "-"*60)
        click.echo("📝 SUI Wallet Address Required")
        click.echo("-"*60)
        click.echo("You need a Sui wallet address to receive mining rewards.")
        click.echo("If you don't have one, you can create it using:")
        click.echo("  • Sui Wallet (Browser Extension): https://chrome.google.com/webstore")
        click.echo("  • Phantom Wallet (Sui Network): https://phantom.app")
        click.echo("  • Or any other Sui-compatible wallet")
        click.echo("-"*60 + "\n")
        
        while True:
            sui_address = click.prompt(
                "Enter your Sui wallet address (0x...)",
                type=str
            ).strip()
            
            if validate_sui_address(sui_address):
                break
            else:
                click.echo("❌ Invalid Sui address format.")
                click.echo("   Must start with '0x' and be 66 characters long (hex format)")
                click.echo("   Example: 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef")
        
        # 3. Ask for referral address (optional)
        default_referral = "f5e3a292-b3fc-480e-93c6-b475cffd6c18"
        click.echo("\n" + "-"*60)
        click.echo("🎁 Referral Program")
        click.echo("-"*60)
        click.echo("If someone referred you, enter their referral ID.")
        click.echo("Otherwise, press Enter to use the default.")
        click.echo("-"*60 + "\n")
        
        referral_address = click.prompt(
            "Enter referral ID (or press Enter for default)",
            type=str,
            default=default_referral,
            show_default=False
        ).strip()
        
        if not referral_address:
            referral_address = default_referral
        
        # Create config
        config = MinerConfig.default()
        config.data_dir = data_dir
        config.node_id = str(uuid.uuid4())
        config.max_ram_gb = max_ram_gb
        config.sui_address = sui_address
        config.referral_address = referral_address
        
        # Save config
        data_path.mkdir(parents=True, exist_ok=True)
        save_config(config, config_path)
        
        click.echo("\n" + "="*60)
        click.echo("✅ Configuration saved!")
        click.echo("="*60)
        click.echo(f"Data directory: {data_dir}")
        click.echo(f"Node ID: {config.node_id}")
        click.echo(f"RAM commitment: {max_ram_gb} GB")
        click.echo(f"SUI address: {sui_address}")
        click.echo("="*60 + "\n")
        
        # Display referral info
        click.echo("💰 REFERRAL PROGRAM")
        click.echo("-"*60)
        click.echo(f"Your Referral ID: {config.node_id}")
        click.echo("")
        click.echo("Share this ID with others to earn 10% of their mining rewards!")
        click.echo("You'll receive 10% extra Rem tokens for life from each referral!")
        click.echo("-"*60 + "\n")
    
    # Load config
    try:
        config = load_config(config_path)
        # Ensure data_dir is expanded
        if config.data_dir.startswith("~"):
            config.data_dir = str(Path(config.data_dir).expanduser())
        else:
            config.data_dir = str(Path(config.data_dir))
    except Exception as e:
        click.echo(f"❌ Error loading config: {e}", err=True)
        return
    
    # Validate required fields
    if not config.sui_address:
        click.echo("❌ Error: Sui address not configured. Please run setup again.", err=True)
        return
    
    if not config.node_id:
        config.node_id = str(uuid.uuid4())
        save_config(config, config_path)
    
    # Ensure referral_address is set (should be set by load_config, but double-check)
    if not config.referral_address:
        config.referral_address = "f5e3a292-b3fc-480e-93c6-b475cffd6c18"
        save_config(config, config_path)
    
    # Display startup info
    click.echo("\n" + "="*60)
    click.echo("🚀 Starting DVM Miner")
    click.echo("="*60)
    click.echo(f"Node ID: {config.node_id}")
    click.echo(f"RAM: {config.max_ram_gb} GB")
    click.echo(f"Connecting to: {config.coordinator_url}")
    click.echo("="*60 + "\n")
    
    # Start miner
    node = MinerNode(config)
    
    try:
        node.start()
    except KeyboardInterrupt:
        click.echo("\n\nShutting down miner...")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        node.shutdown()


@cli.command()
@click.option(
    "--data-dir",
    type=click.Path(),
    default=str(Path.home() / ".dvm_miner"),
    help="Data directory for miner"
)
def status(data_dir: str):
    """Show miner status."""
    data_path = Path(data_dir).expanduser()
    config_path = data_path / "config.json"
    
    if not config_path.exists():
        click.echo(f"❌ Config not found at {config_path}")
        return
    
    try:
        config = load_config(config_path)
        
        click.echo("\n" + "="*60)
        click.echo("📊 Miner Status")
        click.echo("="*60)
        click.echo(f"Node ID: {config.node_id}")
        click.echo(f"Data directory: {config.data_dir}")
        click.echo(f"Coordinator URL: {config.coordinator_url}")
        click.echo(f"Max RAM: {config.max_ram_gb} GB")
        click.echo(f"SUI Address: {config.sui_address}")
        click.echo(f"Referral ID: {config.referral_address}")
        
        # Load engine to get stats
        try:
            from dvm_miner.engine import VectorEngine
            engine = VectorEngine(
                data_dir=data_path,
                embedding_dim=config.embedding_dim,
                max_ram_gb=config.max_ram_gb
            )
            
            total_vectors = engine.get_total_vectors()
            bytes_used = engine.get_bytes_used()
            collections = len(engine.indices)
            
            click.echo("\n" + "-"*60)
            click.echo("Storage Statistics")
            click.echo("-"*60)
            click.echo(f"Collections: {collections}")
            click.echo(f"Total vectors: {total_vectors:,}")
            click.echo(f"Bytes used: {bytes_used / (1024**2):.2f} MB")
            click.echo(f"Capacity: {(bytes_used / engine.max_bytes) * 100:.1f}%")
        except Exception as e:
            click.echo(f"\n⚠️  Could not load engine stats: {e}")
        
        click.echo("="*60 + "\n")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)


if __name__ == "__main__":
    cli()

