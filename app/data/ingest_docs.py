import os
import uuid
import logging
from qdrant_client import QdrantClient
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models for Hybrid Search
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
SPARSE_MODEL_NAME = "prithivida/Splade_PP_en_v1"
QDRANT_PATH = "./qdrant_db"
COLLECTION_NAME = "financial_policies"
DOCS_DIR = "./docs"

class SafePyPDFLoader(PyPDFLoader):
    """Custom loader that catches and ignores corrupted PDF errors."""
    def load(self):
        try:
            return super().load()
        except Exception as e:
            logger.warning(f"Failed to load PDF {self.file_path}: {e}")
            return []
            
    def lazy_load(self):
        try:
            yield from super().lazy_load()
        except Exception as e:
            logger.warning(f"Failed to lazy load PDF {self.file_path}: {e}")
            yield from []

def ingest_documents():
    logger.info(f"Connecting to Local QdrantDB at {QDRANT_PATH}...")
    client = QdrantClient(path=QDRANT_PATH)
    
    logger.info(f"Setting Models: Dense={EMBEDDING_MODEL_NAME}, Sparse={SPARSE_MODEL_NAME}")
    client.set_model(EMBEDDING_MODEL_NAME)
    client.set_sparse_model(SPARSE_MODEL_NAME)
    
    logger.info(f"Resetting collection: {COLLECTION_NAME} (enabling Hybrid Search)")
    try:
        client.delete_collection(collection_name=COLLECTION_NAME)
        logger.info("Deleted old collection.")
    except Exception:
        pass 
        
    try:
        # Create fresh collection with Hybrid Search capabilities
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=client.get_fastembed_vector_params(),
            sparse_vectors_config=client.get_fastembed_sparse_vector_params()
        )
        logger.info("Created new Hybrid-ready collection.")
    except Exception as e:
        logger.error(f"Collection setup error: {e}")
        return
    
    logger.info(f"Crawling directory {DOCS_DIR} for PDF documents...")
    if not os.path.exists(DOCS_DIR):
        logger.error(f"Directory {DOCS_DIR} does not exist. Please place PDFs there.")
        return

    loader = DirectoryLoader(
        DOCS_DIR, 
        glob="**/*.pdf", 
        loader_cls=SafePyPDFLoader,
        show_progress=True
    )
    
    documents = loader.load()
    logger.info(f"Loaded {len(documents)} pages from PDFs.")
    
    if not documents:
        logger.warning(f"No PDFs found in {DOCS_DIR}. Nothing to ingest.")
        return

    logger.info("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunks.")
    
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    
    logger.info("Uploading chunks to Qdrant (Computing Dense + Sparse embeddings)...")
    
    batch_size = 25
    for i in range(0, len(texts), batch_size):
        end = min(i + batch_size, len(texts))
        # .add() automatically uses the models set in set_model and set_sparse_model
        client.add(
            collection_name=COLLECTION_NAME,
            documents=texts[i:end],
            metadata=metadatas[i:end],
            ids=ids[i:end]
        )
        logger.info(f"Uploaded batch {(i//batch_size) + 1} ({end}/{len(texts)} chunks)")
    
    logger.info(f"Successfully ingested {len(chunks)} chunks with Hybrid Indexing.")
    
    # Test retrieval
    logger.info("Testing Hybrid retrieval for: 'unauthorized transaction liability'")
    results = client.query(
        collection_name=COLLECTION_NAME,
        query_text="unauthorized transaction liability",
        limit=2
    )
    for res in results:
        logger.info(f"\n--- MATCH (Score: {res.score}) ---")
        logger.info(f"Source: {res.metadata.get('source', 'Unknown')}")
        logger.info(f"Snippet: {res.document[:200]}...\n")

if __name__ == "__main__":
    ingest_documents()
