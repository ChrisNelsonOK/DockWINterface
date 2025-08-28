#!/bin/bash

# DockWINterface Deployment Update Script
# Usage: ./deploy-update.sh [--rollback]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 DockWINterface Deployment Update Script"
echo "=========================================="

if [ "$1" = "--rollback" ]; then
    echo "🔄 Rolling back to previous configuration..."
    
    if [ -f "docker_config.py.backup" ] && [ -f "docker-compose.production.yml.backup" ]; then
        cp docker_config.py.backup docker_config.py
        cp docker-compose.production.yml.backup docker-compose.production.yml
        echo "✅ Configuration files restored from backup"
    else
        echo "❌ Backup files not found. Cannot rollback."
        exit 1
    fi
else
    echo "📋 Deploying Windows Server 2022 support update..."
    
    # Step 1: Stop existing container
    echo "🛑 Stopping existing container..."
    docker stop DockWINterface 2>/dev/null || echo "Container not running"
    docker rm DockWINterface 2>/dev/null || echo "Container not found"
    
    # Step 2: Fix volume permissions
    echo "🔧 Fixing volume directory permissions..."
    chown -R 1000:1000 /opt/windows/xfer* 2>/dev/null || echo "⚠️  Could not change ownership of /opt/windows/xfer* directories"
    
    # Step 3: Rebuild image
    echo "🔨 Rebuilding Docker image..."
    docker build -t dockwinterface:latest .
    
    # Step 4: Deploy new container
    echo "🚀 Deploying updated container..."
fi

# Deploy container (same for both update and rollback)
docker run -d \
  --name DockWINterface \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$PWD/generated_configs:/app/generated_configs" \
  -v /opt/windows:/opt/windows \
  --health-cmd "curl -f http://localhost:5000/" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  --health-start-period 40s \
  dockwinterface:latest

echo "⏳ Waiting for container to be healthy..."
sleep 10

# Check container status
if docker ps | grep -q DockWINterface; then
    echo "✅ Container deployed successfully!"
    echo "🌐 Application available at: http://localhost:5000"
    
    # Verification tests
    echo ""
    echo "🧪 Running verification tests..."
    
    echo "Testing Windows Server 2022 configuration..."
    if curl -s -X POST http://localhost:5000/api/generate-config \
      -H "Content-Type: application/json" \
      -d '{"name":"test-2022","version":"2022-standard","username":"admin","password":"test123","ram_size":4,"cpu_cores":2,"disk_size":40}' \
      | jq -r .docker_compose | grep -q "xfer2:/storage"; then
        echo "✅ Windows Server 2022 mapping: PASS"
    else
        echo "❌ Windows Server 2022 mapping: FAIL"
    fi
    
    echo "Testing Windows 11 backward compatibility..."
    if curl -s -X POST http://localhost:5000/api/generate-config \
      -H "Content-Type: application/json" \
      -d '{"name":"test-11","version":"11-pro","username":"admin","password":"test123","ram_size":4,"cpu_cores":2,"disk_size":40}' \
      | jq -r .docker_compose | grep -q "xfer:/storage"; then
        echo "✅ Windows 11 compatibility: PASS"
    else
        echo "❌ Windows 11 compatibility: FAIL"
    fi
    
    echo ""
    echo "🎉 Deployment complete!"
    echo "📋 Check the logs with: docker logs DockWINterface"
    
else
    echo "❌ Container failed to start. Check logs:"
    docker logs DockWINterface
    exit 1
fi
