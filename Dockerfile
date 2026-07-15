# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
# Prevent Python from writing pyc files and enable unbuffered output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all python application files (responder, index, and accuracy modules)
COPY *.py .
COPY .env .

# Copy data directory (contains both past_emails.json and evaluation_set.json)
COPY data ./data

# Create db directory for Chroma persistence
RUN mkdir -p db

# Health check - verifies the responder can initialize without crashing
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from responder import EmailResponder; EmailResponder()" || exit 1

# Default command - runs the main responder
CMD ["python", "responder.py"]
