"""
Test suite for RAG Chatbot API
"""
import pytest
import requests
import json
from io import BytesIO

BASE_URL = "http://127.0.0.1:8000"

class TestRagChatbotAPI:
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_chat_endpoint_validation(self):
        """Test chat endpoint input validation"""
        # Test empty question
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"question": "", "model": "gemini-1.5-flash"}
        )
        assert response.status_code == 400
        
        # Test too long question
        long_question = "x" * 1001
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"question": long_question, "model": "gemini-1.5-flash"}
        )
        assert response.status_code == 400
    
    def test_chat_endpoint_valid(self):
        """Test chat endpoint with valid input"""
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"question": "Hello, how are you?", "model": "gemini-1.5-flash"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
    
    def test_list_docs_endpoint(self):
        """Test list documents endpoint"""
        response = requests.get(f"{BASE_URL}/list-docs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        files = {"file": ("test.txt", BytesIO(b"test content"), "text/plain")}
        response = requests.post(f"{BASE_URL}/upload-doc", files=files)
        assert response.status_code == 400
    
    def test_upload_no_file(self):
        """Test upload without file"""
        response = requests.post(f"{BASE_URL}/upload-doc")
        assert response.status_code == 422  # FastAPI validation error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
