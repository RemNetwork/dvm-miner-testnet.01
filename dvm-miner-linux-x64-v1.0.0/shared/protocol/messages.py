"""Protocol message models for coordinator-miner communication."""

import enum
from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field


class ErrorCode(str, enum.Enum):
    """Error codes for protocol errors."""
    STORAGE_FULL = "STORAGE_FULL"
    INDEX_CORRUPTED = "INDEX_CORRUPTED"
    UNKNOWN_COLLECTION = "UNKNOWN_COLLECTION"
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class RegisterMessage(BaseModel):
    """Miner registration message."""
    type: Literal["register"] = "register"
    node_id: str
    capacity_gb: int
    embedding_dim: int
    index_version: int
    secret: str
    sui_address: str  # Sui address for rewards (required in Phase 3)
    sui_signature: Optional[str] = None  # Optional signature (blockchain verifies at claim time)
    timestamp: Optional[int] = None  # Timestamp for replay protection
    referral_code: Optional[str] = None  # Optional referral code (referrer's node_id)
    
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class HeartbeatMessage(BaseModel):
    """Miner heartbeat message."""
    type: Literal["heartbeat"] = "heartbeat"
    node_id: str
    vectors_stored: int
    bytes_used: int
    timestamp: str  # ISO 8601
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class StoreRequest(BaseModel):
    """Request to store vectors on a miner."""
    type: Literal["store_request"] = "store_request"
    request_id: str
    collection_id: str
    shard_id: Optional[str] = None  # For sharded collections
    doc_ids: List[str]
    vectors_b64: str
    shape: Tuple[int, int]
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class StoreResponse(BaseModel):
    """Response from miner after storing vectors."""
    type: Literal["store_response"] = "store_response"
    request_id: str
    node_id: str
    stored_count: int
    status: Literal["ok", "full", "error"]
    error_message: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class SearchRequest(BaseModel):
    """Request to search vectors on a miner."""
    type: Literal["search_request"] = "search_request"
    request_id: str
    collection_id: str
    shard_id: Optional[str] = None  # For sharded collections
    query_b64: str
    shape: Tuple[int]
    top_k: int = 10
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class SearchResultItem(BaseModel):
    """Single search result item."""
    doc_id: str
    score: float


class SearchResponse(BaseModel):
    """Response from miner after searching."""
    type: Literal["search_response"] = "search_response"
    request_id: str
    node_id: str
    results: List[SearchResultItem]
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class ChallengeRequest(BaseModel):
    """PoRAM challenge request sent to miner."""
    type: Literal["challenge_request"] = "challenge_request"
    challenge_id: str
    epoch_seed: str  # hex encoded
    offsets: List[int]  # Byte offsets to challenge
    chunk_size: int  # Size of each chunk
    deadline_ms: int  # Response deadline in milliseconds
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class ChallengeResponse(BaseModel):
    """Miner's response to PoRAM challenge."""
    type: Literal["challenge_response"] = "challenge_response"
    challenge_id: str
    chunks: List[str]  # Base64 encoded data chunks
    response_time_ms: int  # Time taken to respond
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()


class ErrorResponse(BaseModel):
    """Error response message."""
    type: Literal["error"] = "error"
    request_id: Optional[str] = None
    node_id: Optional[str] = None
    error_code: ErrorCode
    error_message: str
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return self.model_dump_json()

