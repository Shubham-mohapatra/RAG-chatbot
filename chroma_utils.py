from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import os

# Sentence Transformers import
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print(" sentence-transformers not available, will use basic embeddings")

# Text splitter configuration
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

# Global variables for lazy initialization
vectorstore = None
_embedding_function = None
_sentence_transformer_model = None  # Lazy-loaded model

def get_sentence_transformer_model(model_name="all-MiniLM-L6-v2"):
    """
    Lazy load Sentence Transformer model only when needed.
    This prevents model loading at startup, reducing memory usage and startup time.
    """
    global _sentence_transformer_model
    
    if _sentence_transformer_model is not None:
        return _sentence_transformer_model
    
    print(f"⚡ Lazy loading Sentence Transformer model: {model_name}...")
    
    try:
        import torch
        # Use CPU and optimize memory
        _sentence_transformer_model = SentenceTransformer(
            model_name,
            device='cpu',
            cache_folder='./models'
        )
        
        # Reduce memory footprint with half precision if available
        if hasattr(_sentence_transformer_model, 'half'):
            try:
                _sentence_transformer_model = _sentence_transformer_model.half()
                print("  Using FP16 (half precision) to save memory")
            except:
                print("  Using FP32 (full precision)")
        
        print(f"✅ Model loaded! Dimension: {_sentence_transformer_model.get_sentence_embedding_dimension()}")
        return _sentence_transformer_model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        raise

class SentenceTransformerEmbeddings:
    """
    Custom wrapper for Sentence Transformers with lazy loading.
    Model is only loaded when embed_documents() or embed_query() is first called.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None  # Model not loaded yet
    
    @property
    def model(self):
        """Lazy load model on first access"""
        if self._model is None:
            self._model = get_sentence_transformer_model(self.model_name)
        return self._model
    
    def embed_documents(self, texts):
        """Embed a list of documents (lazy loads model on first call)"""
        import torch
        with torch.no_grad():  # Disable gradient computation to save memory
            embeddings = self.model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=8,  # Smaller batch size to reduce memory
                convert_to_numpy=True
            )
        return embeddings.tolist()
    
    def embed_query(self, text):
        """Embed a single query"""
        import torch
        with torch.no_grad():
            embedding = self.model.encode(
                [text],
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True
            )[0]
        return embedding.tolist()

def get_embedding_function():
    """
    Get embedding function for ChromaDB using Sentence Transformers with lazy loading.
    Uses 'all-MiniLM-L6-v2' model which provides excellent semantic understanding
    while being fast and efficient (384 dimensions, ~80MB model).
    
    Model is NOT loaded at startup - it's loaded only when first needed.
    This reduces memory usage and startup time, perfect for Render deployment.
    """
    global _embedding_function
    
    if _embedding_function is not None:
        return _embedding_function
    
    print("⚡ Initializing Sentence Transformer embeddings (lazy loading enabled)...")
    print("   Model: all-MiniLM-L6-v2 (384 dimensions)")
    print("   Note: Model will load when first embedding is requested")
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError("sentence-transformers package not installed. Run: pip install sentence-transformers")
    
    try:
        # Create wrapper but don't load model yet
        _embedding_function = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
        print("✅ Embedding function ready (model will lazy load on first use)")
        print("   Benefits: Semantic search, context understanding, lower memory at startup")
        return _embedding_function
    except Exception as e:
        print(f"❌ Error initializing Sentence Transformers: {e}")
        raise

def get_vector_store():
    """Initialize and return the vectorstore"""
    global vectorstore
    
    if vectorstore is not None:
        return vectorstore
    
    try:
        embedding_function = get_embedding_function()
        data_dir = os.getenv("DATA_DIR", ".")
        persist_dir = os.path.join(data_dir, "chroma_db")
        os.makedirs(persist_dir, exist_ok=True)
        vectorstore = Chroma(
            persist_directory=persist_dir, 
            embedding_function=embedding_function
        )
        print("ChromaDB vectorstore initialized successfully!")
        return vectorstore
    except Exception as e:
        print(f" Error initializing vectorstore: {e}")
        raise

def load_and_split_document(file_path: str) -> List[Document]:
    """Load and split document based on file type"""
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    documents = loader.load()
    splits = text_splitter.split_documents(documents)
    return splits

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    """Index a document to ChromaDB"""
    try:
        vectorstore = get_vector_store()
        splits = load_and_split_document(file_path)
        
        # Add metadata to each split
        filename = os.path.basename(file_path)
        for i, split in enumerate(splits):
            split.metadata.update({
                'file_id': file_id,
                'filename': filename,
                'chunk_index': i,
                'total_chunks': len(splits),
                'source': file_path
            })
        
        vectorstore.add_documents(splits)
        print(f"Successfully indexed {filename} with {len(splits)} chunks")
        return True
    except Exception as e:
        print(f" Error indexing document: {e}")
        return False

def delete_doc_from_chroma(file_id: int) -> bool:
    """Delete a document from ChromaDB by file_id"""
    try:
        vectorstore = get_vector_store()
        
        # Get documents with the specific file_id
        docs = vectorstore.get(where={"file_id": file_id})
        
        if docs and docs.get('ids'):
            print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")
            
            # Delete using the IDs
            vectorstore.delete(ids=docs['ids'])
            print(f" Successfully deleted all documents with file_id {file_id}")
            return True
        else:
            print(f"No documents found for file_id {file_id}")
            return False
            
    except Exception as e:
        print(f" Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False

def search_vectorstore(collection, query: str, n_results: int = 4):
    """Search vectorstore for relevant documents"""
    try:
        vectorstore = get_vector_store()
        
        # Use vectorstore similarity search
        results = vectorstore.similarity_search(query, k=n_results)
        
        # Convert to format expected by the rest of the code
        documents = [doc.page_content for doc in results]
        metadatas = [doc.metadata for doc in results]
        distances = [0.5] * len(results)  # Placeholder distances
        
        formatted_results = {
            'documents': [documents],
            'metadatas': [metadatas],
            'distances': [distances]
        }
        
        print(f"Search returned {len(documents)} results")
        return formatted_results
        
    except Exception as e:
        print(f"Error searching vectorstore: {e}")
        return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

# For compatibility with existing code
def extract_text_from_file(file_path: str) -> str:
    """Extract text from file (legacy function for compatibility)"""
    try:
        splits = load_and_split_document(file_path)
        return "\n\n".join([doc.page_content for doc in splits])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        raise
