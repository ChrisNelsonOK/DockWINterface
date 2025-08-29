
## v0.9.1 (2025-08-29)

### Network Subnet Update
- **Changed internal VM network**: Updated from 192.168.100.0/24 to 192.254.254.0/24 to avoid conflicts
- **VM IP**: Windows VMs now use 192.254.254.21 internally (was 192.168.100.21)
- **Bridge Gateway**: Internal gateway now 192.254.254.1 (was 192.168.100.1)

### Network Connectivity Fixes
- **Fixed macvlan network connection**: Containers now properly connect to macvlan networks with assigned IP addresses
- **Post-deployment network handling**: Added automatic bridge→macvlan network switching for containers
- **Enhanced SSH deployment**: Network connection logic now works for both local and remote deployments  
- **Improved troubleshooting**: Added comprehensive network troubleshooting documentation

### Bug Fixes
- Resolved issue where containers deployed with bridge network weren't automatically connected to macvlan
- Fixed connectivity problems for Windows containers on dedicated IP addresses
- Ensured VNC (port 8006) and RDP (port 3389) accessibility on macvlan networks

### Technical Improvements
- Enhanced deployment logic in `docker_config.py` and `ssh_docker.py`
- Added automatic network disconnection/connection during deployment
- Improved logging for network connection processes



## [2.1.0] - 2024-08-28

### 🚀 Major Features Added
- **Multi-Version Windows Support**: Added automatic volume mapping for different Windows versions
- **Windows Server 2022 Support**: Full support for Windows Server 2022 Standard and Datacenter editions
- **Version-Specific Volume Paths**: Automatic path selection based on Windows version
  - Windows 10/11: `/opt/windows/xfer`
  - Windows Server 2022: `/opt/windows/xfer2`
  - Windows Server 2019: `/opt/windows/xfer4`
  - Windows Server 2025: `/opt/windows/xfer3`

### 🐛 Critical Fixes
- **Fixed "unknown server OS" error** for Windows Server deployments
- **Resolved volume mapping conflicts** between different Windows versions
- **Fixed container permission issues** with volume directory access
- **Corrected Docker Compose network configuration** (dokwinterface -> dockwinterface)

### 🔧 Technical Improvements
- Enhanced `DockerConfigGenerator` with intelligent version detection
- Added `_get_version_specific_volume_path()` method for automatic path selection
- Implemented `_ensure_volume_directory()` method with fallback logic
- Updated container configuration to include `/opt/windows` volume mount
- Fixed container user permissions (uid=1000) for proper volume access

### 📋 Deployment Changes
- **BREAKING**: Container rebuild required to pick up new volume mapping logic
- **NEW**: Added `/opt/windows:/opt/windows` volume mount requirement
- **CHANGED**: Volume directories must be owned by uid=1000 (container user)
- **UPDATED**: Docker Compose configuration with proper network naming

### 📚 Documentation Updates
- Updated README.md with multi-version support information
- Added comprehensive troubleshooting section for multi-version deployments
- Created detailed deployment update guide (DEPLOYMENT_UPDATE_2024-08-28.md)
- Enhanced volume mapping strategy documentation

### ⚠️ Breaking Changes
- Container must be rebuilt and redeployed to use new features
- `/opt/windows` directory must be mounted into container
- Windows volume directories require specific ownership (uid=1000)

### 🔄 Migration Required
- Stop and remove existing container
- Rebuild Docker image with new code
- Fix volume directory permissions: `chown -R 1000:1000 /opt/windows/xfer*`
- Deploy container with updated volume mounts

# Changelog

All notable changes to DockWINterface will be documented in this file.

## [1.0.2] - 2025-08-16

### Fixed
- **Critical Bug Fix**: Windows version normalization was not working in production
  - Root cause: `docker_config.py` line 281 incorrectly set VERSION under ram_size condition
  - Fixed by properly separating VERSION and RAM_SIZE environment variable assignments
  - Windows versions now correctly normalize (e.g., `11-enterprise` → `11e`)
  - See `docs/WINDOWS_VERSION_FIX.md` for full details

- **Critical Boot Issue**: Windows containers unable to boot - "No bootable option or device was found"
  - Root cause: Missing `/dev/net/tun` device in container deployments
  - Fixed by adding `/dev/net/tun` to devices list in `docker_config.py` line 26
  - Updated SSH deployment logic to properly check for device existence before adding
  - Windows containers now boot and install correctly with full KVM + networking support

- **SSH Deployment Issue**: Enterprise features causing boot failures through SSH deployment
  - Root cause: Missing `--stop-timeout` parameter in SSH deployment docker command generation
  - Investigation confirmed all enterprise features (SNMP, logging, macvlan, rollback) work individually
  - Fixed by adding `stop_grace_period` to `--stop-timeout` conversion in `ssh_docker.py`
  - Enterprise features now fully functional: macvlan networking, rollback protection, SNMP monitoring, and logging integration

### Improved
- **Code Organization**: 
  - Moved all test files to `tests/` directory
  - Cleaned up root directory by removing temporary and debug files
  - Updated test imports to work from new location
- **Documentation**: Added comprehensive fix documentation in `docs/WINDOWS_VERSION_FIX.md`

## [1.0.1] - 2025-08-15

### Added
- **requirements.txt** file for traditional pip installations
- **Unit Tests** for core components:
  - Comprehensive test suite for DockerConfigGenerator
  - Full test coverage for AIAssistant with mocked OpenAI API
- **Enhanced Security**:
  - SESSION_SECRET minimum length validation (32 characters)
  - Automatic validation on application startup

### Fixed
- **Directory Creation**: Automatic creation of `generated_configs` directory if it doesn't exist
- **Error Handling**: Improved validation and error messages for configuration generation

### Improved
- **Code Quality**: Added unit tests to ensure reliability of core components
- **Documentation**: Updated with testing instructions and security requirements
- **Production Readiness**: Enhanced validation for production deployments

## [1.0.0] - 2025-08-15

### Added
- **Core Application Framework**
  - Flask-based web application with modern dark theme interface
  - Responsive Bootstrap 5 UI with red/grey accent colors
  - Multi-step configuration wizard for Windows containers

- **Advanced Windows Container Support**
  - Comprehensive Windows version selection (Win 10/11 Pro/Enterprise/IoT, Server 2025)
  - Support for 64GB and 128GB RAM configurations
  - CPU allocation up to 32 cores
  - Hardware acceleration (KVM) support
  - Disk size configuration up to 1TB

- **Advanced Networking Features**
  - Static IP configuration with subnet mask and gateway settings
  - Additional network interface (NIC) support for multi-homed configurations
  - Custom network creation and management
  - Port mapping for RDP (3389) and VNC (8006)

- **Enterprise Monitoring & Services**
  - SNMP v2c service integration with community strings and trap destinations
  - WMI service configuration for Windows management
  - Built-in logging server for centralized collection of:
    - SNMP traps and notifications
    - Windows event logs
    - Performance metrics and traces
  - Location data configuration for network management

- **Docker Configuration Generation**
  - Automated docker-compose.yml generation
  - Environment file (.env) creation
  - Volume mount configuration
  - Network bridge setup
  - Service health checks and restart policies

- **AI-Powered Assistant**
  - OpenAI GPT-4o integration for expert guidance
  - Docker and Windows container deployment assistance
  - Configuration troubleshooting support
  - Interactive chat interface

- **User Experience Features**
  - Configuration validation with warnings and error handling
  - Real-time form validation
  - Configuration review before generation
  - File download functionality for generated configurations
  - Statistics tracking for usage analytics
  - Recent activity monitoring

- **Production-Ready Features**
  - Environment variable-based configuration
  - Session management with secure secret keys
  - Error handling and graceful degradation
  - Logging with appropriate levels for production
  - WSGI-compatible for deployment with Gunicorn

### Technical Implementation
- **Backend**: Flask with modular route organization
- **Frontend**: Vanilla JavaScript with Bootstrap 5
- **Configuration**: YAML-based Docker Compose generation
- **AI Integration**: OpenAI API with error handling and fallbacks
- **Security**: Environment-based secrets management

### Documentation
- Comprehensive deployment guide
- Production configuration instructions
- Security best practices
- Troubleshooting documentation

---

## Development Notes

This release represents a complete, production-ready Windows container management platform. The application has been thoroughly tested and optimized for performance, security, and usability.

### Key Architectural Decisions
- **Stateless Design**: No database dependencies for easy scaling
- **Modular Structure**: Separate components for configuration, AI assistance, and routing
- **Security-First**: Environment variable configuration and input validation
- **User-Centric**: Intuitive wizard interface with comprehensive validation

### Performance Optimizations
- **Efficient Configuration Generation**: Optimized YAML processing
- **Responsive UI**: Minimal JavaScript footprint with modern CSS
- **Error Handling**: Comprehensive validation and user feedback
- **Resource Management**: Proper memory and CPU allocation guidance