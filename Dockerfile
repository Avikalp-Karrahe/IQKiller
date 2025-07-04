# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r iqkiller && useradd -r -g iqkiller iqkiller

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=iqkiller:iqkiller . .

# Create necessary directories
RUN mkdir -p /app/cache /app/logs && \
    chown -R iqkiller:iqkiller /app/cache /app/logs

# Switch to non-root user
USER iqkiller

# Expose ports
EXPOSE 7862 7863 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default environment variables
ENV AUTH_ENABLED=true \
    RUN_MODE=app \
    JWT_SECRET=change-this-secret-in-production \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7862

# Default command
CMD ["python", "gradio_app.py"]

# Alternative commands:
# For login only: docker run -e RUN_MODE=login iqkiller
# For both interfaces: docker run -e RUN_MODE=both iqkiller  
# For development (no auth): docker run -e AUTH_ENABLED=false iqkiller 