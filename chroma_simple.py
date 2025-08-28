"""
ChromaDB adapter to use a version that works in Render's environment
"""
import os
import logging
from typing import List, Optional

# Attempt to import chromadb
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings
    logging.info("Successfully imported ChromaDB and embeddings")
except ImportError as e:
    logging.error(f"Failed to import ChromaDB: {e}")
    raise

# Constants
CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_vector_store():
    """Get a ChromaDB vector store with existing embeddings"""
    # Print debug info
    logging.info(f"Setting up ChromaDB with path: {CHROMA_PATH}")
    
    try:
        # Create embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        # Create or load the vector store
        if not os.path.exists(CHROMA_PATH):
            os.makedirs(CHROMA_PATH, exist_ok=True)
            logging.info(f"Created new ChromaDB directory at {CHROMA_PATH}")
            
        # Initialize ChromaDB with minimal settings
        vector_store = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
        )
        
        logging.info("ChromaDB initialized successfully")
        return vector_store
        
    except Exception as e:
        logging.error(f"Error initializing ChromaDB: {e}")
        raise
