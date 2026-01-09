import asyncio
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


async def check_db():
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(uri)
    db = client.powercv  # Use rebranded name or check old name

    # Try both names
    for db_name in ["powercv", "myresumo"]:
        db = client[db_name]
        try:
            collections = await db.list_collection_names()
            print(f"Database: {db_name}, Collections: {collections}")
            if "resumes" in collections:
                count = await db.resumes.count_documents({})
                print(f"Resumes count in {db_name}: {count}")
                if count > 0:
                    sample = await db.resumes.find_one()
                    print(
                        f"Sample resume from {db_name}: {sample.get('title')} for user {sample.get('user_id')}")
        except Exception as e:
            print(f"Error checking {db_name}: {e}")


if __name__ == "__main__":
    asyncio.run(check_db())
