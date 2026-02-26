import json
import os
import chromadb
from chromadb.utils import embedding_functions

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
CHROMA_PATH = "./chroma_db"

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
    print(f"Initializing Local Embeddings: {EMBEDDING_MODEL_NAME}")
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    
    print(f"Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    collection_name = "financial_policies"
    
    print(f"Creating/getting collection: {collection_name}")
    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_func
    )
    
    print("Ingesting mock policies...")
    ids = [p["id"] for p in MOCK_POLICIES]
    documents = [p["text"] for p in MOCK_POLICIES]
    
    collection.upsert(
        ids=ids,
        documents=documents
    )
    
    print(f"Successfully ingested {len(MOCK_POLICIES)} policies into ChromaDB.")
    print("Test retrieval:")
    
    results = collection.query(
        query_texts=["unauthorized debit zero liability"],
        n_results=1
    )
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    ingest_documents()
