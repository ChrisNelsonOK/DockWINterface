# DokWinterface Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    Flask==3.0.0 \
    gunicorn==21.2.0 \
    PyYAML==6.0.1 \
    openai==1.3.0 \
    email-validator==2.1.0 \
    Flask-SQLAlchemy==3.1.1 \
    psycopg2-binary==2.9.9 \
    python-dotenv==1.0.0

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--reuse-port", "main:app"]