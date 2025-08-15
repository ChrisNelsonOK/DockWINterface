# Overview

DokWinterface is a modern web-based management platform for Windows containers using the Dockur project. It provides a user-friendly interface for configuring, deploying, and managing Windows containers with Docker. The application features a configuration wizard, deployment management dashboard, and an AI-powered assistant to help users with container setup and troubleshooting.

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
- **DockerConfigGenerator**: Handles creation of docker-compose.yml and environment files for Dockur Windows containers
- **AIAssistant**: OpenAI-powered chat assistant specialized in Docker and Windows container deployment guidance
- **Configuration Wizard**: Multi-step form interface for guided container setup
- **Deployment Management**: Dashboard for monitoring and managing active container deployments

## Security Considerations
- Environment variable-based configuration for sensitive data (API keys, session secrets)
- Session management with configurable secret keys
- Input validation for configuration parameters
- Graceful degradation when AI features are unavailable

## Application Flow
- Users navigate through a wizard to configure Windows containers
- Configuration data is processed and converted to Docker Compose files
- Generated configurations can be downloaded or deployed
- AI assistant provides contextual help and troubleshooting guidance
- Deployment dashboard allows monitoring of active containers

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