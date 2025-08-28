from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(
    title="RAG Chatbot API",
    description="A RAG chatbot using Google Gemini AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll restrict this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ModelName(str, Enum):
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_2_5_FLASH = "gemini-2.0-flash-exp"

class QueryInput(BaseModel):
    question: str
    session_id: str = "default"
    model: ModelName = ModelName.GEMINI_2_5_FLASH

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "api_key_configured": bool(GOOGLE_API_KEY)}

@app.post("/query", response_model=QueryResponse)
async def query_chatbot(query_input: QueryInput):
    try:
        if not GOOGLE_API_KEY:
            raise HTTPException(status_code=500, detail="Google API key not configured")
        
        # Select model based on input
        model_name = query_input.model.value
        model = genai.GenerativeModel(model_name)
        
        # Create a more detailed prompt for better responses
        prompt = f"""You are a helpful AI assistant. Please provide a comprehensive and informative response to the following question:

Question: {query_input.question}

Please provide a detailed answer that is:
- Accurate and informative
- Well-structured and easy to understand
- Helpful for the user's needs

Answer:"""
        
        # Generate response
        response = model.generate_content(prompt)
        
        return QueryResponse(
            answer=response.text,
            session_id=query_input.session_id,
            model=query_input.model
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# For Vercel serverless deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
