"""
Extremely simplified version of the RAG chatbot that doesn't use complex dependencies
This is a fallback option if the regular main.py doesn't work with Render
"""
import os
import logging
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not found in environment variables")
    GOOGLE_API_KEY = "your-api-key-here"  # Will fail but prevent startup errors

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize FastAPI app
app = FastAPI(title="Minimal RAG API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "OK", "message": "RAG Chatbot API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate a response
        response = model.generate_content(message)
        
        return {
            "response": response.text,
            "sources": []
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main_minimal:app", host="0.0.0.0", port=8000, reload=True)
