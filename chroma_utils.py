from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Text splitter configuration
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)

# Global variables for lazy initialization
vectorstore = None
_embedding_function = None

class SimpleTfidfEmbeddings:
    """Simple TF-IDF based embeddings that work offline"""
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=384,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1
        )
        self.fitted = False
        self.dimension = 384
    
    def _ensure_fitted(self, texts):
        """Ensure the vectorizer is fitted"""
        if not self.fitted and texts:
            self.vectorizer.fit(texts)
            self.fitted = True
    
    def embed_documents(self, texts):
        """Embed multiple documents"""
        if not texts:
            return []
        
        self._ensure_fitted(texts)
        
        try:
            vectors = self.vectorizer.transform(texts)
            dense_vectors = vectors.toarray()
            
            # Pad or truncate to fixed dimension
            result = []
            for vector in dense_vectors:
                if len(vector) < self.dimension:
                    padded = np.zeros(self.dimension)
                    padded[:len(vector)] = vector
                    result.append(padded.tolist())
                else:
                    result.append(vector[:self.dimension].tolist())
            
            return result
        except Exception as e:
            print(f"Error in embed_documents: {e}")
            return [[0.0] * self.dimension for _ in texts]
    
    def embed_query(self, text):
        """Embed a single query"""
        return self.embed_documents([text])[0]

def get_embedding_function():
    """Get embedding function for ChromaDB"""
    global _embedding_function
    
    if _embedding_function is not None:
        return _embedding_function
    
    print("Initializing embeddings...")
    
    # Use simple TF-IDF embeddings for reliability
    _embedding_function = SimpleTfidfEmbeddings()
    print("✅ TF-IDF embeddings initialized successfully!")
    return _embedding_function

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
        print("✅ ChromaDB vectorstore initialized successfully!")
        return vectorstore
    except Exception as e:
        print(f"❌ Error initializing vectorstore: {e}")
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
        print(f"✅ Successfully indexed {filename} with {len(splits)} chunks")
        return True
    except Exception as e:
        print(f"❌ Error indexing document: {e}")
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
            print(f"✅ Successfully deleted all documents with file_id {file_id}")
            return True
        else:
            print(f"⚠️ No documents found for file_id {file_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting document with file_id {file_id} from Chroma: {str(e)}")
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
        
        print(f"✅ Search returned {len(documents)} results")
        return formatted_results
        
    except Exception as e:
        print(f"❌ Error searching vectorstore: {e}")
        return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}

# For compatibility with existing code
def extract_text_from_file(file_path: str) -> str:
    """Extract text from file (legacy function for compatibility)"""
    try:
        splits = load_and_split_document(file_path)
        return "\n\n".join([doc.page_content for doc in splits])
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        raise
