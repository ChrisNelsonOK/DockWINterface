import os
import yaml
import json
from typing import Dict, Any, List
import logging

class DockerConfigGenerator:
    def __init__(self):
        self.output_dir = "generated_configs"
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_docker_compose(self, config: Dict[str, Any]) -> str:
        """Generate docker-compose.yml content for Dockur Windows"""
        
        compose_config = {
            'version': '3.8',
            'services': {
                config.get('name', 'windows'): {
                    'image': f"dockurr/windows:{config.get('version', 'latest')}",
                    'container_name': config.get('name', 'windows'),
                    'environment': self._generate_environment_vars(config),
                    'devices': ['/dev/kvm'],
                    'cap_add': ['NET_ADMIN'],
                    'ports': [
                        f"{config.get('rdp_port', '3389')}:3389/tcp",
                        f"{config.get('vnc_port', '8006')}:8006/tcp"
                    ],
                    'stop_grace_period': '2m',
                    'restart': 'on-failure'
                }
            }
        }
        
        # Add volumes if specified
        volumes = self._generate_volumes(config)
        if volumes:
            compose_config['services'][config.get('name', 'windows')]['volumes'] = volumes
        
        # Add network configuration if specified
        if config.get('network_mode'):
            compose_config['services'][config.get('name', 'windows')]['network_mode'] = config['network_mode']
        
        # Add resource limits if specified
        if config.get('cpu_limit') or config.get('memory_limit'):
            deploy_config = {}
            if config.get('cpu_limit'):
                deploy_config['resources'] = {
                    'limits': {'cpus': str(config['cpu_limit'])}
                }
            if config.get('memory_limit'):
                if 'resources' not in deploy_config:
                    deploy_config['resources'] = {'limits': {}}
                deploy_config['resources']['limits']['memory'] = f"{config['memory_limit']}G"
            
            compose_config['services'][config.get('name', 'windows')]['deploy'] = deploy_config
        
        return yaml.dump(compose_config, default_flow_style=False, sort_keys=False)
    
    def _generate_environment_vars(self, config: Dict[str, Any]) -> List[str]:
        """Generate environment variables for the container"""
        env_vars = []
        
        # Basic Windows configuration
        if config.get('username'):
            env_vars.append(f"USERNAME={config['username']}")
        if config.get('password'):
            env_vars.append(f"PASSWORD={config['password']}")
        
        # Disk configuration
        if config.get('disk_size'):
            env_vars.append(f"DISK_SIZE={config['disk_size']}G")
        
        # CPU and RAM configuration
        if config.get('cpu_cores'):
            env_vars.append(f"CPU_CORES={config['cpu_cores']}")
        if config.get('ram_size'):
            env_vars.append(f"RAM_SIZE={config['ram_size']}G")
        
        # Additional options
        if config.get('enable_kvm', True):
            env_vars.append("KVM=Y")
        
        if config.get('debug', False):
            env_vars.append("DEBUG=Y")
        
        if config.get('language'):
            env_vars.append(f"LANGUAGE={config['language']}")
        
        if config.get('keyboard'):
            env_vars.append(f"KEYBOARD={config['keyboard']}")
        
        return env_vars
    
    def _generate_volumes(self, config: Dict[str, Any]) -> List[str]:
        """Generate volume mappings"""
        volumes = []
        
        # Data volume for persistence
        if config.get('data_volume'):
            volumes.append(f"{config['data_volume']}:/storage")
        
        # Additional volumes
        if config.get('additional_volumes'):
            for volume in config['additional_volumes']:
                if isinstance(volume, dict) and 'host' in volume and 'container' in volume:
                    volumes.append(f"{volume['host']}:{volume['container']}")
                elif isinstance(volume, str):
                    volumes.append(volume)
        
        return volumes
    
    def generate_env_file(self, config: Dict[str, Any]) -> str:
        """Generate .env file content"""
        env_content = "# DokWinterface Generated Environment File\n"
        env_content += f"# Generated for container: {config.get('name', 'windows')}\n\n"
        
        env_vars = self._generate_environment_vars(config)
        for var in env_vars:
            env_content += f"{var}\n"
        
        # Additional Docker-specific settings
        env_content += f"\n# Container Configuration\n"
        env_content += f"CONTAINER_NAME={config.get('name', 'windows')}\n"
        env_content += f"RDP_PORT={config.get('rdp_port', '3389')}\n"
        env_content += f"VNC_PORT={config.get('vnc_port', '8006')}\n"
        
        return env_content
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration parameters"""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ['name', 'version', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate container name
        if config.get('name'):
            name = config['name']
            if not name.replace('-', '').replace('_', '').isalnum():
                errors.append("Container name can only contain letters, numbers, hyphens, and underscores")
        
        # Validate password strength
        password = config.get('password', '')
        if password and len(password) < 8:
            warnings.append("Password should be at least 8 characters long")
        
        # Validate resource limits
        if config.get('cpu_cores'):
            try:
                cpu_cores = int(config['cpu_cores'])
                if cpu_cores < 1 or cpu_cores > 32:
                    warnings.append("CPU cores should be between 1 and 32")
            except ValueError:
                errors.append("CPU cores must be a valid number")
        
        if config.get('ram_size'):
            try:
                ram_size = int(config['ram_size'])
                if ram_size < 2 or ram_size > 64:
                    warnings.append("RAM size should be between 2GB and 64GB")
            except ValueError:
                errors.append("RAM size must be a valid number")
        
        if config.get('disk_size'):
            try:
                disk_size = int(config['disk_size'])
                if disk_size < 20 or disk_size > 1000:
                    warnings.append("Disk size should be between 20GB and 1000GB")
            except ValueError:
                errors.append("Disk size must be a valid number")
        
        # Validate ports
        for port_field in ['rdp_port', 'vnc_port']:
            if config.get(port_field):
                try:
                    port = int(config[port_field])
                    if port < 1024 or port > 65535:
                        warnings.append(f"{port_field} should be between 1024 and 65535")
                except ValueError:
                    errors.append(f"{port_field} must be a valid port number")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def save_config_files(self, config: Dict[str, Any]):
        """Save generated configuration files to disk"""
        container_name = config.get('name', 'windows')
        
        # Generate content
        docker_compose = self.generate_docker_compose(config)
        env_file = self.generate_env_file(config)
        
        # Save docker-compose.yml
        compose_path = os.path.join(self.output_dir, f"{container_name}-docker-compose.yml")
        with open(compose_path, 'w') as f:
            f.write(docker_compose)
        
        # Save .env file
        env_path = os.path.join(self.output_dir, f"{container_name}.env")
        with open(env_path, 'w') as f:
            f.write(env_file)
        
        # Save configuration JSON for reference
        config_path = os.path.join(self.output_dir, f"{container_name}-config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logging.info(f"Configuration files saved for {container_name}")
        
        return {
            'docker_compose_path': compose_path,
            'env_path': env_path,
            'config_path': config_path
        }
