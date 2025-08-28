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

# Install dependencies with forced binary packages
echo "Installing dependencies..."
pip install --no-build-isolation --no-cache-dir --prefer-binary -r requirements-backend.txt

# Check installed packages
echo "Installed packages:"
pip list

echo "========== Build Process Completed =========="
