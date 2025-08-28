# ⚡  DockWINterface  
## Windows Container Generation & Management Platform ##


DockWINterface is a comprehensive web-based management platform for Windows containers using the Dockur project. It provides an intuitive interface for configuring, deploying, and managing Windows containers with Docker, featuring advanced networking, enterprise monitoring, and AI-powered assistance.


| Home Dashboard | Basic Configuration | System Settings |
|:--------------:|:------------------:|:---------------:|
| [![Home](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/1-DockWINterface-Home.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/1-DockWINterface-Home.png) | [![Basic Info](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/2-DockWINterface-BasicInfo.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/2-DockWINterface-BasicInfo.png) | [![System](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/3-DockWINterface-System.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/3-DockWINterface-System.png) |

| Network Configuration | Storage Management | Review & Deploy |
|:---------------------:|:-----------------:|:---------------:|
| [![Network](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/4-DockWINterface-Network.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/4-DockWINterface-Network.png) | [![Storage](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/5-DockWINterface-Storage.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/5-DockWINterface-Storage.png) | [![Review](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/6-DockWINterface-Review.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/6-DockWINterface-Review.png) |

| Generated Configuration | Deployment Results |
|:-----------------------:|:-----------------:|
| [![Generated Config](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/7-DockWINterface-GeneratedConfig.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/7-DockWINterface-GeneratedConfig.png) | [![Results](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/8-DockWINterface-Results.png?raw=true)](https://github.com/ChrisNelsonOK/DockWINterface/blob/main/images/8-DockWINterface-Results.png) |


#
#
![Version](https://img.shields.io/badge/version-v0.9.0-green.svg)
![Status](https://img.shields.io/badge/status-beta%20testing-orange.svg)
![License](https://img.shields.io/badge/license-GPL-blue.svg)


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
cd dockwinterface

# 2. Build and run
docker logs dockwinterface .
docker run -d \
  --name dockwinterface \
  -p 5000:5000 \
  -e SESSION_SECRET="$(openssl rand -hex 32)" \
  -e OPENAI_API_KEY="your-openai-key" \
  -v /var/run/docker-compose -f docker-compose.production.yml up -d dockwinterface
```

### Option 2: Direct Deployment

```bash                                        
# 1. Clone and install
git clone <repository-url>
cd dockwinterface
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

# Built Upon Excellence
#DockWINterface stands on the shoulders of giants. This project is made possible by the groundbreaking work of: 🌟 Dockur Windows Project: https://github.com/dockur/windows
#
Creator: The brilliant minds behind bringing full Windows virtualization to Docker
Innovation: Revolutionary approach to Windows containers that this entire platform depends upon

Community: Active development and continuous improvements that keep this ecosystem thriving

## Why Dockur?
The Dockur Windows project solved the impossible - running full Windows environments in Docker containers with:

✅ True Windows Experience: Complete Windows 10/11 and Server installations
✅ Hardware Acceleration: KVM integration for near-native performance
✅ Universal Compatibility: Works across different host operating systems
✅ Production Ready: Stable, tested, and continuously maintained

DockWINterface simply makes this incredible technology accessible to everyone through an intuitive web interface.

#SpecialThanks

Dockur Team: For creating and maintaining the core Windows containerization technology/process
Docker Community: For the robust container ecosystem
Open Source Contributors: Who make projects like this possible


###### "Standing on the shoulders of giants allows us to see further." - This project exists because of the innovation and hard work of the Dockur project maintainers.

## 📄 License  

This project is licensed under the GPL License - see the LICENSE file for details.

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

# ⚡ DockWINterface 
Making Windows container management simple and powerful.

## 🚀 Multi-Version Windows Support

DockWINterface now supports automatic volume mapping for different Windows versions:

### Supported Windows Versions & Volume Mappings

| Windows Version | Volume Mount Path | Description |
|----------------|------------------|-------------|
| Windows 10 (All editions) | `/opt/windows/xfer` | Home, Pro, Enterprise, IoT |
| Windows 11 (All editions) | `/opt/windows/xfer` | Home, Pro, Enterprise, IoT |
| Windows Server 2022 | `/opt/windows/xfer2` | Standard, Datacenter |
| Windows Server 2019 | `/opt/windows/xfer4` | Standard, Datacenter |
| Windows Server 2025 | `/opt/windows/xfer3` | Standard, Datacenter |

### Automatic Volume Selection

The system automatically selects the appropriate volume path based on the selected Windows version:

- **No manual configuration required** - volume paths are assigned automatically
- **Concurrent deployments supported** - multiple Windows versions can run simultaneously
- **ISO/file isolation** - each version uses its dedicated volume mount
- **Backward compatible** - existing Windows 11 deployments continue to work

### Manual Volume Override

If you need to use a custom volume path, you can still specify it manually in the "Data Volume" field during deployment.

### Troubleshooting Multi-Version Deployments

If you encounter issues with Windows Server deployments:

1. **Verify volume directories exist:**
   ```bash
   ls -la /opt/windows/
   # Should show xfer, xfer2, xfer3, xfer4 directories
   ```

2. **Check permissions:**
   ```bash
   chmod 755 /opt/windows/xfer*
   ```

3. **View deployment logs:**
   ```bash
   docker logs DockWINterface
   ```

Look for log messages like:
- `Auto-selected volume path for version '2022-standard': /opt/windows/xfer2`
- `Created volume directory: /opt/windows/xfer2`


---

## 🔧 Recent Updates (August 28, 2024)

### Windows Server 2022 Support Enhancement
- **Fixed "unknown server OS" error** for Windows Server deployments
- **Added automatic volume mapping** for different Windows versions
- **Enhanced container configuration** with proper volume mounting
- **Improved permission handling** for multi-version support

### Key Changes Made
1. **Updated Docker Configuration**: Added `/opt/windows` volume mount to container
2. **Fixed Volume Permissions**: Corrected ownership for container access (uid=1000)
3. **Enhanced Version Detection**: Improved Windows version parsing and mapping
4. **Updated Documentation**: Added comprehensive deployment and troubleshooting guides

### Deployment Requirements
- **Container Rebuild Required**: New image includes enhanced volume mapping logic
- **Volume Mount Added**: Container now needs access to `/opt/windows` for version-specific paths
- **Permission Fix**: Windows volume directories must be owned by uid=1000 (container user)

## 📋 Post-Update Verification

Verify your deployment is working correctly:

```bash
# Test Windows Server 2022 configuration
curl -X POST http://localhost:5000/api/generate-config \
  -H "Content-Type: application/json" \
  -d '{"name":"test-2022","version":"2022-standard","username":"admin","password":"test123","ram_size":4,"cpu_cores":2,"disk_size":40}' \
  | jq -r .docker_compose | grep xfer

# Should output: - /opt/windows/xfer2:/storage
```

```bash
# Test Windows 11 backward compatibility  
curl -X POST http://localhost:5000/api/generate-config \
  -H "Content-Type: application/json" \
  -d '{"name":"test-11","version":"11-pro","username":"admin","password":"test123","ram_size":4,"cpu_cores":2,"disk_size":40}' \
  | jq -r .docker_compose | grep xfer

# Should output: - /opt/windows/xfer:/storage
```

## 🚨 Important Notes

### Volume Directory Structure
Ensure your `/opt/windows/` directory contains the following subdirectories with proper permissions:
```bash
/opt/windows/xfer/     # Windows 10/11 ISOs and files
/opt/windows/xfer2/    # Windows Server 2022 ISOs and files  
/opt/windows/xfer3/    # Windows Server 2025 ISOs and files
/opt/windows/xfer4/    # Windows Server 2019 ISOs and files
```

### Container Requirements
- **Docker Socket Access**: Required for container deployment
- **Volume Access**: Container needs read/write access to `/opt/windows/`
- **Network Access**: Container must be able to reach target deployment hosts
- **Proper Ownership**: Windows directories must be owned by uid=1000

For detailed deployment instructions, see `DEPLOYMENT_UPDATE_2024-08-28.md`.

