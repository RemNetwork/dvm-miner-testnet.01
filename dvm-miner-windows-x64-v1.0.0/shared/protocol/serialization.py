"""Vector serialization for WebSocket transport."""

import base64
from typing import Tuple

import numpy as np
import zstandard as zstd


def encode_vectors(vectors: np.ndarray) -> Tuple[str, Tuple[int, int]]:
    """
    Encode numpy float32 vectors for WebSocket transport.
    
    Args:
        vectors: numpy array of shape (n, dim) with dtype float32
        
    Returns:
        Tuple of (base64_string, (n, dim) shape)
    """
    # Ensure float32
    if vectors.dtype != np.float32:
        vectors = vectors.astype(np.float32)
    
    # Convert to bytes
    vector_bytes = vectors.tobytes()
    
    # Compress with zstandard
    compressor = zstd.ZstdCompressor()
    compressed = compressor.compress(vector_bytes)
    
    # Base64 encode
    b64_string = base64.b64encode(compressed).decode('ascii')
    
    return b64_string, vectors.shape


def decode_vectors(data_b64: str, shape: Tuple[int, int]) -> np.ndarray:
    """
    Decode base64 compressed vectors back to numpy array.
    
    Args:
        data_b64: Base64 encoded compressed vector data
        shape: Tuple of (n, dim) shape
        
    Returns:
        numpy array of shape (n, dim) with dtype float32
    """
    # Base64 decode
    compressed = base64.b64decode(data_b64)
    
    # Decompress with zstandard
    decompressor = zstd.ZstdDecompressor()
    vector_bytes = decompressor.decompress(compressed)
    
    # Convert back to numpy array
    vectors = np.frombuffer(vector_bytes, dtype=np.float32).reshape(shape)
    
    return vectors


def encode_query_vector(vector: np.ndarray) -> Tuple[str, Tuple[int]]:
    """
    Encode a single query vector (1D array) for WebSocket transport.
    
    Args:
        vector: numpy array of shape (dim,) with dtype float32
        
    Returns:
        Tuple of (base64_string, (dim,) shape)
    """
    # Ensure float32 and 1D
    if vector.dtype != np.float32:
        vector = vector.astype(np.float32)
    if vector.ndim != 1:
        raise ValueError(f"Query vector must be 1D, got shape {vector.shape}")
    
    # Convert to bytes
    vector_bytes = vector.tobytes()
    
    # Compress with zstandard
    compressor = zstd.ZstdCompressor()
    compressed = compressor.compress(vector_bytes)
    
    # Base64 encode
    b64_string = base64.b64encode(compressed).decode('ascii')
    
    return b64_string, vector.shape


def decode_query_vector(data_b64: str, shape: Tuple[int]) -> np.ndarray:
    """
    Decode base64 compressed query vector back to numpy array.
    
    Args:
        data_b64: Base64 encoded compressed vector data
        shape: Tuple of (dim,) shape
        
    Returns:
        numpy array of shape (dim,) with dtype float32
    """
    # Base64 decode
    compressed = base64.b64decode(data_b64)
    
    # Decompress with zstandard
    decompressor = zstd.ZstdDecompressor()
    vector_bytes = decompressor.decompress(compressed)
    
    # Convert back to numpy array
    vector = np.frombuffer(vector_bytes, dtype=np.float32).reshape(shape)
    
    return vector

