import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


async def migrate():
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(uri)

    src_db = client["myresumo"]
    dst_db = client["powercv"]

    # 1. Copy resumes and update user_id
    resumes_col = src_db["resumes"]
    dst_resumes_col = dst_db["resumes"]

    async for resume in resumes_col.find():
        # Update user_id if it's temp-user-id
        if resume.get("user_id") == "temp-user-id":
            resume["user_id"] = "local-user"

        # Check if already exists in dst
        exists = await dst_resumes_col.find_one({"_id": resume["_id"]})
        if not exists:
            await dst_resumes_col.insert_one(resume)
            print(f"Migrated resume: {resume.get('title')}")
        else:
            # Update existing one just in case
            await dst_resumes_col.replace_one({"_id": resume["_id"]}, resume)
            print(f"Updated resume: {resume.get('title')}")

    # 2. Also check cover letters if they exist
    collections = await src_db.list_collection_names()
    if "cover_letters" in collections:
        cl_col = src_db["cover_letters"]
        dst_cl_col = dst_db["cover_letters"]
        async for cl in cl_col.find():
            if cl.get("user_id") == "temp-user-id":
                cl["user_id"] = "local-user"
            exists = await dst_cl_col.find_one({"_id": cl["_id"]})
            if not exists:
                await dst_cl_col.insert_one(cl)
                print(f"Migrated cover letter: {cl.get('title', 'Untitled')}")
            else:
                await dst_cl_col.replace_one({"_id": cl["_id"]}, cl)

    print("Migration complete.")

if __name__ == "__main__":
    asyncio.run(migrate())
