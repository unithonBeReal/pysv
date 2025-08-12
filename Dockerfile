# Use Python 3.11 slim image for production
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including ffmpeg for moviepy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for config and tasks
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Environment variables for production
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=8000
ENV DATA_PATH=/app/data
ENV CONFIG_FILE_PATH=/app/data/config.json

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/config || exit 1

# Use gunicorn for production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--keep-alive", "2", "--max-requests", "1000", "--max-requests-jitter", "50", "app:app"]
