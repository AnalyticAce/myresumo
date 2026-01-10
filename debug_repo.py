
from app.database.repositories.base_repo import BaseRepository
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure we import from the local PowerCV
sys.path.insert(0, os.getcwd())


async def debug_find():
    mock_collection = AsyncMock()
    # Explicitly set search result to None if it were to succeed
    mock_collection.find.return_value = MagicMock()
    mock_collection.find.return_value.to_list = AsyncMock(return_value=None)

    # Try with exception
    mock_collection.find.side_effect = Exception("TEST_EXCEPTION")

    with patch("app.database.connector.MongoConnectionManager.get_instance") as mock_get_instance:
        instance = MagicMock()
        mock_get_instance.return_value = instance

        ctx_manager = MagicMock()
        ctx_manager.__aenter__ = AsyncMock(return_value=mock_collection)
        ctx_manager.__aexit__ = AsyncMock()
        instance.get_collection.return_value = ctx_manager

        repo = BaseRepository("test_db", "test_collection")
        print("DEBUG: calling find...")
        result = await repo.find({"name": "test"})
        print(f"DEBUG: result is {result}")
        return result

if __name__ == "__main__":
    asyncio.run(debug_find())
