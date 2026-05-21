import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

async def check_mongodb_logs():
    if not MONGODB_URI:
        print("Missing MONGODB_URI configuration.")
        return

    try:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client.dispute_engine_db
        
        cursor = db.audit_logs.find().sort("timestamp", -1).limit(2)
        async for doc in cursor:
            print(f"Log ID: {doc.get('_id')}")
            print(f"Timestamp: {doc.get('timestamp')}")
            print(f"Langfuse Trace ID: {doc.get('langfuse_trace_id')}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(check_mongodb_logs())
