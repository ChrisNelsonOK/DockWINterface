# DockWINterface

**Production-ready Windows Container Management Platform**

DockWINterface is a comprehensive web-based management platform for Windows containers using the Dockur project. It provides an intuitive interface for configuring, deploying, and managing Windows containers with Docker, featuring advanced networking, enterprise monitoring, and AI-powered assistance.


* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/1-DockWINterface-Home.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/2-DockWINterface-BasicInfo.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/3-DockWINterface-System.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/4-DockWINterface-Network.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/5-DockWINterface-Storage.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/6-DockWINterface-Review.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/7-DockWINterface-GeneratedConfig.png
* https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/8-DockWINterface-Results.png


  

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-production%20ready-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### Core Functionality
- **Advanced Configuration Wizard**: Step-by-step setup for Windows containers
- **Comprehensive Windows Support**: Win 10/11 (Pro/Enterprise/IoT), Server 2025 (Standard/Datacenter)
- **Resource Management**: CPU allocation up to 32 cores, RAM up to 128GB, storage up to 1TB
- **Hardware Acceleration**: KVM support for optimal performance

### Enterprise Networking
- **Static IP Configuration**: Custom IP addresses with subnet mask and gateway
- **Multiple Network Interfaces**: Multi-homed configurations with additional NICs
- **Advanced Port Mapping**: RDP (3389) and VNC (8006) access
- **Custom Network Creation**: Bridge networks with IPAM configuration

### Enterprise Monitoring & Services
- **SNMP v2c Integration**: Community strings, trap destinations, location data
- **WMI Service Configuration**: Windows Management Instrumentation setup
- **Centralized Logging Server**: Collect SNMP traps, Windows events, metrics, and traces
- **Real-time Monitoring**: Container status and performance tracking

### AI-Powered Assistant
- **Expert Guidance**: OpenAI GPT-4o powered assistance for Docker and Windows containers
- **Configuration Help**: Interactive support for complex setups
- **Troubleshooting**: Automated problem diagnosis and solution recommendations

### Production Features
- **Docker Integration**: Automated docker-compose.yml and environment file generation
- **Security**: Environment variable configuration, session management
- **Scalability**: Stateless design with WSGI compatibility
- **Modern UI**: Responsive dark theme with Bootstrap 5

## 🚀 Quick Start

### Prerequisites
- Docker Engine 20.10+
- 4GB+ RAM (8GB+ recommended)
- Hardware virtualization support (for Windows containers)

### Option 1: Docker Deployment (Recommended)

```bash                                                            
# 1. Clone repository
git clone <repository-url>
cd dokwinterface

# 2. Build and run
docker build -t dokwinterface .
docker run -d \
  --name dokwinterface \
  -p 5000:5000 \
  -e SESSION_SECRET="$(openssl rand -hex 32)" \
  -e OPENAI_API_KEY="your-openai-key" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  dokwinterface
```

### Option 2: Direct Deployment

```bash                                        
# 1. Clone and install
git clone <repository-url>
cd dokwinterface
pip install -r requirements.txt

# 2. Configure environment
export SESSION_SECRET="your-secure-session-key"
export OPENAI_API_KEY="your-openai-key"  # Optional

# 3. Start application
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Access Application
Open your browser and navigate to `http://localhost:5000`

## 📖 Documentation    

- **[Deployment Guide](DEPLOYMENT.md)**: Complete production deployment instructions
- **[Changelog](CHANGELOG.md)**: Version history and feature updates
- **[Configuration Examples](generated_configs/)**: Sample configurations for common setups

## 🛠️ Configuration    

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SESSION_SECRET` | Cryptographically secure random string for sessions |

### Optional Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for AI assistant functionality |
| `FLASK_ENV` | Set to `production` for production deployment |

### Generate Secure Session Secret
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🏗️ Architecture

### Technology Stack
- **Backend**: Flask with Gunicorn WSGI server
- **Frontend**: Bootstrap 5 with vanilla JavaScript
- **Configuration**: YAML-based Docker Compose generation
- **AI Integration**: OpenAI GPT-4o API
- **Deployment**: Docker containerization with health checks

### Key Components
- **DockerConfigGenerator**: Advanced Docker configuration creation
- **AIAssistant**: Intelligent guidance system
- **Configuration Wizard**: Multi-step setup interface
- **Enterprise Services**: SNMP, WMI, and logging integration

## 📦 Generated Configurations

DockWINterface generates production-ready configurations:

### Docker Compose Features
- Windows container orchestration
- Network bridge configuration
- Volume mounting
- Service health checks
- Environment variable management

### Advanced Networking
- Static IP address assignment
- Multiple network interface support
- Custom subnet configuration
- DHCP and static IP mixed environments

### Enterprise Services
- SNMP agent configuration
- WMI service setup
- Centralized logging collection
- Performance monitoring integration

## 🔒 Security

### Security Features
- Environment variable-based secrets management
- Session-based authentication
- Input validation and sanitization
- Docker socket access controls

### Production Security
- Use HTTPS with reverse proxy (nginx/Apache)
- Implement rate limiting
- Monitor Docker socket access
- Regular security updates

## 📊 Monitoring  

### Application Monitoring
- Real-time container status
- Resource usage tracking
- Configuration statistics
- AI assistant usage analytics

### Container Monitoring
- Windows container health checks
- Performance metrics collection
- Log aggregation and analysis
- SNMP trap monitoring

## 🤝 Contributing  

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License  

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- **[Dockur](https://github.com/dockur/windows)**: Windows containers in Docker
- **[Docker](https://docker.com)**: Container platform
- **[OpenAI](https://openai.com)**: AI assistant functionality

## 📞 Support

For support and questions:
- Check the [Deployment Guide](DEPLOYMENT.md) for common issues
- Review application logs for troubleshooting
- Submit issues to the repository

---

**DockWINterface** - Making Windows container management simple and powerful.
