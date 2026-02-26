import json
import os
from qdrant_client import QdrantClient

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
QDRANT_PATH = "./qdrant_db"
COLLECTION_NAME = "financial_policies"

MOCK_POLICIES = [
    {
        "id": "npci-odr-1.1",
        "text": "As per NPCI ODR guidelines for UPI, if a transaction fails but the customer's account is debited (double debit or failed transaction), the issuer bank must auto-reverse the transaction within T+1 days. Failure to do so incurs a penalty of Rs 100 per day."
    },
    {
        "id": "rbi-dpss-2.0",
        "text": "RBI circular on unauthorized transactions states: if a customer reports an unauthorized electronic payment within 3 working days, their liability is ZERO. The bank must credit the amount within 10 working days."
    },
    {
        "id": "merchant-risk-3.4",
        "text": "For ecommerce merchants, if a refund is initiated by the merchant but fails at the acquiring bank level, the acquiring bank is fully liable to manually process the refund via chargeback mechanism."
    },
    {
        "id": "npci-fraud-4.2",
        "text": "In cases of UPI fraud where the user proactively shared their OTP or UPI PIN, the customer bears the full liability until the loss is reported to the bank."
    }
]

def ingest_documents():
    print(f"Connecting to Local QdrantDB at {QDRANT_PATH}...")
    client = QdrantClient(path=QDRANT_PATH)
    
    print(f"Setting FastEmbed model: {EMBEDDING_MODEL_NAME}")
    client.set_model(EMBEDDING_MODEL_NAME)
    
    print(f"Creating/getting collection: {COLLECTION_NAME}")
    try:
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=client.get_fastembed_vector_params()
            )
    except Exception as e:
        print(f"Collection setup error: {e}")
    
    print("Ingesting mock policies...")
    ids = [i for i in range(len(MOCK_POLICIES))]
    documents = [p["text"] for p in MOCK_POLICIES]
    metadata = [{"source_id": p["id"]} for p in MOCK_POLICIES]
    
    client.add(
        collection_name=COLLECTION_NAME,
        documents=documents,
        metadata=metadata,
        ids=ids
    )
    
    print(f"Successfully ingested {len(MOCK_POLICIES)} policies into QdrantDB.")
    print("Test retrieval:")
    
    results = client.query(
        collection_name=COLLECTION_NAME,
        query_text="unauthorized debit zero liability",
        limit=1
    )
    print(results)

if __name__ == "__main__":
    ingest_documents()
