# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Overview

DockWINterface is a production-ready web-based management platform for Windows containers using the Dockur project. It provides an intuitive interface for configuring, deploying, and managing Windows containers with Docker, featuring advanced networking, enterprise monitoring, and AI-powered assistance.

## Core Architecture

### Technology Stack
- **Backend**: Flask 3.0.3 with Gunicorn WSGI server
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **AI Integration**: OpenAI GPT-4o API for intelligent assistance
- **Containerization**: Docker with docker-compose orchestration
- **Monitoring**: Prometheus Flask Exporter for metrics
- **Security**: Flask-Limiter for rate limiting, session-based authentication

### Key Components

#### DockerConfigGenerator (`docker_config.py`)
Core engine that generates production-ready Docker configurations for Windows containers using the Dockur project. Handles:
- Docker Compose YAML generation with advanced networking
- Environment file creation with proper variable escaping
- Macvlan network setup scripts
- Configuration validation and sanitization
- Support for multiple Windows versions (Win 10/11, Server editions)

#### AIAssistant (`ai_assistant.py`)
OpenAI GPT-4o powered assistant providing expert guidance for Docker and Windows containers:
- Interactive chat interface for deployment questions
- Configuration analysis and recommendations
- Troubleshooting assistance with log analysis
- Uses structured JSON responses for configuration advice

#### RollbackManager (`rollback_manager.py`)
Linux-only system recovery using RevertIT integration:
- Creates checkpoints before risky deployments
- Automatic rollback on deployment failures
- Network state preservation
- Docker state snapshots

#### SSH Tunnel Support (`ssh_docker.py`)
Secure remote Docker deployment via SSH tunnels:
- Paramiko-based SSH connections
- Port forwarding for Docker daemon access
- Support for key-based and password authentication

### Data Flow
1. **User Input** → Configuration wizard (`templates/wizard.html`)
2. **Form Processing** → Routes handler (`routes.py`)
3. **Version Mapping** → Windows UI strings to Dockur flags
4. **Configuration Generation** → DockerConfigGenerator creates files
5. **Optional AI Analysis** → GPT-4o provides recommendations
6. **File Output** → Generated configs saved to `generated_configs/`

## Development Commands

### Local Development
```bash
# Start development server
python app.py

# Alternative with Flask CLI
flask run --host=0.0.0.0 --port=5000

# Production server with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
```

### Environment Setup
```bash
# Generate secure session secret
python -c "import secrets; print(secrets.token_hex(32))"

# Set required environment variables
export SESSION_SECRET="your-generated-session-key"
export OPENAI_API_KEY="your-openai-key"  # Optional for AI features
export FLASK_ENV="development"  # or "production"
```

### Docker Development
```bash
# Build development image
docker build -t dokwinterface .

# Run with Docker (development)
docker run -d \
  --name dokwinterface \
  -p 5000:5000 \
  -e SESSION_SECRET="$(openssl rand -hex 32)" \
  -e OPENAI_API_KEY="your-key" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  dokwinterface

# Production deployment
docker-compose -f docker-compose.production.yml up -d
```

### Testing & Debugging
```bash
# Check application logs
docker logs dokwinterface

# Test API endpoints
curl -X POST http://localhost:5000/api/generate-config \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "version": "11", "username": "user", "password": "pass"}'

# Check Docker socket access
docker ps  # Should work from container if socket mounted correctly
```

## Windows Container Configuration

### Version Mapping (UI → Dockur)
The system maps user-friendly UI strings to Dockur backend flags:
```python
# Windows 11
'11-enterprise' → '11'  # Uses Pro instead due to Enterprise installation issues
'11-ltsc' → '11l'

# Windows 10
'10-enterprise' → '10e'
'10-ltsc' → '10l'

# Server editions
'2025' → '2025'
'2022' → '2022'
```

### Network Modes
- **Bridge** (default): Standard Docker networking with port mapping
- **Host**: Container shares host network stack
- **Static IP**: Custom bridge network with fixed IP assignment
- **Macvlan**: Direct Layer 2 network access (requires setup script)
- **None**: No network connectivity

### Resource Guidelines
- **CPU**: 1-32 cores (2-4 recommended for Windows)
- **RAM**: 2-128GB (4-8GB minimum for Windows)
- **Storage**: 20-1000GB (50GB+ recommended for Windows)
- **KVM**: Required for hardware acceleration on Linux

## Key Files & Directories

### Application Structure
```
├── app.py              # Flask application initialization
├── main.py             # Production entry point
├── routes.py           # Route handlers and API endpoints
├── docker_config.py    # Core configuration generation
├── ai_assistant.py     # OpenAI integration
├── rollback_manager.py # System recovery (Linux only)
├── ssh_docker.py       # SSH tunnel support
├── templates/          # Jinja2 HTML templates
├── generated_configs/  # Generated Docker configurations
└── requirements.txt    # Python dependencies
```

### Generated Outputs
- `{name}-docker-compose.yml`: Docker Compose configuration
- `{name}.env`: Environment variables file
- `{name}-config.json`: Configuration backup
- `{name}-setup-macvlan.sh`: Macvlan network setup script (Linux)

## API Endpoints

### Main Endpoints
- `GET /`: Dashboard (renders `templates/index.html`)
- `GET /wizard`: Configuration wizard
- `GET /chat`: AI assistant interface
- `POST /api/generate-config`: Generate Docker configuration

### Rate Limits
- Default: 200 requests per day, 50 per hour
- Configuration generation: Same limits to prevent abuse

## Production Deployment

### Prerequisites
- Docker Engine 20.10+
- 4GB+ RAM (8GB+ recommended)
- Hardware virtualization support for Windows containers
- Linux host for RevertIT rollback features

### Security Requirements
```bash
# Generate cryptographically secure session secret
SESSION_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")

# Recommended: Use reverse proxy (nginx) with HTTPS
# Mount Docker socket with appropriate permissions
# Implement additional rate limiting if needed
```

### Health Monitoring
- Health check endpoint: `GET /` (returns 200 for healthy app)
- Prometheus metrics available via flask-prometheus-exporter
- Container health check: 30s interval, 10s timeout

## Enterprise Features

### SNMP Integration
Supports SNMP v2c configuration for Windows containers:
- Community strings and trap destinations
- Location and contact information
- Performance monitoring integration

### Centralized Logging
Configurable log collection from Windows containers:
- Windows event logs
- SNMP traps
- Performance metrics
- Application traces

### Advanced Networking
- Multiple network interface support
- Static IP assignment with IPAM
- Custom bridge networks
- Macvlan with host access configuration

## AI Assistant Usage

### Configuration
- Requires `OPENAI_API_KEY` environment variable
- Uses GPT-4o model (do not change without explicit request)
- Provides Docker and Windows container expertise

### Capabilities
- Interactive chat for deployment guidance
- Configuration analysis with JSON-formatted recommendations
- Troubleshooting with log analysis
- Best practices for Dockur Windows containers

## Troubleshooting

### Common Issues
1. **Docker socket access**: Ensure `/var/run/docker.sock` is mounted and accessible
2. **Session secret warnings**: Set `SESSION_SECRET` environment variable (32+ characters)
3. **Windows container failures**: Verify KVM support and adequate resources
4. **Network issues**: Check macvlan parent interface and IP conflicts

### Debugging Commands
```bash
# Check Docker connectivity
docker version

# Verify container logs
docker logs -f dokwinterface

# Test AI assistant (if configured)
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me configure Windows 11 Pro"}'
```

## Development Rules

This project follows strict development guidelines defined in `DEVELOPMENT.md`:
- All 12 immutable project rules must be followed
- Production-quality code required at all times
- Complete refactoring of any incomplete modules
- Efficient workflow prioritization
- 100% goal completion requirement

## Related Documentation

- [README.md](README.md): Project overview and quick start
- [DEVELOPMENT.md](DEVELOPMENT.md): Complete development rules and guidelines
- [DEPLOYMENT.md](DEPLOYMENT.md): Production deployment guide
- [CHANGELOG.md](CHANGELOG.md): Version history and updates

---

*Last updated: December 2024*
*Warp AI compatibility: Optimized for terminal-based development workflows*
