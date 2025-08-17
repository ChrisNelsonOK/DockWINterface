# DockWINterface Production Deployment Guide

## Overview

DockWINterface is a production-ready web application for managing Windows containers using the Dockur project. This guide covers deployment, configuration, and operational considerations.

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), Windows Server, or macOS
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: 20GB+ available disk space
- **Network**: Internet connectivity for container image downloads

### Required Software
- **Docker**: Version 20.10+ with Docker Compose
- **Python**: 3.8+ (if running from source)
- **Git**: For cloning the repository

## Quick Start Deployment

### Option 1: Direct Flask Deployment

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd dokwinterface
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   export SESSION_SECRET="your-secure-random-session-key-here"
   export OPENAI_API_KEY="your-openai-api-key-here"  # Optional for AI assistant
   ```

3. **Start Application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --reuse-port main:app
   ```

### Option 2: Docker Deployment

1. **Build Container**
   ```bash
   docker build -t dokwinterface .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name dokwinterface \
     -p 5000:5000 \
     -e SESSION_SECRET="your-secure-session-key" \
     -e OPENAI_API_KEY="your-openai-key" \
     -v /var/run/docker.sock:/var/run/docker.sock \
     dokwinterface
   ```

## Production Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | **Yes** | Cryptographically secure random string for session management |
| `OPENAI_API_KEY` | No | OpenAI API key for AI assistant functionality |
| `FLASK_ENV` | No | Set to `production` for production deployment |

### Security Considerations

1. **Session Secret**: Generate a strong random key:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Docker Socket Access**: The application requires Docker socket access to manage containers. In production:
   - Consider using Docker API over TCP with TLS
   - Run with minimal required permissions
   - Monitor Docker socket access logs

3. **Network Security**:
   - Use reverse proxy (nginx/Apache) with SSL/TLS termination
   - Implement rate limiting
   - Consider firewall rules for container access

### Reverse Proxy Configuration (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Container Management

### Windows Container Requirements

DockWINterface generates configurations for Windows containers using Dockur. Ensure:

1. **Hardware Virtualization**: KVM support on Linux hosts
2. **Resource Allocation**: Adequate CPU, RAM, and storage for Windows VMs
3. **Network Configuration**: Proper DHCP/static IP setup for containers

### Generated Files

The application generates these configuration files:
- `docker-compose.yml`: Main container orchestration
- `.env`: Environment variables for the container
- Configuration can be downloaded or deployed directly

## Monitoring and Maintenance

### Application Logs
```bash
# Application logs
docker logs dokwinterface

# Container logs (generated configurations)
docker logs [container-name]
```

### Health Checks
- Application status: `http://your-domain.com/`
- AI Assistant status: Visible in dashboard
- Container status: Available in deployments page

### Backup Considerations
- Configuration files are generated on-demand
- No persistent database required
- Backup application configuration and custom settings

## Troubleshooting

### Common Issues

1. **"Session secret not configured"**
   - Solution: Set `SESSION_SECRET` environment variable

2. **"AI Assistant unavailable"**
   - Solution: Configure `OPENAI_API_KEY` or use without AI features

3. **"Docker connection refused"**
   - Solution: Ensure Docker daemon is running and socket is accessible

4. **"Container won't start"**
   - Check generated configuration files
   - Verify host system supports virtualization
   - Review container resource requirements

### Log Analysis
```bash
# Application debug logs
docker logs dokwinterface 2>&1 | grep ERROR

# System resource usage
docker stats dokwinterface
```

## Scaling Considerations

### Horizontal Scaling
- Application is stateless and can run multiple instances
- Use load balancer for multiple instances
- Share Docker socket access across instances

### Resource Scaling
- Monitor CPU/RAM usage during container operations
- Windows containers require significant resources (4GB+ RAM each)
- Plan storage for container images and persistent volumes

## Support and Updates

### Update Process
1. Stop application
2. Pull latest code/image
3. Restart application
4. Verify functionality

### Support Resources
- Application logs for debugging
- Docker community for container issues
- Dockur project documentation for Windows container specifics

## License and Compliance

Ensure compliance with:
- Microsoft Windows licensing for container usage
- Docker licensing terms
- OpenAI API terms of service (if using AI features)

---

For additional support or questions, refer to the project documentation or submit an issue to the repository.