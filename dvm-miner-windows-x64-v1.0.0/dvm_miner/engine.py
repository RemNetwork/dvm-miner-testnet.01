"""Vector engine with HNSW indices and per-shard support."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import hnswlib
import numpy as np
import structlog

logger = structlog.get_logger(__name__)


class VectorEngine:
    """Manages HNSW indices per collection with optional sharding support."""
    
    def __init__(self, data_dir: Path, embedding_dim: int, max_ram_gb: int):
        """
        Initialize vector engine.
        
        Args:
            data_dir: Directory for storing indices and data
            embedding_dim: Dimension of embedding vectors
            max_ram_gb: Maximum RAM usage in GB
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.embedding_dim = embedding_dim
        self.max_bytes = max_ram_gb * 1024**3
        
        # Per-shard storage: collection_id -> shard_id -> index
        # For backward compatibility: None shard_id = "default"
        self.indices: Dict[str, Dict[str, hnswlib.Index]] = {}
        self.id_maps: Dict[str, Dict[str, Dict[int, str]]] = {}  # collection -> shard -> internal_id -> doc_id
        self.next_ids: Dict[str, Dict[str, int]] = {}  # collection -> shard -> counter
        self.locks: Dict[str, Dict[str, asyncio.Lock]] = {}  # collection -> shard -> lock
        
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Load existing indices
        self.load_all()
        
        logger.info("VectorEngine initialized", sharding_enabled=True)
    
    def _normalize_shard_id(self, shard_id: Optional[str]) -> str:
        """Normalize shard_id for internal use."""
        return shard_id if shard_id else "default"
    
    async def _get_lock(self, collection_id: str, shard_id: Optional[str] = None) -> asyncio.Lock:
        """Get or create lock for a collection/shard."""
        normalized_shard = self._normalize_shard_id(shard_id)
        
        if collection_id not in self.locks:
            self.locks[collection_id] = {}
        if normalized_shard not in self.locks[collection_id]:
            self.locks[collection_id][normalized_shard] = asyncio.Lock()
        
        return self.locks[collection_id][normalized_shard]
    
    def get_total_vectors(self) -> int:
        """Get total number of vectors across all collections and shards."""
        total = 0
        for collection_shards in self.indices.values():
            for index in collection_shards.values():
                if index:
                    total += index.get_current_count()
        return total
    
    def get_bytes_used(self) -> int:
        """Get approximate bytes used by vectors."""
        total_vectors = self.get_total_vectors()
        return total_vectors * self.embedding_dim * 4  # 4 bytes per float32
    
    def can_accept(self, num_vectors: int) -> bool:
        """
        Check if engine can accept more vectors.
        
        Args:
            num_vectors: Number of vectors to add
            
        Returns:
            True if capacity allows
        """
        bytes_needed = num_vectors * self.embedding_dim * 4
        return self.get_bytes_used() + bytes_needed <= self.max_bytes
    
    async def add_vectors(
        self,
        collection_id: str,
        vectors: np.ndarray,
        doc_ids: List[str],
        shard_id: Optional[str] = None
    ):
        """
        Add vectors to a collection's index (optionally to a specific shard).
        
        Args:
            collection_id: Collection identifier
            vectors: numpy array of shape (n, dim) with dtype float32
            doc_ids: List of document IDs
            shard_id: Optional shard identifier (None for legacy non-sharded)
        """
        if vectors.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Vector dimension mismatch: {vectors.shape[1]} != {self.embedding_dim}"
            )
        
        if len(doc_ids) != vectors.shape[0]:
            raise ValueError(
                f"Doc IDs count mismatch: {len(doc_ids)} != {vectors.shape[0]}"
            )
        
        normalized_shard = self._normalize_shard_id(shard_id)
        lock = await self._get_lock(collection_id, shard_id)
        
        async with lock:
            # Ensure collection structure exists
            if collection_id not in self.indices:
                self.indices[collection_id] = {}
                self.id_maps[collection_id] = {}
                self.next_ids[collection_id] = {}
            
            # Create index if it doesn't exist for this shard
            if normalized_shard not in self.indices[collection_id]:
                index = hnswlib.Index(space="cosine", dim=self.embedding_dim)
                max_elements = 1000000  # Large initial capacity
                index.init_index(
                    max_elements=max_elements,
                    ef_construction=200,
                    M=16
                )
                index.set_ef(50)
                self.indices[collection_id][normalized_shard] = index
                self.id_maps[collection_id][normalized_shard] = {}
                self.next_ids[collection_id][normalized_shard] = 0
            
            index = self.indices[collection_id][normalized_shard]
            
            # Normalize vectors (L2 normalization for cosine similarity)
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1  # Avoid division by zero
            normalized_vectors = vectors / norms
            
            # Generate internal IDs
            start_id = self.next_ids[collection_id][normalized_shard]
            internal_ids = list(range(start_id, start_id + len(doc_ids)))
            
            # Add vectors in thread pool (hnswlib operations are CPU-bound)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                index.add_items,
                normalized_vectors,
                internal_ids
            )
            
            # Update id map
            for internal_id, doc_id in zip(internal_ids, doc_ids):
                self.id_maps[collection_id][normalized_shard][internal_id] = doc_id
            
            # Update counter
            self.next_ids[collection_id][normalized_shard] += len(doc_ids)
            
            logger.debug(
                "Added vectors",
                collection_id=collection_id,
                shard_id=normalized_shard,
                count=len(doc_ids)
            )
    
    async def search(
        self,
        collection_id: str,
        query_vector: np.ndarray,
        k: int,
        shard_id: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Search for similar vectors (optionally in a specific shard).
        
        Args:
            collection_id: Collection identifier
            query_vector: Query vector of shape (dim,) with dtype float32
            k: Number of results to return
            shard_id: Optional shard identifier (None for legacy non-sharded)
            
        Returns:
            List of (doc_id, score) tuples sorted by score descending
        """
        normalized_shard = self._normalize_shard_id(shard_id)
        
        if collection_id not in self.indices:
            return []
        
        if normalized_shard not in self.indices[collection_id]:
            return []
        
        if k <= 0:
            return []
        
        lock = await self._get_lock(collection_id, shard_id)
        async with lock:
            index = self.indices[collection_id][normalized_shard]
            
            if index.get_current_count() == 0:
                return []
            
            # Normalize query vector
            norm = np.linalg.norm(query_vector)
            if norm == 0:
                return []
            normalized_query = query_vector / norm
            
            # Search in thread pool
            loop = asyncio.get_event_loop()
            labels, distances = await loop.run_in_executor(
                self.executor,
                index.knn_query,
                normalized_query,
                min(k, index.get_current_count())  # Don't ask for more than exist
            )
            
            # Convert to results
            id_map = self.id_maps[collection_id][normalized_shard]
            results = []
            for label, distance in zip(labels[0], distances[0]):
                doc_id = id_map.get(int(label))
                if doc_id:
                    # Convert distance to similarity (1 - distance for cosine)
                    similarity = 1.0 - distance
                    results.append((doc_id, similarity))
            
            # Sort by score descending
            results.sort(key=lambda x: x[1], reverse=True)
            
            return results
    
    def save_collection(self, collection_id: str):
        """Save a collection's indices and mappings to disk (all shards)."""
        if collection_id not in self.indices:
            return
        
        collection_dir = self.data_dir / collection_id
        collection_dir.mkdir(parents=True, exist_ok=True)
        
        for shard_id, index in self.indices[collection_id].items():
            try:
                # Save index
                index_path = collection_dir / f"shard_{shard_id}.bin"
                index.save_index(str(index_path))
                
                # Save mappings
                map_data = {
                    "id_map": self.id_maps[collection_id][shard_id],
                    "next_id": self.next_ids[collection_id].get(shard_id, 0)
                }
                map_path = collection_dir / f"shard_{shard_id}_map.json"
                with open(map_path, "w") as f:
                    json.dump(map_data, f)
                
                logger.debug(
                    "Saved shard",
                    collection_id=collection_id,
                    shard_id=shard_id
                )
            except Exception as e:
                logger.error(
                    "Failed to save shard",
                    collection_id=collection_id,
                    shard_id=shard_id,
                    error=str(e)
                )
    
    def save_all(self):
        """Save all collections to disk."""
        for collection_id in list(self.indices.keys()):
            self.save_collection(collection_id)
        logger.info("Saved all collections", count=len(self.indices))
    
    def load_all(self):
        """Load all collections from disk (including per-shard indices)."""
        # Legacy: Load old format (*.bin files in root)
        for bin_path in self.data_dir.glob("*.bin"):
            collection_id = bin_path.stem
            
            try:
                # Load legacy format
                index = hnswlib.Index(space="cosine", dim=self.embedding_dim)
                index.load_index(str(bin_path))
                index.set_ef(50)
                
                # Store as "default" shard
                if collection_id not in self.indices:
                    self.indices[collection_id] = {}
                    self.id_maps[collection_id] = {}
                    self.next_ids[collection_id] = {}
                
                self.indices[collection_id]["default"] = index
                
                # Load mappings
                map_path = self.data_dir / f"{collection_id}_map.json"
                if map_path.exists():
                    with open(map_path, "r") as f:
                        map_data = json.load(f)
                    self.id_maps[collection_id]["default"] = {
                        int(k): v for k, v in map_data["id_map"].items()
                    }
                    self.next_ids[collection_id]["default"] = map_data.get("next_id", 0)
                else:
                    self.id_maps[collection_id]["default"] = {}
                    self.next_ids[collection_id]["default"] = 0
                
                logger.info(
                    "Loaded legacy collection",
                    collection_id=collection_id
                )
            except Exception as e:
                logger.error(
                    "Failed to load legacy collection",
                    collection_id=collection_id,
                    error=str(e)
                )
        
        # New format: Load per-collection directories with shards
        for collection_dir in self.data_dir.iterdir():
            if not collection_dir.is_dir():
                continue
            
            collection_id = collection_dir.name
            
            # Find all shard files
            for bin_path in collection_dir.glob("shard_*.bin"):
                shard_id = bin_path.stem.replace("shard_", "").replace(".bin", "")
                
                try:
                    # Load index
                    index = hnswlib.Index(space="cosine", dim=self.embedding_dim)
                    index.load_index(str(bin_path))
                    index.set_ef(50)
                    
                    if collection_id not in self.indices:
                        self.indices[collection_id] = {}
                        self.id_maps[collection_id] = {}
                        self.next_ids[collection_id] = {}
                    
                    self.indices[collection_id][shard_id] = index
                    
                    # Load mappings
                    map_path = collection_dir / f"shard_{shard_id}_map.json"
                    if map_path.exists():
                        with open(map_path, "r") as f:
                            map_data = json.load(f)
                        self.id_maps[collection_id][shard_id] = {
                            int(k): v for k, v in map_data["id_map"].items()
                        }
                        self.next_ids[collection_id][shard_id] = map_data.get("next_id", 0)
                    else:
                        self.id_maps[collection_id][shard_id] = {}
                        self.next_ids[collection_id][shard_id] = 0
                    
                    logger.info(
                        "Loaded shard",
                        collection_id=collection_id,
                        shard_id=shard_id
                    )
                except Exception as e:
                    logger.error(
                        "Failed to load shard",
                        collection_id=collection_id,
                        shard_id=shard_id,
                        error=str(e)
                    )
    
    async def autosave_loop(self, interval_seconds: int = 300):
        """Background task to periodically save all collections."""
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                self.save_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in autosave loop", error=str(e))

