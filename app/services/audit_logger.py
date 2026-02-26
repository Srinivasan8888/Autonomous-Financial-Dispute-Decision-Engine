from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from datetime import datetime, timezone

# Optional global client
client = None
db = None

if settings.MONGODB_URI:
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client.dispute_engine_db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

async def log_dispute(request_data: dict, decision_data: dict, run_id: str = None):
    """
    Asynchronously logs the exact input, output, and LLM trace ID to MongoDB.
    This ensures $0 infrastructure still has enterprise-grade auditability.
    """
    if db is None:
        print("MongoDB URI not configured. Skipping audit log.")
        return
        
    audit_document = {
        "timestamp": datetime.now(timezone.utc),
        "request": request_data,
        "decision": decision_data,
        "langfuse_trace_id": run_id, # Ties the DB row to the LLM observation trace
        "status": "completed"
    }
    
    try:
        await db.audit_logs.insert_one(audit_document)
    except Exception as e:
        print(f"Failed to insert audit log: {e}")
