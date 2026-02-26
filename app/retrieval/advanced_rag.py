import os
from qdrant_client import QdrantClient

# Initialize the local embedding model using FastEmbed
# This runs locally on CPU and costs $0, avoids Microsoft C++ build tools issues on Windows.
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
COLLECTION_NAME = "financial_policies"

# Initialize local Qdrant disk DB
try:
    qdrant_client = QdrantClient(path="./qdrant_db")
except Exception as e:
    print(f"Warning: Failed to load Qdrant client: {e}")
    qdrant_client = None

def ensure_collection():
    if not qdrant_client: return False
    try:
        qdrant_client.set_model(EMBEDDING_MODEL_NAME)
        collections = qdrant_client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_client.get_fastembed_vector_params()
            )
        return True
    except Exception as e:
        print(f"Failed to initialize Qdrant collection: {e}")
        return False

# Initialize on startup
is_ready = ensure_collection()

def retrieve_policies(query: str, top_k: int = 3) -> str:
    """
    Performs a vector search on the local QdrantDB for the given query using FastEmbed.
    Returns a concatenated string of the most relevant policy documents.
    """
    if not is_ready or not qdrant_client:
        return "No DB Connection. Mock Policy: NPCI-ODR-Rule-5.2 - If transaction fails but debit occurs, auto-refund within T+1 days."
        
    try:
        results = qdrant_client.query(
            collection_name=COLLECTION_NAME,
            query_text=query,
            limit=top_k
        )
        
        if not results:
            return "No matching policies found in database."
            
        extracted_docs = [hit.document for hit in results]
        combined_context = "\n\n---\n\n".join(extracted_docs)
        return combined_context
        
    except Exception as e:
        print(f"Retrieval error: {e}")
        return f"Error retrieving policies: {str(e)}"
