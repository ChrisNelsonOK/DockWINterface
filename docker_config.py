import os
import yaml
import json
import subprocess
import tempfile
import logging
from typing import Dict, Any, List, Optional

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
        # Basic service configuration
        service_config = {
            'image': 'dockurr/windows',
            'container_name': config.get('name', 'windows'),
            'environment': self._generate_environment_dict(config),
            'devices': ['/dev/kvm'],
            'cap_add': ['NET_ADMIN'],
            'stop_grace_period': '2m',
            'restart': 'on-failure'
        }

        # Add ports only if not using macvlan
        # (macvlan exposes all ports by default)
        if config.get('network_mode') != 'macvlan':
            service_config['ports'] = [
                f"{config.get('rdp_port', '3389')}:3389/tcp",
                f"{config.get('vnc_port', '8006')}:8006/tcp"
            ]

        # Add DHCP-specific devices and cgroup rules for macvlan
        is_macvlan_dhcp = (config.get('network_mode') == 'macvlan' and
                           config.get('macvlan_dhcp'))
        if is_macvlan_dhcp:
            service_config['devices'].append('/dev/vhost-net')
            service_config['device_cgroup_rules'] = ['c *:* rwm']

        compose_config = {
            'services': {
                config.get('name', 'windows'): service_config
            }
        }

        # Add volumes if specified
        volumes = self._generate_volumes(config)
        if volumes:
            service = compose_config['services'][config.get('name', 'windows')]
            service['volumes'] = volumes

        # Add network configuration
        networks = self._generate_networks(config)
        if networks:
            if 'networks' not in compose_config:
                compose_config['networks'] = {}
            compose_config['networks'].update(networks)

            # Connect service to networks
            service_networks = self._generate_service_networks(config)
            if service_networks:
                service_name = config.get('name', 'windows')
                service = compose_config['services'][service_name]
                service['networks'] = service_networks
        elif config.get('network_mode') == 'host':
            service_config['network_mode'] = 'host'
        elif config.get('network_mode') == 'static':
            # Static IP configuration
            if config.get('static_ip'):
                compose_config['networks'] = {
                    'dokwinterface_net': {
                        'driver': 'bridge',
                        'ipam': {
                            'config': [{
                                'subnet': config.get('subnet', '172.20.0.0/16'),
                                'gateway': config.get('gateway', '172.20.0.1')
                            }]
                        }
                    }
                }
                service_config['networks'] = {
                    'dokwinterface_net': {
                        'ipv4_address': config['static_ip']
                    }
                }
        elif config.get('network_mode') == 'macvlan':
            # Macvlan network configuration
            network_name = config.get('macvlan_network_name', 'macvlan_net')
            service_config['networks'] = [network_name]
            
            # If container IP is specified, use it
            if config.get('macvlan_container_ip'):
                service_config['networks'] = {
                    network_name: {
                        'ipv4_address': config['macvlan_container_ip']
                    }
                }
        elif config.get('network_mode') == 'none':
            service_config['network_mode'] = 'none'
        elif config.get('network_mode') == 'macvlan':
            # For macvlan, reference the external network
            network_name = config.get('macvlan_network_name', 'macvlan-net')
            service = compose_config['services'][config.get('name', 'windows')]
            service['networks'] = {network_name: {}}
            if config.get('macvlan_ip'):
                ipv4 = config['macvlan_ip']
                service['networks'][network_name]['ipv4_address'] = ipv4

            # Add external network reference
            compose_config['networks'] = {
                network_name: {
                    'external': True
                }
            }
        elif (config.get('network_mode') and
              config.get('network_mode') not in ['static', 'macvlan']):
            service = compose_config['services'][config.get('name', 'windows')]
            service['network_mode'] = config['network_mode']

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
                mem_limit = config['memory_limit']
                deploy_config['resources']['limits']['memory'] = mem_limit
            service = compose_config['services'][config.get('name', 'windows')]
            service['deploy'] = deploy_config

        return yaml.dump(compose_config, default_flow_style=False, sort_keys=False, indent=2)

    def _generate_environment_vars(self, config: Dict[str, Any], for_env_file: bool = False) -> List[str]:
        """Generate environment variables for the container"""
        env_vars = []

        # Basic Windows configuration
        if config.get('username'):
            username = self._escape_env_value(config['username'], for_env_file)
            env_vars.append(f"USERNAME={username}")
        if config.get('password'):
            password = self._escape_env_value(config['password'], for_env_file)
            env_vars.append(f"PASSWORD={password}")
        
        # Windows version
        if config.get('version'):
            env_vars.append(f"VERSION={config['version']}")

        # Version selection and keyboard settings
        if config.get('language'):
            env_vars.append(f"LANGUAGE={config['language']}")
        if config.get('keyboard'):
            env_vars.append(f"KEYBOARD={config['keyboard']}")

        # System resources
        if config.get('cpu_cores'):
            env_vars.append(f"CPU_CORES={config['cpu_cores']}")
        if config.get('ram_size'):
            env_vars.append(f"VERSION={config['version']}")

        # Storage configuration
        if config.get('disk_size'):
            env_vars.append(f"DISK={config['disk_size']}")
        
        # Screen resolution (if provided)
        if config.get('screen_resolution'):
            env_vars.append(f"SCREEN={config['screen_resolution']}")

        # Additional options
        if config.get('enable_kvm', True):
            env_vars.append("KVM=Y")

        if config.get('debug', False):
            env_vars.append("DEBUG=Y")

        # Network configuration
        if config.get('dns_servers'):
            env_vars.append(f"DNS={config['dns_servers']}")
        
        # Macvlan DHCP mode
        is_macvlan_dhcp = (config.get('network_mode') == 'macvlan' and
                           config.get('macvlan_dhcp'))
        if is_macvlan_dhcp:
            env_vars.append("DHCP=Y")

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
    
    def _generate_environment_dict(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate environment variables as dictionary for direct YAML embedding"""
        env_dict = {}
        
        # Basic Windows configuration
        if config.get('username'):
            env_dict['USERNAME'] = str(config['username'])
        if config.get('password'):
            # Escape $ characters for Docker Compose YAML ($ -> $$)
            password = str(config['password'])
            env_dict['PASSWORD'] = password.replace('$', '$$')
        
        # Version selection and keyboard settings
        if config.get('language'):
            env_dict['LANGUAGE'] = str(config['language'])
        if config.get('keyboard'):
            env_dict['KEYBOARD'] = str(config['keyboard'])
        
        # System resources
        if config.get('cpu_cores'):
            env_dict['CPU_CORES'] = str(config['cpu_cores'])
        if config.get('ram_size'):
            env_dict['VERSION'] = str(config['version'])
        
        # Storage configuration
        if config.get('disk_size'):
            env_dict['DISK_SIZE'] = f"{config['disk_size']}G"
        
        # Network configuration
        if config.get('network_mode') == 'host':
            env_dict['NETWORK'] = 'host'
        elif config.get('network_mode') == 'macvlan':
            env_dict['NETWORK'] = 'macvlan'
            if config.get('macvlan_container_ip'):
                env_dict['IP'] = str(config['macvlan_container_ip'])
        elif config.get('network_mode') == 'static':
            if config.get('static_ip'):
                env_dict['IP'] = str(config['static_ip'])
        
        # Additional features
        if config.get('remote_desktop', True):
            env_dict['RDP'] = 'true'
        
        if config.get('web_interface', True):
            env_dict['VNC'] = 'true'
        
        # GPU support
        if config.get('gpu_support'):
            env_dict['GPU'] = 'true'
        
        # Audio support
        if config.get('audio_support'):
            env_dict['AUDIO'] = 'true'
        
        # USB support
        if config.get('usb_support'):
            env_dict['USB'] = 'true'
        
        # File sharing
        if config.get('file_sharing'):
            env_dict['SHARE'] = 'true'
        
        return env_dict
    
    def _escape_env_value(self, value: str, for_env_file: bool = False) -> str:
        """Escape special characters in environment variable values"""
        if not isinstance(value, str):
            return str(value)
        
        if for_env_file:
            # For .env files, use single quotes to prevent variable substitution
            if '$' in value:
                # Use single quotes to prevent any variable substitution
                escaped = value.replace("'", "\\'")
                return f"'{escaped}'"
            # For values without $, use double quotes if they contain special characters
            elif any(char in value for char in [' ', '"', '\\', '&', '|', ';', '(', ')', '<', '>', '`']):
                escaped = value.replace('"', '\\"')
                return f'"{escaped}"'
            return value
        else:
            # For Docker Compose YAML, only quote if value contains spaces
            if ' ' in value:
                escaped = value.replace('"', '\\"')
                escaped = f'"{escaped}"'
                return escaped
            
        return value
    
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
        # Note: Macvlan networks are created externally, not in docker-compose
        
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
    
    def generate_macvlan_setup_script(self, config: Dict[str, Any]) -> str:
        """Generate script to create macvlan network"""
        network_name = config.get('macvlan_network_name', 'macvlan-net')
        parent_interface = config.get('macvlan_parent', 'eth0')
        subnet = config.get('macvlan_subnet', '192.168.1.0/24')
        gateway = config.get('macvlan_gateway', '192.168.1.1')
        ip_range = config.get('macvlan_ip_range', '192.168.1.192/27')
        aux_address = config.get('macvlan_aux_address', '')
        
        script = "#!/bin/bash\n\n"
        script += "# DockWINterface Macvlan Network Setup Script\n"
        script += f"# Generated for container: {config.get('name', 'windows')}\n\n"
        
        script += "# Check if network already exists\n"
        script += f"if docker network ls | grep -q '{network_name}'; then\n"
        script += f"  echo 'Network {network_name} already exists'\n"
        script += "else\n"
        script += "  echo 'Creating macvlan network...'\n"
        script += "  docker network create -d macvlan \\\n"
        script += f"    --subnet={subnet} \\\n"
        script += f"    --gateway={gateway} \\\n"
        script += f"    --ip-range={ip_range} \\\n"
        if aux_address:
            script += f"    --aux-address='host={aux_address}' \\\n"
        script += f"    -o parent={parent_interface} \\\n"
        script += f"    {network_name}\n"
        script += "fi\n\n"
        
        # Add host access configuration if aux_address is provided
        if aux_address and config.get('macvlan_enable_host_access'):
            shim_name = f"{network_name}-shim"
            script += "# Configure host access to macvlan network\n"
            script += f"echo 'Setting up host access via {shim_name}...'\n"
            script += f"sudo ip link add {shim_name} link {parent_interface} type macvlan mode bridge\n"
            script += f"sudo ip addr add {aux_address}/32 dev {shim_name}\n"
            script += f"sudo ip link set {shim_name} up\n"
            script += f"sudo ip route add {ip_range} dev {shim_name}\n"
            script += f"echo 'Host can now communicate with containers via {aux_address}'\n\n"
        
        script += "echo 'Macvlan network setup complete!'\n"
        return script
    
    def generate_env_file(self, config: Dict[str, Any]) -> str:
        """Generate .env file content"""
        env_content = "# DockWINterface Generated Environment File\n"
        env_content += f"# Generated for container: {config.get('name', 'windows')}\n\n"
        
        env_vars = self._generate_environment_vars(config, for_env_file=True)
        for var in env_vars:
            env_content += f"{var}\n"
        
        # Debug logging for password escaping
        if config.get('password'):
            logging.info(f"Original password: {config.get('password')}")
            escaped_password = self._escape_env_value(config.get('password'), for_env_file=True)
            logging.info(f"Escaped password: {escaped_password}")
        
        # Additional Docker-specific settings
        env_content += "\n# Container Configuration\n"
        env_content += f"CONTAINER_NAME={config.get('name', 'windows')}\n"
        env_content += f"RDP_PORT={config.get('rdp_port', '3389')}\n"
        env_content += f"VNC_PORT={config.get('vnc_port', '8006')}\n"
        
        logging.info(f"Generated .env file content:\n{env_content}")
        return env_content
    
    def validate_macvlan_config(self, config: Dict[str, Any]) -> List[str]:
        """Validate macvlan-specific configuration"""
        errors = []
        
        if config.get('network_mode') == 'macvlan':
            # Check required macvlan fields
            if not config.get('macvlan_subnet'):
                errors.append("Macvlan subnet is required (e.g., 192.168.1.0/24)")
            
            if not config.get('macvlan_gateway'):
                errors.append("Macvlan gateway is required (e.g., 192.168.1.1)")
            
            if not config.get('macvlan_parent'):
                errors.append("Parent network interface is required (e.g., eth0)")
            
            # Validate IP format if static IP is provided
            if config.get('macvlan_ip'):
                import re
                ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
                if not re.match(ip_pattern, config['macvlan_ip']):
                    errors.append("Invalid macvlan IP address format")
            
            # Validate subnet format
            if config.get('macvlan_subnet'):
                import re
                subnet_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$'
                if not re.match(subnet_pattern, config['macvlan_subnet']):
                    errors.append("Invalid subnet format (use CIDR notation, e.g., 192.168.1.0/24)")
        
        return errors
    
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
        
        # Validate macvlan configuration if applicable
        macvlan_errors = self.validate_macvlan_config(config)
        errors.extend(macvlan_errors)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def save_config_files(self, config: Dict[str, Any]):
        """Save generated configuration files to disk"""
        container_name = config.get('name', 'windows')
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
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
        
        # Save macvlan setup script if using macvlan
        script_path = None
        if config.get('network_mode') == 'macvlan':
            macvlan_script = self.generate_macvlan_setup_script(config)
            script_path = os.path.join(self.output_dir, f"{container_name}-setup-macvlan.sh")
            with open(script_path, 'w') as f:
                f.write(macvlan_script)
            # Make script executable
            os.chmod(script_path, 0o755)
        
        logging.info(f"Configuration files saved for {container_name}")
        
        result = {
            'docker_compose_path': compose_path,
            'env_path': env_path,
            'config_path': config_path
        }
        if script_path:
            result['macvlan_script_path'] = script_path
        
        return result


class RemoteDockerDeployer:
    def __init__(self, docker_host: str):
        self.docker_host = docker_host
        
    def deploy(self, config: Dict[str, Any], docker_compose: str, env_file: str = None) -> Dict[str, Any]:
        """Deploy container to remote Docker host"""
        try:
            container_name = config.get('name', 'windows')
            
            # Parse docker-compose YAML to extract configuration
            import yaml
            compose_data = yaml.safe_load(docker_compose)
            service_config = compose_data.get('services', {}).get(container_name, {})
            
            # Set DOCKER_HOST environment variable only for TCP connections
            env = os.environ.copy()
            if self.docker_host.startswith('tcp://'):
                env['DOCKER_HOST'] = self.docker_host
            
            # Build docker run command
            cmd = ['docker', 'run', '-d', '--name', container_name]
            
            # Add ports
            if 'ports' in service_config:
                for port in service_config['ports']:
                    cmd.extend(['-p', port])
            
            # Add environment variables
            if 'environment' in service_config:
                for key, value in service_config['environment'].items():
                    # Ensure value is a string and properly formatted
                    value_str = str(value) if value is not None else ''
                    cmd.extend(['-e', f"{key}={value_str}"])
            
            # Add volumes
            if 'volumes' in service_config:
                for volume in service_config['volumes']:
                    cmd.extend(['-v', volume])
            
            # Add restart policy
            if 'restart' in service_config:
                cmd.extend(['--restart', service_config['restart']])
            
            # Add network mode
            if 'network_mode' in service_config:
                cmd.extend(['--network', service_config['network_mode']])
            
            # Add privileged if needed
            if service_config.get('privileged'):
                cmd.append('--privileged')
            
            # Add capabilities
            if 'cap_add' in service_config:
                for cap in service_config['cap_add']:
                    cmd.extend(['--cap-add', cap])
            
            # Add devices - check if they exist first
            if 'devices' in service_config:
                for device in service_config['devices']:
                    # Skip /dev/kvm if it doesn't exist (common in containers)
                    if device == '/dev/kvm' and not os.path.exists(device):
                        logging.warning(f"Skipping device {device} as it doesn't exist")
                        continue
                    cmd.extend(['--device', device])
            
            # Add image - ensure it exists
            image = service_config.get('image', 'dockurr/windows')
            cmd.append(image)
            
            logging.info(f"Deploying container with command: {' '.join(cmd)}")
            print(f"DEBUG: Docker command: {' '.join(cmd)}")  # Debug output
            
            # First, stop and remove any existing container with the same name
            stop_cmd = ['docker', 'stop', container_name]
            subprocess.run(stop_cmd, env=env, capture_output=True, text=True, timeout=30)
            
            rm_cmd = ['docker', 'rm', container_name]
            subprocess.run(rm_cmd, env=env, capture_output=True, text=True, timeout=30)
            
            # Deploy container
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            print(f"DEBUG: Docker run result - returncode: {result.returncode}, stdout: {result.stdout}, stderr: {result.stderr}")  # Debug output
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                
                return {
                    'success': True,
                    'container_id': container_id,
                    'output': f"Container {container_name} deployed successfully"
                }
            else:
                return {
                    'success': False,
                    'error': f"Docker deployment failed: {result.stderr}",
                    'output': result.stdout
                }
                    
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Deployment timed out after 5 minutes'
            }
        except Exception as e:
            logging.error(f"Remote deployment error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Deployment failed: {str(e)}"
            }
