#!/bin/bash
set -e  # Exit immediately if a command exits with non-zero status

echo "========== Starting Simplified Build Process =========="

# Create necessary directories
mkdir -p uploads
mkdir -p chroma_db

# Upgrade pip and install wheel
echo "Upgrading pip and installing wheel..."
pip install --upgrade pip
pip install wheel setuptools

# First install numpy explicitly to ensure we have the right version
echo "Installing numpy..."
pip install numpy==1.24.3

# Install all dependencies from the simplified requirements file
echo "Installing dependencies from requirements-simple.txt..."
pip install -r requirements-simple.txt

# Check installed packages
echo "Installed packages:"
pip list

echo "========== Build Process Completed =========="
