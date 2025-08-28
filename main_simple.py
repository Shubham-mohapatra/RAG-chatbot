from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI(
    title="RAG Chatbot API",
    description="A simple RAG chatbot using Google Gemini AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class QueryInput(BaseModel):
    query: str
    model: str = "gemini-1.5-flash"

class QueryResponse(BaseModel):
    response: str
    model_used: str

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
        model_name = "gemini-1.5-flash" if query_input.model == "gemini-1.5-flash" else "gemini-1.5-pro"
        model = genai.GenerativeModel(model_name)
        
        # Generate response
        response = model.generate_content(query_input.query)
        
        return QueryResponse(
            response=response.text,
            model_used=model_name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
