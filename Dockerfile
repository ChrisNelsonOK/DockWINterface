# DockWINterface Production Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Docker CLI
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# Create application directories with proper permissions
RUN mkdir -p /var/lib/dokwinterface/snapshots /var/lib/dokwinterface/generated_configs /etc/dokwinterface \
    && chmod -R 755 /var/lib/dokwinterface /etc/dokwinterface

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create non-root user and add to docker group
RUN useradd --create-home --shell /bin/bash app \
    && groupadd -f docker \
    && usermod -aG docker app \
    && chown -R app:app /app /var/lib/dokwinterface /etc/dokwinterface
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Production command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--reuse-port", "main:app"]
