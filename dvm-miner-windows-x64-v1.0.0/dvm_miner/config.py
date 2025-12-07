"""Miner configuration."""

import json
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class MinerConfig:
    """Miner configuration."""
    coordinator_url: str
    data_dir: str
    node_id: str
    max_ram_gb: int
    embedding_dim: int
    index_version: int
    miner_secret: str
    sui_address: str
    referral_address: str
    
    @classmethod
    def default(cls) -> "MinerConfig":
        """Create default configuration."""
        return cls(
            coordinator_url="wss://api.getrem.online/miners_ws",
            data_dir="~/.dvm_miner",
            node_id="",
            max_ram_gb=4,
            embedding_dim=384,
            index_version=1,
            miner_secret="xuLHbzL7awVGHe-PQpAmwRuVJodUtwFRKGhSnAKS8pQ",
            sui_address="",
            referral_address="f5e3a292-b3fc-480e-93c6-b475cffd6c18"
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def load_config(path: Path) -> MinerConfig:
    """Load configuration from JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, "r") as f:
        data = json.load(f)
    
    # Generate node_id if missing
    if not data.get("node_id"):
        data["node_id"] = str(uuid.uuid4())
    
    # Set default referral_address if missing (for backward compatibility)
    if not data.get("referral_address"):
        data["referral_address"] = "f5e3a292-b3fc-480e-93c6-b475cffd6c18"
    
    # Only keep fields that exist in MinerConfig (ignore extra fields from old configs)
    config_fields = {
        'coordinator_url', 'data_dir', 'node_id', 'max_ram_gb', 
        'embedding_dim', 'index_version', 'miner_secret', 
        'sui_address', 'referral_address'
    }
    filtered_data = {k: v for k, v in data.items() if k in config_fields}
    
    return MinerConfig(**filtered_data)


def save_config(config: MinerConfig, path: Path):
    """Save configuration to JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Expand ~ in data_dir
    config_dict = config.to_dict()
    if config_dict["data_dir"].startswith("~"):
        config_dict["data_dir"] = str(Path(config_dict["data_dir"]).expanduser())
    
    with open(path, "w") as f:
        json.dump(config_dict, f, indent=2)

