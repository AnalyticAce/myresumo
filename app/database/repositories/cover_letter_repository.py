"""Cover letter repository module.

This module implements the repository pattern for cover letter database operations.
It handles all CRUD operations, queries, and data persistence for cover letters.
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId

from app.database.connector import MongoConnectionManager
from app.database.models.cover_letter import CoverLetter, CoverLetterData
from app.database.repositories.base_repo import BaseRepository

# Set up logging
logger = logging.getLogger(__name__)


def get_db_name() -> str:
    """Get database name from environment or use default."""
    return os.getenv("MONGODB_DB", "powercv")


class CoverLetterRepository(BaseRepository):
    """Repository class for cover letter database operations.

    This class provides methods for creating, retrieving, updating, and deleting
    cover letter records in the database, as well as querying and filtering operations.
    """

    def __init__(self):
        """Initialize the cover letter repository with database connection."""
        self.connection_manager = MongoConnectionManager.get_instance()
        self.collection_name = "cover_letters"

    async def create_cover_letter(self, cover_letter: CoverLetter) -> Optional[str]:
        """Create a new cover letter in the database.

        Args:
            cover_letter: CoverLetter model instance to create

        Returns:
            The ID of the created cover letter, or None if creation failed

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()
            cover_letter_dict = cover_letter.model_dump()

            # Convert datetime objects to ISO format for MongoDB
            if "created_at" in cover_letter_dict:
                cover_letter_dict["created_at"] = cover_letter_dict["created_at"].isoformat(
                )
            if "updated_at" in cover_letter_dict:
                cover_letter_dict["updated_at"] = cover_letter_dict["updated_at"].isoformat(
                )

            # Convert content_data to dict
            if "content_data" in cover_letter_dict:
                cover_letter_dict["content_data"] = cover_letter_dict["content_data"].model_dump(
                )

            async with connection_manager.get_collection(get_db_name(), self.collection_name) as collection:
                result = await collection.insert_one(cover_letter_dict)
            return str(result.inserted_id) if result else None

        except Exception as e:
            raise Exception(f"Failed to create cover letter: {str(e)}")

    async def get_cover_letter_by_id(self, cover_letter_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a cover letter by its ID.

        Args:
            cover_letter_id: The ID of the cover letter to retrieve

        Returns:
            Cover letter data as dictionary, or None if not found

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()
            async with connection_manager.get_collection(get_db_name(), self.collection_name) as collection:
                result = await collection.find_one({"_id": ObjectId(cover_letter_id)})
                if result:
                    result["_id"] = str(result["_id"])
                return result

        except Exception as e:
            raise Exception(f"Failed to retrieve cover letter: {str(e)}")

    async def get_cover_letters_by_user_id(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all cover letters for a specific user.

        Args:
            user_id: The ID of the user whose cover letters to retrieve

        Returns:
            List of cover letter dictionaries

        Raises:
            Exception: If database operation fails
        """
        client = None
        try:
            db_name = os.getenv("MONGODB_DB", "powercv")

            # Get the async client from the connection manager
            connection_manager = MongoConnectionManager.get_instance()
            client = connection_manager.get_client()
            db = client[db_name]
            collection = db[self.collection_name]

            # Use async find with await
            cursor = collection.find(
                {"user_id": user_id}).sort("created_at", -1)

            # Convert cursor to list
            result = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                doc = dict(doc)  # Convert to dict to make it mutable
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                result.append(doc)

            return result

        except Exception as e:
            error_msg = f"Failed to retrieve user cover letters: {str(e)}"
            logger.error(error_msg)  # Use proper logging
            raise Exception(error_msg) from e

        finally:
            # Don't close the client - it's managed by singleton connection manager
            pass

    async def update_cover_letter(self, cover_letter_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing cover letter.

        Args:
            cover_letter_id: The ID of the cover letter to update
            update_data: Dictionary containing fields to update

        Returns:
            True if update was successful, False otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()

            # Add updated timestamp
            update_data["updated_at"] = datetime.now().isoformat()

            # Convert content_data if present
            if "content_data" in update_data and hasattr(update_data["content_data"], "model_dump"):
                update_data["content_data"] = update_data["content_data"].model_dump()

            async with connection_manager.get_collection("myresumo", self.collection_name) as collection:
                result = await collection.update_one(
                    {"_id": ObjectId(cover_letter_id)},
                    {"$set": update_data}
                )
            return result.modified_count > 0

        except Exception as e:
            raise Exception(f"Failed to update cover letter: {str(e)}")

    async def delete_cover_letter(self, cover_letter_id: str) -> bool:
        """Delete a cover letter by its ID.

        Args:
            cover_letter_id: The ID of the cover letter to delete

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()
            async with connection_manager.get_collection("myresumo", self.collection_name) as collection:
                result = await collection.delete_one({"_id": ObjectId(cover_letter_id)})
            return result.deleted_count > 0

        except Exception as e:
            raise Exception(f"Failed to delete cover letter: {str(e)}")

    async def get_cover_letters_by_resume_id(self, resume_id: str) -> List[Dict[str, Any]]:
        """Retrieve all cover letters associated with a specific resume.

        Args:
            resume_id: The ID of the resume to find associated cover letters for

        Returns:
            List of cover letter dictionaries

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()
            async with connection_manager.get_collection("myresumo", self.collection_name) as collection:
                cursor = collection.find(
                    {"resume_id": resume_id}).sort("created_at", -1)
                cover_letters = await cursor.to_list(length=None)
            return cover_letters or []

        except Exception as e:
            raise Exception(
                f"Failed to retrieve cover letters for resume: {str(e)}")

    async def search_cover_letters(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Search cover letters by text content.

        Args:
            user_id: The ID of the user whose cover letters to search
            query: Search query string

        Returns:
            List of matching cover letter dictionaries

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()
            search_filter = {
                "user_id": user_id,
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"target_company": {"$regex": query, "$options": "i"}},
                    {"target_role": {"$regex": query, "$options": "i"}},
                    {"generated_content": {"$regex": query, "$options": "i"}}
                ]
            }

            async with connection_manager.get_collection("myresumo", self.collection_name) as collection:
                cursor = collection.find(search_filter).sort("created_at", -1)
                cover_letters = await cursor.to_list(length=None)
            return cover_letters or []

        except Exception as e:
            raise Exception(f"Failed to search cover letters: {str(e)}")

    async def get_cover_letter_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about a user's cover letters.

        Args:
            user_id: The ID of the user

        Returns:
            Dictionary containing cover letter statistics

        Raises:
            Exception: If database operation fails
        """
        try:
            connection_manager = MongoConnectionManager.get_instance()

            async with connection_manager.get_collection("myresumo", self.collection_name) as collection:
                # Total cover letters
                total_count = await collection.count_documents({"user_id": user_id})

                # Generated cover letters
                generated_count = await collection.count_documents(
                    {"user_id": user_id, "is_generated": True}
                )

                # Cover letters by company
                pipeline = [
                    {"$match": {"user_id": user_id}},
                    {"$group": {"_id": "$target_company", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
                company_stats = await collection.aggregate(pipeline).to_list(length=None)

            return {
                "total_cover_letters": total_count,
                "generated_cover_letters": generated_count,
                "draft_cover_letters": total_count - generated_count,
                "top_companies": list(company_stats)
            }

        except Exception as e:
            raise Exception(f"Failed to get cover letter statistics: {str(e)}")
