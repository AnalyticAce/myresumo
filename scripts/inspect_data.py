import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


async def inspect():
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(uri)
    db = client.powercv
    col = db.resumes

    doc = await col.find_one()
    if doc:
        print("Fields in resume:")
        for k, v in doc.items():
            print(f"- {k}: {type(v)}")
    else:
        print("No resumes found in powercv.")

if __name__ == "__main__":
    asyncio.run(inspect())
