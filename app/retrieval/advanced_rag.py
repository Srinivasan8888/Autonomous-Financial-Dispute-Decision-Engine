import os
import warnings
from qdrant_client import QdrantClient

warnings.filterwarnings("ignore", category=UserWarning, module="qdrant_client")

# Models for Hybrid Search
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"
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
        # Initialize models for dense and sparse embeddings
        qdrant_client.set_model(EMBEDDING_MODEL_NAME)
        qdrant_client.set_sparse_model(SPARSE_MODEL_NAME)
        
        collections = qdrant_client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            qdrant_client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=qdrant_client.get_fastembed_vector_params(),
                sparse_vectors_config=qdrant_client.get_fastembed_sparse_vector_params()
            )
        return True
    except Exception as e:
        print(f"Failed to initialize Qdrant collection: {e}")
        return False

# Initialize on startup
is_ready = ensure_collection()

def retrieve_policies(query: str, top_k: int = 3) -> str:
    """
    Performs a Hybrid Search (Dense + Sparse) on the local QdrantDB.
    Returns a concatenated string of the most relevant policy documents.
    """
    if not is_ready or not qdrant_client:
        return "No DB Connection. Mock Policy: NPCI-ODR-Rule-5.2 - If transaction fails but debit occurs, auto-refund within T+1 days."
        
    try:
        # Hybrid Search: Qdrant automatically combines dense and sparse vectors
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
