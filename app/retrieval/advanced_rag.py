import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

# Initialize the local embedding model from HuggingFace
# This runs locally on CPU and costs $0
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

try:
    print(f"Loading local embedding model: {EMBEDDING_MODEL_NAME}")
    # chromadb built-in sentence-transformer wrapper
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    
    # Initialize local ChromaDB (Persistent storage in ./chroma_db folder)
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    collection_name = "financial_policies"
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_func
    )
except Exception as e:
    print(f"Failed to initialize ChromaDB or Embeddings: {e}")
    collection = None

def retrieve_policies(query: str, top_k: int = 3) -> str:
    """
    Performs a vector search on the local ChromaDB for the given query.
    Returns a concatenated string of the most relevant policy documents.
    """
    if not collection:
        return "No DB Connection. Mock Policy: NPCI-ODR-Rule-5.2 - If transaction fails but debit occurs, auto-refund within T+1 days."
        
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        extracted_docs = results.get('documents', [[]])[0]
        
        if not extracted_docs:
            return "No matching policies found in database."
            
        combined_context = "\n\n---\n\n".join(extracted_docs)
        return combined_context
        
    except Exception as e:
        print(f"Retrieval error: {e}")
        return f"Error retrieving policies: {str(e)}"
