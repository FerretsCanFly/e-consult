"""Vector search functionality for MongoDB with sentence transformers (Async only)."""

import logging
import asyncio
from typing import List
from sentence_transformers import SentenceTransformer
from motor.motor_asyncio import AsyncIOMotorCollection

from .encoder_manager import encoder_manager
from ..exceptions import (
    VectorSearchError,
    EncoderError,
    DatabaseError,
    ConfigurationError
)

logger = logging.getLogger("vector_search")


# =============================================================================
# ASYNCHRONOUS FUNCTIONS
# =============================================================================

async def perform_async_vector_search(
    collection: AsyncIOMotorCollection, 
    query: str, 
    search_index: str
) -> List[dict]:
    """Voer async vector similarity search uit."""
    logger.info("Voer async similarity search uit voor query: %s", query)
    
    try:
        # Get encoder from manager (geen nieuwe initialisatie!)
        try:
            encoder = await encoder_manager.get_encoder()
        except Exception as e:
            logger.error("Failed to get encoder: %s", e)
            raise EncoderError("Encoder initialization failed", str(e)) from e
        
        # Encode query in thread pool (CPU-intensive)
        try:
            loop = asyncio.get_event_loop()
            query_vector = await loop.run_in_executor(
                None,
                lambda: encoder.encode([query])[0].tolist()
            )
        except Exception as e:
            logger.error("Failed to encode query: %s", e)
            raise EncoderError("Query encoding failed", str(e)) from e
        
        # Get vector search configuration from environment
        try:
            from ..config import get_vector_search_config
            vector_config = get_vector_search_config()
        except Exception as e:
            logger.error("Failed to load vector search config: %s", e)
            raise ConfigurationError("Configuration loading failed", str(e)) from e
        
        # Perform vector search
        try:
            results_cursor = collection.aggregate([
                {
                    "$vectorSearch": {
                        "queryVector": query_vector,
                        "path": "content_vector",
                        "numCandidates": vector_config["num_candidates"],
                        "limit": vector_config["limit"],
                        "index": search_index,
                    }
                }
            ])
        except Exception as e:
            logger.error("Database aggregation failed: %s", e)
            raise DatabaseError("Vector search aggregation failed", str(e)) from e
        
        # Convert cursor to list
        try:
            results = []
            async for doc in results_cursor:
                results.append({k: str(v) for k, v in doc.items()})
        except Exception as e:
            logger.error("Failed to process search results: %s", e)
            raise DatabaseError("Result processing failed", str(e)) from e
        
        logger.info("Async similarity search voltooid: %d resultaten gevonden", len(results))
        return results
        
    except (EncoderError, DatabaseError, ConfigurationError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        logger.error("Unexpected error during vector search: %s", e)
        raise VectorSearchError("Unexpected vector search error", str(e)) from e
