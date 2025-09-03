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

### Application Structure
- **Direct Flask Application**: Uses app.py for development and main.py for production
- **Route Management**: Centralized in routes.py with function-based views
- **Session Handling**: Flask sessions with secure cookies using SESSION_SECRET
- **Rate Limiting**: Flask-Limiter for API and UI requests (200/day, 50/hour)
- **Prometheus Metrics**: /metrics endpoint with custom container counters
- **Async Processing**: Background threads for deployment operations

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

## Development Environment Setup

### Python Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Linux/macOS)
source venv/bin/activate

# Activate the virtual environment (Windows)
venv\Scripts\activate

# Install dependencies with pip
pip install -r requirements.txt

# Alternative with uv (faster dependency manager)
pip install uv
uv pip install -r requirements.txt
```

### Environment Variables
```bash
# Generate secure session secret
python -c "import secrets; print(secrets.token_hex(32))"

# Set required environment variables
export SESSION_SECRET="your-generated-session-key"
export OPENAI_API_KEY="your-openai-key"  # Optional for AI features
export FLASK_ENV="development"  # or "production"
export FLASK_DEBUG=1  # Enable debug mode during development
```

### Dependency Management
```bash
# Use uv for dependency management
uv pip install -r requirements.txt

# Update a specific package
uv pip install --upgrade flask

# Export requirements file from pyproject.toml
uv pip export -r requirements.txt pyproject.toml

# Check for security vulnerabilities
pip install pip-audit
pip-audit
```

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

### Flask CLI Commands
```bash
# List all routes
flask routes

# Start Python shell with application context
flask shell

# Set debug mode (on macOS/Linux)
export FLASK_DEBUG=1
flask run

# Set debug mode (on Windows PowerShell)
$env:FLASK_DEBUG=1
flask run
```

### Docker Development
```bash
# Build development image
docker build -t dockwinterface .

# Run with Docker (development)
docker run -d \
  --name dockwinterface \
  -p 5000:5000 \
  -e SESSION_SECRET="$(openssl rand -hex 32)" \
  -e OPENAI_API_KEY="your-key" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  dockwinterface

# Production deployment
docker-compose -f docker-compose.production.yml up -d
```

### Testing Framework
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Stop on first failure
pytest -x

# Run a specific test file
pytest tests/test_docker_config.py

# Run a specific test function
pytest tests/test_docker_config.py::TestDockerConfigGenerator::test_network_configuration

# Run with coverage report
pip install pytest-cov
pytest --cov=. --cov-report=html

# Run tests in Docker context
docker exec -it dockwinterface pytest
```

### Code Quality & Linting
```bash
# Format code with Black
pip install black
black . --line-length=120

# Sort imports with isort
pip install isort
isort . --profile black

# Lint with flake8
pip install flake8
flake8 . --max-line-length=120

# Type checking with mypy
pip install mypy
mypy . --ignore-missing-imports
```

### Debugging & Profiling
```bash
# Debug with pdb
python -m pdb app.py

# Insert breakpoint in code
# import pdb; pdb.set_trace()

# Profile performance with cProfile
python -m cProfile -o profile.pstats app.py
pip install snakeviz
snakeviz profile.pstats

# Debug Docker container
docker exec -it dockwinterface /bin/bash

# View container logs
docker logs -f dockwinterface
```

### Testing & Debugging
```bash
# Check application logs
docker logs dockwinterface

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
│   ├── base.html       # Base template with layout
│   ├── index.html      # Dashboard page
│   ├── wizard.html     # Configuration wizard
│   └── chat.html       # AI assistant interface
├── static/             # Static assets (CSS, JS, images)
├── tests/              # Pytest test suite (15+ test files)
│   ├── test_docker_config.py
│   ├── test_api.py
│   └── test_yaml_*.py  # Various YAML generation tests
├── generated_configs/  # Generated Docker configurations
├── docs/               # Additional documentation
│   └── DEPLOYMENT.md   # Production deployment guide
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Project metadata and dependencies
├── pytest.ini          # Pytest configuration
└── .env.example        # Example environment variables
```

### Generated Outputs
- `{name}-docker-compose.yml`: Docker Compose configuration
- `{name}.env`: Environment variables file
- `{name}-config.json`: Configuration backup
- `{name}-setup-macvlan.sh`: Macvlan network setup script (Linux)

### Storage Configuration

#### Default Storage (Docker Volumes)
By default, DockWINterface creates Docker named volumes for OS image storage:
- **OS Image Storage**: `{container-name}_os_data:/storage` - Managed Docker volume
- **Benefits**: Portable, secure, managed by Docker, better for production
- **Isolation**: Complete isolation from host filesystem
- **Backup**: Use Docker volume backup commands

#### Alternative Storage (Host Directories)
Optionally, you can use host directory mounting for OS storage:
- **Configuration**: Select "Host Directory" in the storage configuration step
- **Path**: User-specified directory (e.g., `/opt/windows-storage`)
- **Benefits**: Direct host access, easier manual backup
- **Use Cases**: Development environments, specific backup requirements

#### File Sharing (Optional)
Separate from OS storage, file sharing enables host-container file transfer:
- **Purpose**: Transfer files to/from Windows container
- **Default Paths**:
  - Windows 10/11: `/opt/windows/xfer:/file_share`
  - Windows Server 2022: `/opt/windows/xfer2:/file_share`
  - Windows Server 2025: `/opt/windows/xfer3:/file_share`
  - Windows Server 2019: `/opt/windows/xfer4:/file_share`
- **Enable**: Check "Enable file sharing" in storage configuration

### Volume Management Commands

#### Docker Volume Operations
```bash
# List all Docker volumes
docker volume ls

# Inspect a specific volume
docker volume inspect {container-name}_os_data

# Create a volume manually
docker volume create {container-name}_os_data

# Remove unused volumes
docker volume prune

# Remove specific volume (container must be stopped)
docker volume rm {container-name}_os_data
```

#### Volume Backup & Restore
```bash
# Backup Docker volume to tar file
docker run --rm \
  -v {container-name}_os_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/{container-name}_backup_$(date +%Y%m%d).tar.gz -C /data .

# Restore Docker volume from tar file
docker volume create {container-name}_os_data
docker run --rm \
  -v {container-name}_os_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/{container-name}_backup_YYYYMMDD.tar.gz -C /data
```

#### Migration Between Storage Types
```bash
# Migrate from host directory to Docker volume
# 1. Stop container
docker stop {container-name}

# 2. Create Docker volume
docker volume create {container-name}_os_data

# 3. Copy data from host directory to volume
docker run --rm \
  -v /path/to/host/directory:/source \
  -v {container-name}_os_data:/target \
  alpine cp -a /source/. /target/

# 4. Update docker-compose.yml to use volume instead of host mount
# 5. Start container with new configuration
docker-compose up -d
```

#### File Sharing Directory Management
```bash
# Create file sharing directories with proper permissions
sudo mkdir -p /opt/windows/xfer /opt/windows/xfer2 /opt/windows/xfer3 /opt/windows/xfer4
sudo chmod 755 /opt/windows/xfer*
sudo chown 1000:1000 /opt/windows/xfer*

# Verify file sharing directory status
ls -la /opt/windows/
```

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
docker logs -f dockwinterface

# Test AI assistant (if configured)
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Help me configure Windows 11 Pro"}'
```

## Development Principles

This project follows strict development guidelines defined in `DEVELOPMENT.md`, with these key principles:

### The 12 Immutable Project Rules

1. **Foundation Features**: Never change core functionality without explicit approval
2. **Production Quality**: Full production-ready code required at all times
3. **Complete Refactoring**: Remove all placeholder/mock implementations
4. **Codebase Streamlining**: Maintain lean, efficient codebase
5. **Token Limit Strategy**: Use efficient chunking strategies, never leave fragmented code
6. **Clarification Over Assumption**: When in doubt, ask for explicit confirmation
7. **Efficient Workflow**: Prioritize based on project needs
8. **Visual Task Tracking**: Maintain current task visualization
9. **Documentation Consistency**: Update for seamless transitions
10. **Rule Evolution**: Update rules as needed
11. **100% Goal Completion**: Complete everything the first time
12. **Next-Gen Innovation**: Target cutting-edge UI while maintaining stability

For complete details on development practices, refer to [DEVELOPMENT.md](DEVELOPMENT.md).

## Related Documentation

- [README.md](README.md): Project overview and quick start
- [DEVELOPMENT.md](DEVELOPMENT.md): Complete development rules and guidelines
- [DEPLOYMENT.md](docs/DEPLOYMENT.md): Production deployment guide
- [CHANGELOG.md](CHANGELOG.md): Version history and updates

---

*Last updated: September 2025*
*Warp AI compatibility: Optimized for terminal-based development workflows*
