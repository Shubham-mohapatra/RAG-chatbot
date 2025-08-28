#!/bin/bash
set -e  # Exit immediately if a command exits with non-zero status

echo "========== Starting Custom Build Process =========="

# Create necessary directories
mkdir -p uploads
mkdir -p chroma_db

# Upgrade pip and install wheel
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel setuptools

# Set environment variables to avoid Rust compilation
export PIP_ONLY_BINARY=:all:
export HNSWLIB_NO_NATIVE=1
export CHROMADB_FORCE_DISABLE_COMPILE=1
export SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

# Install dependencies in two steps to avoid compatibility issues
echo "Installing core dependencies..."
pip install --no-build-isolation --no-cache-dir --prefer-binary fastapi==0.104.1 uvicorn==0.24.0 python-multipart==0.0.6 sqlalchemy==2.0.23 google-generativeai==0.3.2 python-dotenv==1.0.0 pydantic==1.10.8

echo "Installing ML dependencies..."
pip install --no-build-isolation --no-cache-dir --prefer-binary sentence-transformers==4.0.2

echo "Installing LangChain and ChromaDB..."
pip install --no-build-isolation --no-cache-dir --prefer-binary langchain==0.0.352 langchain-core==0.1.3 langchain-google-genai==0.0.6 langchain-community==0.0.16 chromadb==0.4.6

# Check installed packages
echo "Installed packages:"
pip list

echo "========== Build Process Completed =========="
