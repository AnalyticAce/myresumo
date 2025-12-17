"""MongoDB connection management module.

This module provides the MongoConnectionManager class which handles database connections
and implements the singleton pattern to ensure efficient connection reuse throughout
the application. It manages connection pooling and provides context managers for
safe database operations.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Optional

import motor.motor_asyncio
from app.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Build the MongoDB URI with database name
MONGODB_URI = f"{settings.MONGODB_URI.rstrip('/')}/{settings.MONGODB_DB}"

# Log the URI (masked) for debugging
masked_uri = MONGODB_URI.split("@")[-1] if "@" in MONGODB_URI else MONGODB_URI
logger.info(f"MongoDB URI: ...{masked_uri}")


class MongoConnectionManager:
    """Singleton class for managing MongoDB connections.

    This class implements the singleton pattern to ensure only one instance of the
    connection manager exists. It manages connection pooling to MongoDB and provides
    methods for retrieving and closing connections.

    Attributes:
        _instance: Class-level singleton instance reference
        _client: The shared motor AsyncIOMotorClient instance
    """

    _instance: Optional["MongoConnectionManager"] = None
    _client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None

    MONGO_CONFIG = {
        "maxPoolSize": 1000,
        "minPoolSize": 50,
        "maxIdleTimeMS": 45000,
        "waitQueueTimeoutMS": 10000,
        "serverSelectionTimeoutMS": 10000,
        "retryWrites": True,
    }

    @classmethod
    def get_instance(cls):
        """Get the singleton instance of MongoConnectionManager.

        Returns:
            MongoConnectionManager: The singleton instance
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        """Initialize the MongoDB connection manager."""
        if MongoConnectionManager._instance is not None and MongoConnectionManager._instance is not self:
            return  # Don't re-initialize if instance already exists

    async def _get_client(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Get an async MongoDB client instance.

        Returns:
            AsyncIOMotorClient: MongoDB motor client for asynchronous operations
        """
        return motor.motor_asyncio.AsyncIOMotorClient(
            MONGODB_URI, **self.MONGO_CONFIG
        )
        
    def get_client(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Get the MongoDB client instance, creating it if it doesn't exist.
        Uses connection pooling for better performance.

        Returns:
            AsyncIOMotorClient: MongoDB motor client for asynchronous operations
        """
        if self._client is None:
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                MONGODB_URI, **self.MONGO_CONFIG
            )
        return self._client

    async def close_all(self):
        """Close all active MongoDB connections.

        This method should be called during application shutdown to properly
        release all database connections.
        """
        if self._client is not None:
            self._client.close()
            self._client = None

    @asynccontextmanager
    async def get_collection(self, db_name: str, collection_name: str):
        """Get a MongoDB collection as an async context manager.

        Args:
            db_name: Name of the database
            collection_name: Name of the collection

        Yields:
            motor.motor_asyncio.AsyncIOMotorCollection: The requested collection

        Examples:
            ```python
            async with connection_manager.get_collection("mydb", "users") as collection:
                await collection.find_one({"email": "user@example.com"})
            ```
        """
        client = self.get_client()
        try:
            collection = client[db_name][collection_name]
            yield collection
        finally:
            pass
