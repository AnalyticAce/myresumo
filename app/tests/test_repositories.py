"""Tests for database repositories."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
from bson import ObjectId

from app.database.repositories.base_repo import BaseRepository
from app.database.repositories.resume_repository import ResumeRepository


class TestBaseRepository:
    """Test BaseRepository class."""

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    def test_init(self, mock_manager):
        """Test repository initialization."""
        mock_manager.get_instance.return_value = MagicMock()
        repo = BaseRepository("test_db", "test_collection")
        assert repo.db_name == "test_db"
        assert repo.collection_name == "test_collection"

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_find_one_success(self, mock_manager):
        """Test successful document retrieval."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.find_one = AsyncMock(return_value={"_id": ObjectId(), "name": "test"})
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.find_one({"name": "test"})

        assert result is not None
        assert result["name"] == "test"
        assert "_id" in result

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_find_one_not_found(self, mock_manager):
        """Test document not found."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.find_one = AsyncMock(return_value=None)
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.find_one({"name": "nonexistent"})

        assert result is None

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_find_many_success(self, mock_manager):
        """Test multiple document retrieval."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        
        # Create a proper async cursor mock
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": ObjectId(), "name": "test1"},
            {"_id": ObjectId(), "name": "test2"}
        ])
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        
        # Make find() return the cursor directly
        mock_collection.find.return_value = mock_cursor
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.find_many({"status": "active"})

        assert len(result) == 2

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_insert_one_success(self, mock_manager):
        """Test document insertion."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_collection.insert_one = AsyncMock(return_value=mock_result)
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.insert_one({"name": "test"})

        assert result is not None
        assert len(result) > 0

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_update_one_success(self, mock_manager):
        """Test document update."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_collection.update_one = AsyncMock(return_value=mock_result)
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.update_one(
            {"_id": ObjectId()},
            {"$set": {"name": "updated"}}
        )

        assert result is True

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_delete_one_success(self, mock_manager):
        """Test document deletion."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_collection.delete_one = AsyncMock(return_value=mock_result)
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.delete_one({"_id": ObjectId()})

        assert result is True


class TestResumeRepository:
    """Test ResumeRepository class."""

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    def test_init(self, mock_manager):
        """Test resume repository initialization."""
        mock_manager.get_instance.return_value = MagicMock()
        repo = ResumeRepository()
        assert repo.collection_name == "resumes"

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_get_resume_by_id(self, mock_manager):
        """Test resume retrieval by ID."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.find_one = AsyncMock(return_value={"_id": ObjectId(), "title": "My Resume"})
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = ResumeRepository()
        result = await repo.get_resume_by_id(str(ObjectId()))

        assert result is not None
        assert result["title"] == "My Resume"

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_get_resumes_by_user_id(self, mock_manager):
        """Test resumes retrieval by user ID."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        
        # Create a proper async cursor mock
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"_id": ObjectId(), "title": "Resume 1"},
            {"_id": ObjectId(), "title": "Resume 2"}
        ])
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        
        # Make find() return the cursor directly
        mock_collection.find.return_value = mock_cursor
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = ResumeRepository()
        result = await repo.get_resumes_by_user_id("user123")

        assert len(result) == 2

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_update_resume(self, mock_manager):
        """Test resume update."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_collection.update_one = AsyncMock(return_value=mock_result)
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = ResumeRepository()
        result = await repo.update_resume(
            str(ObjectId()),
            {"title": "Updated Resume"}
        )

        assert result is True

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_delete_resume(self, mock_manager):
        """Test resume deletion."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_collection.delete_one = AsyncMock(return_value=mock_result)
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = ResumeRepository()
        result = await repo.delete_resume(str(ObjectId()))

        assert result is True


class TestRepositoryErrorHandling:
    """Test repository error handling."""

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_find_one_exception(self, mock_manager):
        """Test exception handling in find_one."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.find_one = AsyncMock(side_effect=Exception("Database error"))
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.find_one({"name": "test"})

        assert result is None

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_insert_one_exception(self, mock_manager):
        """Test exception handling in insert_one."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.insert_one = AsyncMock(side_effect=Exception("Database error"))
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.insert_one({"name": "test"})

        assert result == ""

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_update_one_exception(self, mock_manager):
        """Test exception handling in update_one."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.update_one = AsyncMock(side_effect=Exception("Database error"))
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.update_one({"_id": ObjectId()}, {"$set": {"name": "test"}})

        assert result is False

    @patch('app.database.repositories.base_repo.MongoConnectionManager')
    @pytest.mark.asyncio
    async def test_delete_one_exception(self, mock_manager):
        """Test exception handling in delete_one."""
        mock_instance = MagicMock()
        mock_collection = MagicMock()
        mock_collection.__aenter__ = AsyncMock(return_value=mock_collection)
        mock_collection.__aexit__ = AsyncMock(return_value=None)
        mock_collection.delete_one = AsyncMock(side_effect=Exception("Database error"))
        mock_instance.get_collection.return_value = mock_collection
        mock_manager.get_instance.return_value = mock_instance

        repo = BaseRepository("test_db", "test_collection")
        result = await repo.delete_one({"_id": ObjectId()})

        assert result is False
