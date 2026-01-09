"""MongoDB connection management module.

This module provides the MongoConnectionManager class which handles database connections
and implements the singleton pattern to ensure efficient connection reuse throughout
the application. It manages connection pooling and provides context managers for
safe database operations.
"""

import logging
import re
from contextlib import asynccontextmanager
from typing import Optional

import motor.motor_asyncio

from app.config import get_settings

# Set up logging
logger = logging.getLogger(__name__)


def sanitize_mongodb_uri_for_logging(uri: str) -> str:
    """Remove credentials from URI for safe logging."""
    return re.sub(r'://([^:]+):([^@]+)@', '://***:***@', uri)


def get_secure_mongodb_config():
    """Get secure MongoDB configuration from settings."""
    settings = get_settings()

    if not settings.mongodb_uri:
        raise ValueError("MONGODB_URI not configured")

    return {
        "uri": settings.mongodb_uri,
        "database": settings.database_name
    }


# Initialize configuration
config = get_secure_mongodb_config()
MONGODB_URI = config["uri"]
MONGODB_DB = config["database"]

# Log securely
logger.info(f"MongoDB URI initialized: {sanitize_mongodb_uri_for_logging(MONGODB_URI)}")


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

    # Determine if TLS should be enabled
    USE_TLS = "mongodb+srv" in MONGODB_URI

    MONGO_CONFIG = {
        "maxPoolSize": 10,  # Reduced for security
        "minPoolSize": 1,
        "maxIdleTimeMS": 30000,  # Reduced idle time
        "waitQueueTimeoutMS": 5000,
        "serverSelectionTimeoutMS": 5000,
        "retryWrites": True,
        "retryReads": True,
    }

    # Add TLS settings only when TLS is enabled
    if USE_TLS:
        MONGO_CONFIG.update({
            "tls": True,
            "tlsAllowInvalidCertificates": False,  # Strict certificate validation for production
        })

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

        Raises:
            ConnectionError: If connection to MongoDB fails
        """
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(
            MONGODB_URI, **self.MONGO_CONFIG
        )

            # Test connection
            await client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB: {sanitize_mongodb_uri_for_logging(MONGODB_URI)}")

            return client

        except Exception as e:
            logger.error("Failed to connect to MongoDB")
            # Don't log the full URI which might contain credentials
            raise ConnectionError("Database connection failed") from e

    def get_client(self) -> motor.motor_asyncio.AsyncIOMotorClient:
        """Get the MongoDB client instance, creating it if it doesn't exist.
        Uses connection pooling for better performance.

        Returns:
            AsyncIOMotorClient: MongoDB motor client for asynchronous operations

        Note:
            This method creates a synchronous client. For async operations,
            use _get_client() instead.
        """
        if self._client is None:
            try:
                self._client = motor.motor_asyncio.AsyncIOMotorClient(
                    MONGODB_URI, **self.MONGO_CONFIG
                )
                logger.info(f"MongoDB client created: {sanitize_mongodb_uri_for_logging(MONGODB_URI)}")
            except Exception as e:
                logger.error("Failed to create MongoDB client")
                raise ConnectionError("Database client creation failed") from e

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
