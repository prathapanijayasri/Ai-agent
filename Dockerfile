# Use official slim Python runtime
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FLASK_PORT=5000 \
    FLASK_HOST=0.0.0.0

WORKDIR /app

# Install system dependencies needed for PyMuPDF and C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for Docker layer caching
COPY backend/requirements.txt /app/requirements.txt

# Install python dependencies with compatible versions
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and knowledge base
COPY backend /app/backend
COPY knowledge_base /app/knowledge_base

# Create directories for persistent chroma db storage and file uploads
RUN mkdir -p /app/chroma_db /app/backend/uploads

# Expose port
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Launch application
CMD ["python", "backend/app.py"]
