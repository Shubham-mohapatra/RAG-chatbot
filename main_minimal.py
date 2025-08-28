"""
Extremely simplified version of the RAG chatbot that doesn't use complex dependencies
This is a fallback option if the regular main.py doesn't work with Render
"""
import os
import logging
import json
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
try:
    import google.generativeai as genai
except ImportError:
    print("WARNING: google.generativeai module not found")
    genai = None
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
    return {"status": "OK", "message": "RAG Chatbot API is running (Minimal Version)"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "minimal"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    try:
        if not genai:
            return {
                "response": "Google Generative AI module not available. Please check your configuration.",
                "sources": []
            }
            
        # Configure the model
        if not GOOGLE_API_KEY:
            return {
                "response": "GOOGLE_API_KEY environment variable is not set.",
                "sources": []
            }
            
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate a response
        response = model.generate_content(message)
        
        return {
            "response": response.text,
            "sources": []
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return {
            "response": f"Error: {str(e)}",
            "error": True,
            "sources": []
        }

if __name__ == "__main__":
    uvicorn.run("main_minimal:app", host="0.0.0.0", port=8000, reload=True)
