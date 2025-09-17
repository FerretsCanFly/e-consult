"""Database configuration module for MongoDB connection."""

import os
import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

logger = logging.getLogger("database")

class DatabaseManager:
    """Async database connection manager met connection pooling."""
    
    def __init__(self):
        self._async_client: Optional[AsyncIOMotorClient] = None
        self._connection_lock = asyncio.Lock()
        self._health_check_interval = 300  # 5 minuten
        self._last_health_check = 0
        
    async def get_async_client(self) -> AsyncIOMotorClient:
        """Get or create async MongoDB client met connection pooling."""
        if self._async_client is not None:
            # Check if connection is still healthy
            if await self._is_connection_healthy():
                return self._async_client
        
        async with self._connection_lock:
            # Double-check pattern
            if self._async_client is not None and await self._is_connection_healthy():
                return self._async_client
                
            await self._create_async_connection()
            return self._async_client
    
    async def _create_async_connection(self) -> None:
        """Create new async MongoDB connection."""
        try:
            uri = self._get_mongodb_uri()
            
            # Connection pooling configuratie
            self._async_client = AsyncIOMotorClient(
                uri,
                maxPoolSize=50,           # Maximum connections in pool
                minPoolSize=5,            # Minimum connections in pool
                maxIdleTimeMS=30000,      # Close idle connections after 30s
                waitQueueTimeoutMS=10000,  # Wait max 10s for available connection
                connectTimeoutMS=30000,   # Connection timeout
                serverSelectionTimeoutMS=30000,  # Server selection timeout
                heartbeatFrequencyMS=20000,      # Health check frequency
                retryWrites=True
            )
            
            # Test connection
            await self._async_client.admin.command("ping")
            logger.info("✅ Async MongoDB connection pool created successfully")
            
        except Exception as e:
            logger.error("❌ Failed to create async MongoDB connection: %s", e)
            self._async_client = None
            raise
    
    async def _is_connection_healthy(self) -> bool:
        """Check if current connection is healthy."""
        current_time = asyncio.get_event_loop().time()
        
        # Rate limit health checks
        if current_time - self._last_health_check < self._health_check_interval:
            return True
        
        try:
            if self._async_client:
                await self._async_client.admin.command("ping")
                self._last_health_check = current_time
                return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False
        
        return False
    
    def _get_mongodb_uri(self) -> str:
        """Get MongoDB URI from environment."""
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI ontbreekt in .env")
        return uri
    
    async def close_connections(self) -> None:
        """Close all database connections."""
        if self._async_client:
            self._async_client.close()
            self._async_client = None
            logger.info("🛑 Async MongoDB connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions (backward compatibility)
async def get_async_mongo_client() -> AsyncIOMotorClient:
    """Get async MongoDB client from connection pool."""
    return await db_manager.get_async_client()

def get_mongodb_uri() -> str:
    """Get MongoDB URI from environment variables."""
    uri: str = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI ontbreekt in .env")
    return uri
