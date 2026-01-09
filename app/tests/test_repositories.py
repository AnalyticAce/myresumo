"""Unit tests for database repositories."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from bson import ObjectId
from datetime import datetime
from app.database.repositories.base_repo import BaseRepository
from app.database.repositories.resume_repository import ResumeRepository
from app.database.repositories.cover_letter_repository import CoverLetterRepository
from app.database.models.resume import Resume, ResumeData, UserInformation, Skills
from app.database.models.cover_letter import CoverLetter, CoverLetterData


class MockAsyncIterator:
    """Helper for mocking async iterators."""

    def __init__(self, data):
        self.data = data
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.data):
            val = self.data[self.index]
            self.index += 1
            return val
        else:
            raise StopAsyncIteration


@pytest.fixture
def mock_collection():
    """Mock MongoDB collection."""
    mock = AsyncMock()
    # motor's find() and aggregate() are synchronous, they return a cursor
    mock.find = MagicMock()
    mock.aggregate = MagicMock()
    mock.count_documents = AsyncMock()
    mock.insert_one = AsyncMock()
    mock.update_one = AsyncMock()
    mock.delete_one = AsyncMock()
    mock.find_one = AsyncMock()
    return mock


@pytest.fixture
def mock_conn_manager(mock_collection):
    """Mock MongoConnectionManager globally."""
    with patch("app.database.connector.MongoConnectionManager.get_instance") as mock_get_instance:
        instance = MagicMock()
        mock_get_instance.return_value = instance

        ctx_manager = MagicMock()
        ctx_manager.__aenter__ = AsyncMock(return_value=mock_collection)
        ctx_manager.__aexit__ = AsyncMock(return_value=False)
        instance.get_collection.return_value = ctx_manager

        mock_client = MagicMock()
        instance.get_client.return_value = mock_client
        # For client[db][coll].find
        mock_client.__getitem__.return_value.__getitem__.return_value.find = MagicMock()

        yield instance


@pytest.mark.asyncio
class TestBaseRepository:
    async def test_find_one_success(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        doc_id = ObjectId()
        mock_collection.find_one.return_value = {"_id": doc_id, "name": "test"}
        result = await repo.find_one({"name": "test"})
        assert result["_id"] == str(doc_id)

    async def test_find_one_error(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_collection.find_one.side_effect = Exception("DB Error")
        result = await repo.find_one({"name": "test"})
        assert result is None

    async def test_find_success(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": ObjectId()}])
        mock_collection.find.return_value = mock_cursor
        result = await repo.find({"name": "test"})
        assert len(result) == 1

    async def test_find_error(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(side_effect=Exception("DB Error"))
        mock_collection.find.return_value = mock_cursor
        result = await repo.find({"name": "test"})
        assert result == []

    async def test_find_many_success(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": ObjectId()}])
        mock_collection.find.return_value = mock_cursor
        result = await repo.find_many({"name": "test"}, sort=[("created_at", -1)])
        assert len(result) == 1

    async def test_find_many_error(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_cursor = MagicMock()
        mock_cursor.to_list.side_effect = Exception("DB Error")
        mock_collection.find.return_value = mock_cursor
        result = await repo.find_many({})
        assert result == []

    async def test_insert_one_success(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        doc_id = ObjectId()
        mock_collection.insert_one.return_value = MagicMock(inserted_id=doc_id)
        result = await repo.insert_one({"name": "test"})
        assert result == str(doc_id)

    async def test_insert_one_error(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_collection.insert_one.side_effect = Exception("DB Error")
        result = await repo.insert_one({"name": "test"})
        assert result == ""

    async def test_update_one_error(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_collection.update_one.side_effect = Exception("DB Error")
        result = await repo.update_one({}, {})
        assert result is False

    async def test_delete_one_error(self, mock_conn_manager, mock_collection):
        repo = BaseRepository("test_db", "test_collection")
        mock_collection.delete_one.side_effect = Exception("DB Error")
        result = await repo.delete_one({})
        assert result is False


@pytest.mark.asyncio
class TestResumeRepository:
    @pytest.fixture
    def sample_resume_data(self):
        return ResumeData(
            user_information=UserInformation(
                name="Test", main_job_title="Engineer", profile_description="Desc",
                email="test@example.com", experiences=[], education=[], skills=Skills(hard_skills=[], soft_skills=[])
            )
        )

    @pytest.fixture
    def sample_resume(self):
        return Resume(user_id="u1", title="T1", original_content="C1", job_description="J1")

    async def test_create_resume(self, mock_conn_manager, mock_collection, sample_resume):
        repo = ResumeRepository("test_db")
        mock_collection.insert_one.return_value = MagicMock(
            inserted_id=ObjectId())
        result = await repo.create_resume(sample_resume)
        assert len(result) > 0

    async def test_get_resume_by_id_success(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        doc_id = ObjectId()
        mock_collection.find_one.return_value = {
            "_id": doc_id, "title": "Test"}
        result = await repo.get_resume_by_id(str(doc_id))
        assert result["title"] == "Test"

    async def test_get_resume_by_id_error(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        result = await repo.get_resume_by_id("invalid")
        assert result is None

    async def test_get_resumes_by_user_id(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(
            return_value=[{"_id": ObjectId(), "user_id": "user123"}])
        mock_collection.find.return_value = mock_cursor
        result = await repo.get_resumes_by_user_id("user123")
        assert len(result) == 1

    async def test_update_resume_success(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        result = await repo.update_resume(str(ObjectId()), {"title": "New"})
        assert result is True

    async def test_update_resume_error(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        mock_collection.update_one.side_effect = Exception("DB Error")
        result = await repo.update_resume(str(ObjectId()), {})
        assert result is False

    async def test_update_optimized_data_full(self, mock_conn_manager, mock_collection, sample_resume_data):
        repo = ResumeRepository("test_db")
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        result = await repo.update_optimized_data(
            str(ObjectId()), sample_resume_data, ats_score=85, original_ats_score=75,
            matching_skills=["Python"], missing_skills=["Java"], recommendation="Rec",
            score_improvement=10
        )
        assert result is True
        args, _ = mock_collection.update_one.call_args
        assert args[1]["$set"]["score_improvement"] == 10

    async def test_update_optimized_data_corrected(self, mock_conn_manager, mock_collection, sample_resume_data):
        repo = ResumeRepository("test_db")
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        # 70 < 80 -> corrected score = 80 + (80-70+5) = 93 (Wait, 80-70+5=15, 80+15=95. Error in my head?)
        # 80-70+5 = 15. 80+15 = 95.
        result = await repo.update_optimized_data(str(ObjectId()), sample_resume_data, 70, original_ats_score=80)
        assert result is True
        args, _ = mock_collection.update_one.call_args
        assert args[1]["$set"]["ats_score"] == 95

    async def test_update_optimized_data_error(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        mock_collection.update_one.side_effect = Exception("DB Error")
        result = await repo.update_optimized_data(str(ObjectId()), MagicMock(), 80)
        assert result is False

    async def test_delete_resume_success(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        result = await repo.delete_resume(str(ObjectId()))
        assert result is True

    async def test_delete_resume_error(self, mock_conn_manager, mock_collection):
        repo = ResumeRepository("test_db")
        mock_collection.delete_one.side_effect = Exception("DB Error")
        result = await repo.delete_resume(str(ObjectId()))
        assert result is False


@pytest.mark.asyncio
class TestCoverLetterRepository:
    @pytest.fixture
    def sample_cover_letter_data(self):
        return CoverLetterData(
            company_name="C", sender_name="S", sender_email="test@example.com", job_title="J",
            introduction="I", body_paragraphs=["P"], closing="Cl", signature="Sig"
        )

    @pytest.fixture
    def sample_cover_letter(self, sample_cover_letter_data):
        return CoverLetter(
            user_id="user123",
            title="Test CL",
            target_company="TechCorp",
            target_role="Software Engineer",
            job_description="Job Desc",
            content_data=sample_cover_letter_data
        )

    async def test_create_cover_letter_success(self, mock_conn_manager, mock_collection, sample_cover_letter):
        repo = CoverLetterRepository()
        mock_collection.insert_one.return_value = MagicMock(
            inserted_id=ObjectId())
        result = await repo.create_cover_letter(sample_cover_letter)
        assert len(result) > 0

    async def test_create_cover_letter_error(self, mock_conn_manager, mock_collection, sample_cover_letter):
        repo = CoverLetterRepository()
        mock_collection.insert_one.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to create cover letter"):
            await repo.create_cover_letter(sample_cover_letter)

    async def test_get_cover_letter_by_id_success(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        doc_id = ObjectId()
        mock_collection.find_one.return_value = {
            "_id": doc_id, "title": "Test"}
        result = await repo.get_cover_letter_by_id(str(doc_id))
        assert result["title"] == "Test"

    async def test_get_cover_letter_by_id_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.find_one.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to retrieve cover letter"):
            await repo.get_cover_letter_by_id(str(ObjectId()))

    async def test_get_cover_letters_by_user_id(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.__aiter__ = MagicMock(
            return_value=MockAsyncIterator([{"_id": ObjectId(), "user_id": "u1"}]))
        mock_client = mock_conn_manager.get_client.return_value
        mock_client.__getitem__.return_value.__getitem__.return_value.find.return_value = mock_cursor
        result = await repo.get_cover_letters_by_user_id("u1")
        assert len(result) == 1

    async def test_get_cover_letters_by_user_id_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_conn_manager.get_client.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to retrieve user cover letters"):
            await repo.get_cover_letters_by_user_id("u1")

    async def test_update_cover_letter_success(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        result = await repo.update_cover_letter(str(ObjectId()), {"title": "New"})
        assert result is True

    async def test_update_cover_letter_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.update_one.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to update cover letter"):
            await repo.update_cover_letter(str(ObjectId()), {})

    async def test_delete_cover_letter_success(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        result = await repo.delete_cover_letter(str(ObjectId()))
        assert result is True

    async def test_delete_cover_letter_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.delete_one.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to delete cover letter"):
            await repo.delete_cover_letter(str(ObjectId()))

    async def test_get_cover_letters_by_resume_id(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": ObjectId()}])
        mock_collection.find.return_value = mock_cursor
        result = await repo.get_cover_letters_by_resume_id("r1")
        assert len(result) == 1

    async def test_get_cover_letters_by_resume_id_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.find.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to retrieve cover letters for resume"):
            await repo.get_cover_letters_by_resume_id("r1")

    async def test_search_cover_letters(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor  # Chained call
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": ObjectId()}])
        mock_collection.find.return_value = mock_cursor
        result = await repo.search_cover_letters("u1", "q")
        assert len(result) == 1

    async def test_search_cover_letters_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.find.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to search cover letters"):
            await repo.search_cover_letters("u1", "q")

    async def test_get_cover_letter_statistics(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.count_documents.side_effect = [10, 5]
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[{"_id": "A", "count": 1}])
        mock_collection.aggregate.return_value = mock_cursor
        result = await repo.get_cover_letter_statistics("u1")
        assert result["total_cover_letters"] == 10

    async def test_get_cover_letter_statistics_error(self, mock_conn_manager, mock_collection):
        repo = CoverLetterRepository()
        mock_collection.count_documents.side_effect = Exception("E")
        with pytest.raises(Exception, match="Failed to get cover letter statistics"):
            await repo.get_cover_letter_statistics("u1")
