# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for some Python C-extensions)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download HuggingFace model during build to cache it in the image
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Copy application source code
COPY . .

# Expose port
EXPOSE 8000

# Start command (Uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
