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
        
        # Add network configuration
        networks = self._generate_networks(config)
        if networks:
            if 'networks' not in compose_config:
                compose_config['networks'] = {}
            compose_config['networks'].update(networks)
            
            # Connect service to networks
            service_networks = self._generate_service_networks(config)
            if service_networks:
                compose_config['services'][config.get('name', 'windows')]['networks'] = service_networks
        elif config.get('network_mode') and config.get('network_mode') != 'static':
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
        
        # Language and keyboard settings
        if config.get('language'):
            env_vars.append(f"LANGUAGE={config['language']}")
        if config.get('keyboard'):
            env_vars.append(f"KEYBOARD={config['keyboard']}")
        
        # System resources
        if config.get('cpu_cores'):
            env_vars.append(f"CPU_CORES={config['cpu_cores']}")
        if config.get('ram_size'):
            env_vars.append(f"RAM_SIZE={config['ram_size']}G")
        
        # Disk configuration
        if config.get('disk_size'):
            env_vars.append(f"DISK_SIZE={config['disk_size']}G")
        
        # Additional options
        if config.get('enable_kvm', True):
            env_vars.append("KVM=Y")
        
        if config.get('debug', False):
            env_vars.append("DEBUG=Y")
        
        # Network configuration
        if config.get('dns_servers'):
            env_vars.append(f"DNS={config['dns_servers']}")
        
        # Static IP configuration
        if config.get('network_mode') == 'static':
            if config.get('static_ip'):
                env_vars.append(f"IP={config['static_ip']}")
            if config.get('gateway'):
                env_vars.append(f"GATEWAY={config['gateway']}")
            if config.get('subnet_mask'):
                env_vars.append(f"NETMASK={config['subnet_mask']}")
        
        # SNMP configuration
        if config.get('enable_snmp'):
            env_vars.append("SNMP_ENABLED=Y")
            if config.get('snmp_community'):
                env_vars.append(f"SNMP_COMMUNITY={config['snmp_community']}")
            if config.get('snmp_port'):
                env_vars.append(f"SNMP_PORT={config['snmp_port']}")
            if config.get('snmp_location'):
                env_vars.append(f"SNMP_LOCATION={config['snmp_location']}")
            if config.get('snmp_contact'):
                env_vars.append(f"SNMP_CONTACT={config['snmp_contact']}")
            if config.get('snmp_trap_destinations'):
                # Convert multiline trap destinations to comma-separated list
                traps = config['snmp_trap_destinations'].strip().replace('\n', ',')
                env_vars.append(f"SNMP_TRAPS={traps}")
        
        # Logging configuration
        if config.get('enable_logging'):
            env_vars.append("LOGGING_ENABLED=Y")
            if config.get('log_server_host'):
                env_vars.append(f"LOG_SERVER={config['log_server_host']}")
            if config.get('log_server_port'):
                env_vars.append(f"LOG_PORT={config['log_server_port']}")
            if config.get('log_protocol'):
                env_vars.append(f"LOG_PROTOCOL={config['log_protocol']}")
            if config.get('log_format'):
                env_vars.append(f"LOG_FORMAT={config['log_format']}")
            
            # Log sources
            log_sources = []
            if config.get('log_windows_events'):
                log_sources.append('windows_events')
            if config.get('log_snmp_traps'):
                log_sources.append('snmp_traps')
            if config.get('log_performance_metrics'):
                log_sources.append('performance_metrics')
            if config.get('log_application_traces'):
                log_sources.append('application_traces')
            
            if log_sources:
                env_vars.append(f"LOG_SOURCES={','.join(log_sources)}")
        
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
    
    def _generate_networks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Docker networks configuration"""
        networks = {}
        
        # Static IP network configuration
        if config.get('network_mode') == 'static':
            network_name = config.get('network_name', 'dokwinter-network')
            networks[network_name] = {
                'driver': 'bridge',
                'ipam': {
                    'config': [{
                        'subnet': self._calculate_subnet(config.get('static_ip', ''), config.get('subnet_mask', '255.255.255.0')),
                        'gateway': config.get('gateway')
                    }]
                }
            }
        
        # Additional network interfaces
        if config.get('additional_networks'):
            for i, network_config in enumerate(config['additional_networks']):
                if isinstance(network_config, dict) and network_config.get('network'):
                    net_name = network_config['network']
                    networks[net_name] = {
                        'driver': 'bridge'
                    }
                    if network_config.get('ip') and network_config.get('subnet'):
                        networks[net_name]['ipam'] = {
                            'config': [{
                                'subnet': self._calculate_subnet(network_config.get('ip', ''), network_config.get('subnet', '255.255.255.0'))
                            }]
                        }
        
        return networks
    
    def _generate_service_networks(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service network configuration"""
        service_networks = {}
        
        # Static IP configuration
        if config.get('network_mode') == 'static' and config.get('static_ip'):
            network_name = config.get('network_name', 'dokwinter-network')
            service_networks[network_name] = {
                'ipv4_address': config['static_ip']
            }
        
        # Additional network interfaces
        if config.get('additional_networks'):
            for network_config in config['additional_networks']:
                if isinstance(network_config, dict) and network_config.get('network'):
                    net_name = network_config['network']
                    service_networks[net_name] = {}
                    if network_config.get('ip'):
                        service_networks[net_name]['ipv4_address'] = network_config['ip']
        
        return service_networks
    
    def _calculate_subnet(self, ip_address: str, subnet_mask: str) -> str:
        """Calculate subnet CIDR from IP and mask"""
        if not ip_address or not subnet_mask:
            return "172.20.0.0/16"  # Default subnet
        
        try:
            # Convert subnet mask to CIDR notation
            mask_parts = subnet_mask.split('.')
            if len(mask_parts) == 4:
                cidr = sum([bin(int(part)).count('1') for part in mask_parts])
                ip_parts = ip_address.split('.')
                if len(ip_parts) == 4:
                    # Calculate network address
                    network_parts = []
                    for i in range(4):
                        network_parts.append(str(int(ip_parts[i]) & int(mask_parts[i])))
                    return f"{'.'.join(network_parts)}/{cidr}"
        except (ValueError, IndexError):
            pass
        
        return "172.20.0.0/16"  # Fallback subnet
    
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
                if ram_size < 2 or ram_size > 128:
                    warnings.append("RAM size should be between 2GB and 128GB")
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
