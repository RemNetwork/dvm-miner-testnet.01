"""Miner node implementation."""

import asyncio
import json
import signal
import sys
import time
import hashlib
import base64
from datetime import datetime
from pathlib import Path

import structlog
import ssl
import websockets
from websockets.exceptions import ConnectionClosed, InvalidURI

# Add shared protocol to path
_script_dir = Path(__file__).parent
_miner_dir = _script_dir.parent
# Try local shared first (in miner_clean/shared)
_local_shared = _miner_dir.parent / "shared"
# Try parent shared (in DVM/shared)
_repo_shared = _miner_dir.parent.parent / "shared"

if _local_shared.exists():
    # Use local shared module (self-contained)
    _repo_root = _miner_dir.parent
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
elif _repo_shared.exists():
    # Use parent shared module (if miner_clean is in DVM repo)
    _repo_root = _miner_dir.parent.parent
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))

from dvm_miner.config import MinerConfig
from dvm_miner.engine import VectorEngine
from shared.protocol.messages import (
    ChallengeRequest,
    ChallengeResponse,
    ErrorCode,
    ErrorResponse,
    HeartbeatMessage,
    RegisterMessage,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    StoreRequest,
    StoreResponse,
)
from shared.protocol.serialization import decode_query_vector, decode_vectors

logger = structlog.get_logger(__name__)


class MinerNode:
    """Miner node that connects to coordinator and handles requests."""
    
    def __init__(self, config: MinerConfig):
        """Initialize miner node."""
        self.config = config
        # Expand ~ in data_dir
        data_dir = Path(config.data_dir).expanduser() if config.data_dir.startswith("~") else Path(config.data_dir)
        self.engine = VectorEngine(
            data_dir=data_dir,
            embedding_dim=config.embedding_dim,
            max_ram_gb=config.max_ram_gb
        )
        self.websocket = None
        self.running = False
        self.heartbeat_task = None
        self.autosave_task = None
        
        # PoRAM: Allocate and pre-fill claimed RAM
        self.poram_memory = None
        self._initialize_poram_memory()
    
    def start(self):
        """Start the miner node with reconnect loop."""
        self.running = True
        self._shutdown_event = None
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal", signal=signum)
            self.running = False
            if self._shutdown_event:
                try:
                    loop = asyncio.get_event_loop()
                    if not loop.is_closed():
                        loop.call_soon_threadsafe(self._shutdown_event.set)
                except:
                    pass
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Main reconnect loop
        try:
            asyncio.run(self._run_loop())
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.shutdown()
    
    async def _run_loop(self):
        """Main async reconnect loop."""
        self._shutdown_event = asyncio.Event()
        
        while self.running:
            try:
                await self._connect_and_run()
            except Exception as e:
                logger.error("Connection error", error=str(e))
                if self.running:
                    logger.info("Reconnecting in 5 seconds...")
                    await asyncio.sleep(5)
            finally:
                if self.websocket:
                    try:
                        await self.websocket.close()
                    except:
                        pass
                    self.websocket = None
    
    async def _connect_and_run(self):
        """Connect to coordinator and run message loop."""
        urls = [url.strip() for url in self.config.coordinator_url.split(",")]
        
        for i, url in enumerate(urls):
            try:
                logger.info("Connecting to coordinator", url=url, attempt=i+1, total=len(urls))
                
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                async with websockets.connect(
                    url,
                    ssl=ssl_context,
                    close_timeout=10
                ) as ws:
                    self.websocket = ws
                    
                    try:
                        await self._run_session(ws)
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("Connection closed", url=url)
                        return
                    except Exception as e:
                        logger.error("Session error", error=str(e))
                        return
                    
                    return

            except (OSError, asyncio.TimeoutError, websockets.exceptions.InvalidURI) as e:
                logger.warning("Failed to connect to coordinator", url=url, error=str(e))
                continue
        
        raise Exception(f"Could not connect to any coordinator: {urls}")

    async def _run_session(self, ws):
        """Run the authenticated session with the coordinator."""
        try:
            # Send registration message (no signature needed - clean version)
            timestamp = int(time.time())
            register_msg = RegisterMessage(
                node_id=self.config.node_id,
                capacity_gb=self.config.max_ram_gb,
                embedding_dim=self.config.embedding_dim,
                index_version=self.config.index_version,
                secret=self.config.miner_secret,
                sui_address=self.config.sui_address,
                sui_signature=None,  # No signature in clean version
                timestamp=timestamp,
                referral_code=self.config.referral_address or None
            )
            await ws.send(register_msg.model_dump_json())
            logger.info("Sent registration message", node_id=self.config.node_id)
            
            # Wait for registration response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                response_dict = json.loads(response)
                
                if response_dict.get("type") == "error":
                    error_code = response_dict.get("error_code", "UNKNOWN")
                    error_message = response_dict.get("error_message", "Unknown error")
                    logger.error(
                        "Registration rejected by coordinator",
                        error_code=error_code,
                        error_message=error_message
                    )
                    await ws.close()
                    return
                
                # Registration successful
                logger.info("Registration successful! Connected to coordinator")
                
                # Display referral information prominently
                print("\n" + "="*60)
                print("✅ MINER REGISTERED SUCCESSFULLY!")
                print("="*60)
                print(f"Node ID: {self.config.node_id}")
                print("-" * 60)
                print("💰 EARN EXTRA REWARDS WITH REFERRALS!")
                print(f"Your Referral ID: {self.config.node_id}")
                print("")
                print("Share this ID with others to earn 10% of their mining rewards!")
                print("You'll receive 10% extra Rem tokens for life from each referral!")
                print("="*60 + "\n")
                
                # Save referral info to file
                self._save_referral_info()
                
            except asyncio.TimeoutError:
                logger.warning("No registration response received, assuming success")
            except websockets.exceptions.ConnectionClosed:
                logger.error("Connection closed during registration")
                return
            except Exception as e:
                logger.error("Error waiting for registration response", error=str(e))
                return
            
            # Start background tasks
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop(ws))
            self.autosave_task = asyncio.create_task(
                self.engine.autosave_loop(interval_seconds=300)
            )
            
            # Main message loop
            while self.running:
                try:
                    try:
                        raw_message = await asyncio.wait_for(
                            ws.recv(),
                            timeout=1.0
                        )
                        await self._handle_message(raw_message, ws)
                    except asyncio.TimeoutError:
                        if self._shutdown_event.is_set() or not self.running:
                            logger.info("Shutdown requested, breaking message loop")
                            break
                        continue
                except websockets.exceptions.ConnectionClosed:
                    logger.info("WebSocket connection closed")
                    break
                except asyncio.CancelledError:
                    logger.info("Message loop cancelled")
                    break
                except Exception as e:
                    error_str = str(e).lower()
                    if "ping" in error_str and "timeout" in error_str:
                        logger.debug("Protocol ping timeout, connection closed", error=str(e))
                        break
                    else:
                        logger.error("Error in message loop", error=str(e))
                        await asyncio.sleep(0.1)
                    
        finally:
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
            
            if self.autosave_task:
                self.autosave_task.cancel()
                try:
                    await self.autosave_task
                except asyncio.CancelledError:
                    pass
            
            self.websocket = None
    
    def _save_referral_info(self):
        """Save referral information to file."""
        try:
            data_dir = Path(self.config.data_dir).expanduser() if self.config.data_dir.startswith("~") else Path(self.config.data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)
            
            with open(data_dir / "referral_info.txt", "w") as f:
                f.write("DVM Miner Referral Information\n")
                f.write("==============================\n\n")
                f.write(f"Your Node ID: {self.config.node_id}\n")
                f.write(f"Your Referral ID: {self.config.node_id}\n\n")
                f.write("💰 EARN 10% EXTRA REM TOKENS FOR LIFE!\n\n")
                f.write("Share your Referral ID with others to earn 10% of their mining rewards!\n")
                f.write("This is a lifetime benefit - you'll receive 10% from all their future earnings!\n\n")
                f.write("How to use:\n")
                f.write(f"1. Share this ID: {self.config.node_id}\n")
                f.write("2. When someone sets up their miner, they enter your ID as referral\n")
                f.write("3. You automatically earn 10% bonus from their mining rewards\n")
                f.write("4. This benefit lasts for the lifetime of their mining activity!\n")
            
            logger.info(f"Referral info saved to {data_dir / 'referral_info.txt'}")
        except Exception as e:
            logger.warning(f"Could not save referral info file: {e}")
    
    async def _heartbeat_loop(self, ws):
        """Send periodic heartbeat messages."""
        while self.running and ws:
            try:
                await asyncio.sleep(30)
                
                if not self.running or not ws:
                    break
                
                try:
                    from websockets.protocol import State
                    if hasattr(ws, 'state') and ws.state != State.OPEN:
                        logger.debug("WebSocket not open, stopping heartbeat loop")
                        break
                except (AttributeError, ImportError):
                    if hasattr(ws, 'closed') and ws.closed:
                        logger.debug("WebSocket closed, stopping heartbeat loop")
                        break
                    
                heartbeat = HeartbeatMessage(
                    node_id=self.config.node_id,
                    vectors_stored=self.engine.get_total_vectors(),
                    bytes_used=self.engine.get_bytes_used(),
                    timestamp=datetime.utcnow().isoformat()
                )
                await ws.send(heartbeat.model_dump_json())
                logger.debug("Sent heartbeat")
            except websockets.exceptions.ConnectionClosed:
                logger.debug("Connection closed during heartbeat send")
                break
            except RuntimeError as e:
                if "closed" in str(e).lower() or "not connected" in str(e).lower():
                    logger.debug("Connection not available for heartbeat")
                    break
                raise
            except asyncio.CancelledError:
                break
            except Exception as e:
                error_str = str(e).lower()
                if "ping" in error_str and "timeout" in error_str:
                    logger.debug("Ping timeout detected")
                    break
                else:
                    logger.error("Error in heartbeat loop", error=str(e))
                    await asyncio.sleep(5)
    
    async def _handle_message(self, raw_message: str, ws):
        """Handle incoming message from coordinator."""
        try:
            message_dict = json.loads(raw_message)
            message_type = message_dict.get("type")
            
            if message_type == "store_request":
                response = await self._handle_store(message_dict)
                await ws.send(response.model_dump_json())
            elif message_type == "search_request":
                response = await self._handle_search(message_dict)
                await ws.send(response.model_dump_json())
            elif message_type == "challenge_request":
                response = await self._handle_challenge(message_dict)
                await ws.send(response.model_dump_json())
            else:
                logger.warning("Unknown message type", type=message_type)
                error = ErrorResponse(
                    request_id=message_dict.get("request_id"),
                    node_id=self.config.node_id,
                    error_code=ErrorCode.INVALID_MESSAGE,
                    error_message=f"Unknown message type: {message_type}"
                )
                await ws.send(error.model_dump_json())
        
        except Exception as e:
            logger.error("Error handling message", error=str(e))
            error = ErrorResponse(
                request_id=message_dict.get("request_id") if 'message_dict' in locals() else None,
                node_id=self.config.node_id,
                error_code=ErrorCode.INTERNAL_ERROR,
                error_message=str(e)
            )
            try:
                await ws.send(error.model_dump_json())
            except:
                pass
    
    async def _handle_store(self, message_dict: dict) -> StoreResponse:
        """Handle store request."""
        try:
            request = StoreRequest(**message_dict)
            vectors = decode_vectors(request.vectors_b64, request.shape)
            
            if not self.engine.can_accept(len(request.doc_ids)):
                return StoreResponse(
                    request_id=request.request_id,
                    node_id=self.config.node_id,
                    stored_count=0,
                    status="full",
                    error_message="Storage capacity exceeded"
                )
            
            await self.engine.add_vectors(
                request.collection_id,
                vectors,
                request.doc_ids,
                shard_id=request.shard_id
            )
            
            return StoreResponse(
                request_id=request.request_id,
                node_id=self.config.node_id,
                stored_count=len(request.doc_ids),
                status="ok"
            )
        except Exception as e:
            logger.error("Error in store handler", error=str(e))
            return StoreResponse(
                request_id=message_dict.get("request_id"),
                node_id=self.config.node_id,
                stored_count=0,
                status="error",
                error_message=str(e)
            )
    
    async def _handle_search(self, message_dict: dict) -> SearchResponse:
        """Handle search request."""
        try:
            request = SearchRequest(**message_dict)
            query_vector = decode_query_vector(request.query_b64, request.shape)
            k = getattr(request, 'top_k', 50)
            results = await self.engine.search(
                request.collection_id,
                query_vector,
                k=k,
                shard_id=request.shard_id
            )
            
            result_items = [
                SearchResultItem(doc_id=doc_id, score=score)
                for doc_id, score in results
            ]
            
            return SearchResponse(
                request_id=request.request_id,
                node_id=self.config.node_id,
                results=result_items
            )
        except Exception as e:
            logger.error("Error in search handler", error=str(e))
            return SearchResponse(
                request_id=message_dict.get("request_id"),
                node_id=self.config.node_id,
                results=[]
            )
    
    async def _handle_challenge(self, message_dict: dict) -> ChallengeResponse:
        """Handle PoRAM challenge request."""
        start_time = time.time()
        
        try:
            request = ChallengeRequest(**message_dict)
            
            logger.info(
                "Received PoRAM challenge",
                challenge_id=request.challenge_id,
                num_offsets=len(request.offsets),
                chunk_size_kb=f"{request.chunk_size / 1024:.0f}"
            )
            
            epoch_seed = bytes.fromhex(request.epoch_seed)
            chunks_b64 = []
            
            for offset in request.offsets:
                chunk_data = bytearray()
                current_offset = offset
                
                while len(chunk_data) < request.chunk_size:
                    seed_input = epoch_seed + current_offset.to_bytes(8, 'big')
                    hash_bytes = hashlib.sha256(seed_input).digest()
                    
                    remaining = request.chunk_size - len(chunk_data)
                    if remaining >= 32:
                        chunk_data.extend(hash_bytes)
                        current_offset += 32
                    else:
                        chunk_data.extend(hash_bytes[:remaining])
                        current_offset += remaining
                
                chunks_b64.append(base64.b64encode(bytes(chunk_data)).decode())
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            logger.info(
                "PoRAM challenge completed",
                challenge_id=request.challenge_id,
                response_time_ms=response_time_ms,
                num_chunks=len(chunks_b64)
            )
            
            return ChallengeResponse(
                challenge_id=request.challenge_id,
                chunks=chunks_b64,
                response_time_ms=response_time_ms
            )
        except Exception as e:
            logger.error("Error handling challenge", error=str(e))
            return ChallengeResponse(
                challenge_id=message_dict.get("challenge_id", "unknown"),
                chunks=[],
                response_time_ms=0
            )
    
    def _initialize_poram_memory(self):
        """Initialize PoRAM memory allocation."""
        claimed_bytes = self.config.max_ram_gb * 1024 * 1024 * 1024
        
        logger.info(
            "Initializing PoRAM memory allocation",
            claimed_gb=self.config.max_ram_gb,
            claimed_bytes=claimed_bytes
        )
        
        try:
            chunk_size = 1024 * 1024 * 1024  # 1GB chunks
            num_chunks = self.config.max_ram_gb
            
            allocated_chunks = []
            for chunk_idx in range(num_chunks):
                try:
                    logger.info(f"Allocating chunk {chunk_idx+1}/{num_chunks}")
                    chunk = bytearray(chunk_size)
                    
                    # Touch every 4KB page to force OS allocation
                    page_size = 4096
                    for offset in range(0, chunk_size, page_size):
                        chunk[offset] = (chunk_idx + offset) % 256
                    
                    allocated_chunks.append(chunk)
                    logger.info(f"✅ Chunk {chunk_idx+1}/{num_chunks} allocated")
                except MemoryError:
                    logger.error(
                        "FAILED to allocate claimed RAM",
                        claimed_gb=self.config.max_ram_gb,
                        allocated_gb=chunk_idx
                    )
                    raise RuntimeError(
                        f"Cannot allocate {self.config.max_ram_gb}GB - only {chunk_idx}GB available. "
                        f"Reduce max_ram_gb in config!"
                    )
            
            self.poram_memory = {
                'chunks': allocated_chunks,
                'chunk_size': chunk_size,
                'total_gb': num_chunks,
                'total_bytes': claimed_bytes
            }
            
            logger.info("✅ PoRAM memory allocation complete", allocated_gb=num_chunks)
        except Exception as e:
            logger.error("Failed to initialize PoRAM memory", error=str(e), claimed_gb=self.config.max_ram_gb)
            raise
    
    def shutdown(self):
        """Gracefully shutdown miner node."""
        logger.info("Shutting down miner node")
        self.running = False
        
        if hasattr(self, '_shutdown_event'):
            try:
                self._shutdown_event.set()
            except:
                pass
        
        try:
            self.engine.save_all()
        except Exception as e:
            logger.warning("Error saving indices", error=str(e))
        
        logger.info("Miner node shut down")

