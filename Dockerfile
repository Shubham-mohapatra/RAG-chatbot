# Backend Dockerfile for RAG Chatbot
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads chroma_db

# Expose port
EXPOSE 8080

# Health check - Extended start period for model download on first run
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run the application with Uvicorn so FastAPI binds to the correct port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
