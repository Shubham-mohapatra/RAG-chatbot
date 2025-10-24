from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
import shutil
import uvicorn
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)
LOG_PATH = os.path.join(DATA_DIR, 'app.log')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO)


app = FastAPI(
    title="RAG Chatbot API",
    description="A production-ready RAG chatbot using Google Gemini AI and ChromaDB",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://rag-chatbot-frontend-bjj8.onrender.com",  # Your deployed frontend
        "https://www.smartdocs.com",  # Your custom domain
        "https://smartdocs.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to RAG Chatbot API! Visit /docs for API documentation."}

@app.get("/health")
def health_check():
    """Health check endpoint to verify server status"""
    try:
        from chroma_utils import get_vector_store
        vectorstore = get_vector_store()
        return {
            "status": "healthy",
            "vector_store": "connected",
            "embeddings": "initialized",
            "timestamp": str(datetime.now())
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": str(datetime.now())
        }

@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    # Validate input
    if not query_input.question or len(query_input.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if len(query_input.question) > 1000:
        raise HTTPException(status_code=400, detail="Question too long (max 1000 characters)")
    
    # Generate a proper session ID if none provided
    session_id = query_input.session_id if query_input.session_id and query_input.session_id != "string" else str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

    try:
        chat_history = get_chat_history(session_id)
        rag_chain = get_rag_chain(query_input.model.value)
        
        answer = rag_chain.invoke({
            "input": query_input.question,
            "chat_history": chat_history
        })['answer']
        
        insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
        logging.info(f"Session ID: {session_id}, AI Response: {answer}")
        return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)
        
    except Exception as e:
        error_msg = f"Error processing query: {str(e)}"
        logging.error(error_msg)
        print(f"Chat endpoint error: {error_msg}")  # Also print to console for debugging
        raise HTTPException(status_code=500, detail=f"An error occurred while processing your request: {str(e)}")

@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()

@app.post("/upload-doc")
def upload_document(file: UploadFile = File(...)):
    """Upload and index a document to the RAG system"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.html']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_extension} not supported. Allowed: {allowed_extensions}"
            )
        
        # Check file size (limit to 10MB)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = UPLOADS_DIR
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get actual file size and content type
        actual_file_size = os.path.getsize(file_path)
        content_type = file.content_type or "application/octet-stream"
        
        # Insert document record and get file_id
        file_id = insert_document_record(file.filename, actual_file_size, content_type)
        
        # Index document to ChromaDB
        success = index_document_to_chroma(file_path, file_id)
        
        if success:
            logging.info(f"Successfully uploaded and indexed: {file.filename} with file_id: {file_id}")
            return {
                "message": f"Successfully uploaded and indexed document: {file.filename}",
                "file_id": file_id,
                "filename": file.filename,
                "file_size": actual_file_size
            }
        else:
            # If indexing fails, delete the database record
            delete_document_record(file_id)
            os.remove(file_path)  # Also remove the uploaded file
            raise HTTPException(status_code=500, detail="Failed to index document to ChromaDB")
            
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logging.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    try:
        chroma_delete_success = delete_doc_from_chroma(request.file_id)

        if chroma_delete_success:
            db_delete_success = delete_document_record(request.file_id)
            if db_delete_success:
                return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
            else:
                raise HTTPException(status_code=500, detail=f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database.")
        else:
            raise HTTPException(status_code=500, detail=f"Failed to delete document with file_id {request.file_id} from Chroma.")
    except Exception as e:
        logging.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting RAG Chatbot server...")
    port = 8080  # Changed from 8000 to avoid conflicts
    print(f"Server will run on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
