# Overview

DokWinterface is a production-ready, comprehensive web-based management platform for Windows containers using the Dockur project. It provides an intuitive interface for configuring, deploying, and managing Windows containers with Docker. The application features an advanced configuration wizard, deployment management dashboard, enterprise networking capabilities, SNMP/WMI services integration, centralized logging server configuration, and an AI-powered assistant for expert guidance.

## Current Status: Production Ready (v1.0.0)
- ✅ All core features implemented and tested
- ✅ Production deployment configuration complete
- ✅ Security hardening and environment variable management
- ✅ Comprehensive documentation and deployment guides
- ✅ Advanced Windows container support with enterprise features
- ✅ Mock data removed and production optimizations applied

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Flask-based web application with server-side rendering using Jinja2 templates
- **UI Framework**: Bootstrap 5 with dark theme as the primary design system
- **JavaScript Architecture**: Vanilla JavaScript with modular structure for different components (wizard, chat, main utilities)
- **Styling**: Custom CSS with CSS variables for theming, responsive design with mobile-first approach

## Backend Architecture
- **Web Framework**: Flask with blueprint-style route organization
- **Application Structure**: Modular design with separate components for configuration generation, AI assistance, and routing
- **Configuration Management**: YAML-based Docker Compose generation with environment variable handling
- **File Generation**: Automated creation of Docker configuration files with user-customizable options

## Core Components
- **DockerConfigGenerator**: Advanced creation of docker-compose.yml and environment files with support for static IPs, multiple NICs, SNMP/WMI services, and logging server configuration
- **AIAssistant**: OpenAI GPT-4o powered chat assistant specialized in Docker and Windows container deployment guidance with enterprise configuration support
- **Configuration Wizard**: Comprehensive multi-step interface supporting all Windows versions (10/11 Pro/Enterprise/IoT, Server 2025), advanced networking, and enterprise monitoring
- **Deployment Management**: Production-ready dashboard for monitoring and managing active container deployments with real-time status
- **Enterprise Services**: SNMP v2c integration, WMI configuration, and centralized logging server for enterprise monitoring
- **Advanced Networking**: Static IP configuration, additional network interfaces, custom network creation, and multi-homed setups

## Security Considerations
- Environment variable-based configuration for sensitive data (API keys, session secrets)
- Session management with configurable secret keys
- Input validation for configuration parameters
- Graceful degradation when AI features are unavailable

## Application Flow
- Users navigate through an advanced wizard to configure Windows containers with comprehensive options
- Configuration data is validated and processed into production-ready Docker Compose files
- Generated configurations include networking, monitoring, and enterprise service setup
- Configurations can be downloaded, reviewed, or deployed directly
- AI assistant provides expert guidance on complex configurations and troubleshooting
- Deployment dashboard allows real-time monitoring and management of active containers
- Enterprise features enable SNMP monitoring, centralized logging, and advanced networking

## Recent Changes (August 2025)
- **Production Finalization**: Removed all mock data and development artifacts
- **Security Hardening**: Implemented environment variable-based configuration with secure session management
- **Performance Optimization**: Disabled debug mode and optimized logging for production
- **Documentation**: Created comprehensive deployment guides and production documentation
- **Code Cleanup**: Streamlined codebase and removed development-only features

# External Dependencies

## Required Services
- **OpenAI API**: Powers the AI assistant functionality for providing expert guidance on Docker and Windows container deployment
- **Docker Engine**: Required for container deployment and management (not directly integrated but necessary for generated configurations)
- **Dockur Windows Project**: The base container images used for Windows virtualization

## Python Packages
- **Flask**: Web framework for the application backend
- **PyYAML**: YAML processing for Docker Compose file generation
- **OpenAI**: Official OpenAI client library for AI chat functionality (optional dependency with graceful fallback)

## Frontend Dependencies
- **Bootstrap 5**: UI component framework and styling
- **Font Awesome**: Icon library for UI elements
- **CDN-delivered assets**: External hosting for CSS and JavaScript libraries

## Development Dependencies
- **Logging**: Built-in Python logging for debugging and monitoring
- **Environment Variables**: Configuration management for API keys and settings
- **File System Operations**: Local file generation and management for configuration outputs