"""Encoder manager for sentence transformer with singleton pattern."""

from typing import Optional
from sentence_transformers import SentenceTransformer
import asyncio
import logging

logger = logging.getLogger("encoder_manager")

class EncoderManager:
    """Singleton manager voor sentence transformer encoder."""
    
    _instance: Optional['EncoderManager'] = None
    _encoder: Optional[SentenceTransformer] = None
    _initialization_lock = asyncio.Lock()
    
    def __new__(cls) -> 'EncoderManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def get_encoder(self) -> SentenceTransformer:
        """Get or initialize encoder asynchronously."""
        if self._encoder is not None:
            return self._encoder
            
        async with self._initialization_lock:
            # Double-check pattern
            if self._encoder is not None:
                return self._encoder
                
            logger.info("🚀 Initializing sentence transformer encoder...")
            try:
                # Run in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                self._encoder = await loop.run_in_executor(
                    None, 
                    self._create_encoder
                )
                logger.info("✅ Encoder successfully initialized")
                return self._encoder
            except Exception as e:
                logger.error("❌ Encoder initialization failed: %s", e)
                raise
    
    def _create_encoder(self) -> SentenceTransformer:
        """Create encoder instance (runs in thread pool)."""
        model_name = "all-MiniLM-L6-v2"
        return SentenceTransformer(model_name)
    
    def is_initialized(self) -> bool:
        """Check if encoder is ready."""
        return self._encoder is not None

# Global instance
encoder_manager = EncoderManager()
