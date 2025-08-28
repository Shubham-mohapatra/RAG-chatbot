#!/bin/bash

# Create directories for uploads and chromaDB if they don't exist
mkdir -p uploads
mkdir -p chroma_db

# Install Python dependencies with preference for pre-built binaries
pip install --prefer-binary -r requirements-render.txt

# Initialize the database
python -c "import db_utils; db_utils.initialize_db()"

echo "Build completed successfully!"
