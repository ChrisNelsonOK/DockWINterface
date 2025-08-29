#!/usr/bin/env python3
"""SSH tunnel support for secure remote Docker access"""

import os
import socket
import select
import threading
import paramiko
import subprocess
import tempfile
import time
import logging
from typing import Dict, Any, Optional, Tuple
from contextlib import contextmanager

class SSHDockerTunnel:
    """Manages SSH tunnel for Docker access"""
    
    def __init__(self, ssh_host: str, ssh_user: str, ssh_password: str = None, 
                 ssh_key_path: str = None, ssh_port: int = 22, 
                 docker_port: int = 2375):
        """
        Initialize SSH tunnel for Docker access
        
        Args:
            ssh_host: Remote host address
            ssh_user: SSH username
            ssh_password: SSH password (optional if using key)
            ssh_key_path: Path to SSH private key (optional if using password)
            ssh_port: SSH port (default 22)
            docker_port: Docker daemon port on remote (default 2375)
        """
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_password = ssh_password
        self.ssh_key_path = ssh_key_path
        self.ssh_port = ssh_port
        self.docker_port = docker_port
        self.local_port = None
        self.ssh_client = None
        self.tunnel_thread = None
        self.stop_tunnel = threading.Event()
        
    def _find_free_port(self) -> int:
        """Find a free local port for the tunnel"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
        
    def _create_ssh_client(self) -> paramiko.SSHClient:
        """Create and connect SSH client"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_kwargs = {
            'hostname': self.ssh_host,
            'port': self.ssh_port,
            'username': self.ssh_user,
        }
        
        if self.ssh_key_path:
            # Use SSH key authentication
            if os.path.exists(os.path.expanduser(self.ssh_key_path)):
                connect_kwargs['key_filename'] = os.path.expanduser(self.ssh_key_path)
            else:
                raise FileNotFoundError(f"SSH key not found: {self.ssh_key_path}")
        elif self.ssh_password:
            # Use password authentication
            connect_kwargs['password'] = self.ssh_password
        else:
            # Try default SSH keys
            connect_kwargs['look_for_keys'] = True
            
        client.connect(**connect_kwargs)
        return client
        
    def _tunnel_handler(self, local_port: int):
        """Handle tunnel connections"""
        local_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        local_socket.bind(('127.0.0.1', local_port))
        local_socket.listen(5)
        local_socket.settimeout(1.0)
        
        logging.info(f"SSH tunnel listening on 127.0.0.1:{local_port}")
        
        while not self.stop_tunnel.is_set():
            try:
                client_socket, addr = local_socket.accept()
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Tunnel accept error: {e}")
                break
                
            try:
                # Create channel to Docker daemon
                transport = self.ssh_client.get_transport()
                channel = transport.open_channel(
                    'direct-tcpip',
                    ('localhost', self.docker_port),
                    ('127.0.0.1', local_port)
                )
                
                # Start forwarding thread
                threading.Thread(
                    target=self._forward_tunnel,
                    args=(client_socket, channel),
                    daemon=True
                ).start()
                
            except Exception as e:
                logging.error(f"Channel creation error: {e}")
                client_socket.close()
                
        local_socket.close()
        
    def _forward_tunnel(self, local_socket: socket.socket, channel: paramiko.Channel):
        """Forward data between local socket and SSH channel"""
        try:
            while True:
                r, w, x = select.select([local_socket, channel], [], [], 1)
                
                if local_socket in r:
                    data = local_socket.recv(4096)
                    if not data:
                        break
                    channel.send(data)
                    
                if channel in r:
                    data = channel.recv(4096)
                    if not data:
                        break
                    local_socket.send(data)
                    
        except Exception as e:
            logging.debug(f"Tunnel forwarding ended: {e}")
        finally:
            channel.close()
            local_socket.close()
            
    def start(self) -> str:
        """
        Start SSH tunnel and return local Docker endpoint
        
        Returns:
            Docker endpoint URL (e.g., tcp://localhost:12345)
        """
        if self.ssh_client:
            raise RuntimeError("Tunnel already started")
            
        # Connect SSH
        self.ssh_client = self._create_ssh_client()
        
        # Find free local port
        self.local_port = self._find_free_port()
        
        # Start tunnel thread
        self.stop_tunnel.clear()
        self.tunnel_thread = threading.Thread(
            target=self._tunnel_handler,
            args=(self.local_port,),
            daemon=True
        )
        self.tunnel_thread.start()
        
        # Give tunnel time to start
        time.sleep(0.5)
        
        return f"tcp://localhost:{self.local_port}"
        
    def stop(self):
        """Stop SSH tunnel"""
        if self.ssh_client:
            self.stop_tunnel.set()
            if self.tunnel_thread:
                self.tunnel_thread.join(timeout=2)
            self.ssh_client.close()
            self.ssh_client = None
            self.local_port = None
            
    def __enter__(self):
        """Context manager entry"""
        return self.start()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        

class SSHRemoteDockerDeployer:
    """Deploy Docker containers via SSH tunnel"""
    
    def __init__(self, ssh_config: Dict[str, Any]):
        """
        Initialize SSH Docker deployer
        
        Args:
            ssh_config: Dictionary with SSH connection details
                - host: SSH host address
                - user: SSH username
                - password: SSH password (optional)
                - key_path: Path to SSH key (optional)
                - port: SSH port (default 22)
        """
        self.ssh_config = ssh_config
        
    def deploy(self, config: Dict[str, Any], docker_compose: str) -> Dict[str, Any]:
        """
        Deploy container via SSH
        
        Args:
            config: Container configuration
            docker_compose: Docker Compose YAML content
            
        Returns:
            Deployment result dictionary
        """
        try:
            # Connect directly via SSH instead of using tunnel
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': self.ssh_config['host'],
                'port': self.ssh_config.get('port', 22),
                'username': self.ssh_config['username'],
            }
            
            if self.ssh_config.get('password'):
                connect_kwargs['password'] = self.ssh_config['password']
            elif self.ssh_config.get('key_path'):
                connect_kwargs['key_filename'] = os.path.expanduser(self.ssh_config['key_path'])
            
            logging.info(f"Connecting to SSH host {self.ssh_config['host']}")
            ssh_client.connect(**connect_kwargs)
            
            try:
                # Parse docker-compose to extract configuration
                import yaml
                compose_data = yaml.safe_load(docker_compose)
                container_name = config.get('name', 'windows')
                service_config = compose_data.get('services', {}).get(container_name, {})
                
                # Build docker run command
                cmd_parts = ['docker', 'run', '-d', '--name', container_name]
                
                # Add ports
                if 'ports' in service_config:
                    for port in service_config['ports']:
                        cmd_parts.extend(['-p', port])
                
                # Add environment variables
                    # Use proper RFC 1918 private IP for internal VM network instead of Microsoft public IP space
                    if "VM_NET_IP" not in service_config.get("environment", {}):
                        cmd_parts.extend(["-e", "VM_NET_IP=192.254.254.21"])
                if 'environment' in service_config:
                    for key, value in service_config['environment'].items():
                        # Ensure value is a string and escape for shell
                        value_str = str(value)
                        # For sensitive values like passwords, use single quotes to prevent shell expansion
                        if key == 'PASSWORD' and ('$' in value_str or '"' in value_str):
                            # Remove any existing quotes from Docker Compose YAML and wrap in single quotes
                            clean_password = value_str.strip('"\'')
                            cmd_parts.extend(['-e', f"{key}='{clean_password}'"])
                        else:
                            cmd_parts.extend(['-e', f"{key}={value_str}"])
                
                # Add volumes
                if 'volumes' in service_config:
                    for volume in service_config['volumes']:
                        cmd_parts.extend(['-v', volume])
                
                # Add restart policy
                if 'restart' in service_config:
                    cmd_parts.extend(['--restart', service_config['restart']])
                
                # Add stop timeout (convert stop_grace_period to --stop-timeout)
                if 'stop_grace_period' in service_config:
                    grace_period = service_config['stop_grace_period']
                    # Convert from docker-compose format (e.g., "2m") to seconds
                    if isinstance(grace_period, str):
                        if grace_period.endswith('m'):
                            timeout_seconds = int(grace_period[:-1]) * 60
                        elif grace_period.endswith('s'):
                            timeout_seconds = int(grace_period[:-1])
                        else:
                            timeout_seconds = int(grace_period)
                    else:
                        timeout_seconds = int(grace_period)
                    cmd_parts.extend(['--stop-timeout', str(timeout_seconds)])
                
                # Add network mode
                if 'network_mode' in service_config:
                    cmd_parts.extend(['--network', service_config['network_mode']])
                
                # Add privileged if needed
                if service_config.get('privileged'):
                    cmd_parts.append('--privileged')
                
                # Add capabilities
                if 'cap_add' in service_config:
                    for cap in service_config['cap_add']:
                        cmd_parts.extend(['--cap-add', cap])
                
                # Add devices - check if they exist on remote host first
                if 'devices' in service_config:
                    for device in service_config['devices']:
                        # Check if device exists on remote host
                        check_cmd = f"test -e {device} && echo 'exists'"
                        stdin, stdout, stderr = ssh_client.exec_command(check_cmd)
                        result = stdout.read().decode().strip()
                        
                        if result == 'exists':
                            cmd_parts.extend(['--device', device])
                            logging.info(f"Adding device {device} to container")
                        else:
                            logging.warning(f"Device {device} not found on remote host, skipping")
                
                # Add image
                cmd_parts.append(service_config['image'])
                
                # Build the full command string
                docker_cmd = ' '.join(cmd_parts)
                logging.info(f"Running Docker command on remote host: {docker_cmd}")
                
                # First stop and remove any existing container
                logging.info("Stopping and removing existing container if present")
                stdin, stdout, stderr = ssh_client.exec_command(f"docker stop {container_name} 2>/dev/null; docker rm {container_name} 2>/dev/null")
                stdout.read()  # Wait for completion
                
                # Run docker command on remote host
                logging.info("Executing Docker run command on remote host")
                logging.info(f"Full command: {docker_cmd}")
                stdin, stdout, stderr = ssh_client.exec_command(docker_cmd)
                
                # Get output
                output = stdout.read().decode()
                error = stderr.read().decode()
                exit_status = stdout.channel.recv_exit_status()
                
                logging.info(f"Docker command exit status: {exit_status}")
                logging.info(f"Docker stdout: {output}")
                if error:
                    logging.error(f"Docker stderr: {error}")
                
                if exit_status != 0:
                    error_msg = error if error else output
                    logging.error(f"Docker run failed: {error_msg}")
                    
                    # Try to get Docker version for debugging
                    stdin, stdout, stderr = ssh_client.exec_command("docker version")
                    version_output = stdout.read().decode()
                    logging.info(f"Docker version on remote host: {version_output}")
                    
                    return {
                        'success': False,
                        'error': f"Docker deployment failed: {error_msg}"
                    }
                
                # Success - get container info
                container_id = output.strip()

                # Handle post-creation network connection for macvlan via SSH
                if (config.get("network_mode") == "macvlan" and config.get("macvlan_ip") and
                    service_config.get("network_mode") != "macvlan"):
                    # Container was created with bridge network, now connect to macvlan via SSH
                    network_name = config.get("macvlan_network_name", "macvlan")
                    macvlan_ip = config["macvlan_ip"]
                    
                    logging.info(f"Connecting container to macvlan network {network_name} with IP {macvlan_ip} via SSH")
                    
                    # Disconnect from bridge network first
                    disconnect_ssh_cmd = f"docker network disconnect bridge {container_name}"
                    stdin, stdout, stderr = ssh_client.exec_command(disconnect_ssh_cmd)
                    stdout.read()  # Wait for completion
                    
                    # Connect to macvlan network with specific IP
                    connect_ssh_cmd = f"docker network connect --ip {macvlan_ip} {network_name} {container_name}"
                    stdin, stdout, stderr = ssh_client.exec_command(connect_ssh_cmd)
                    connect_output = stdout.read().decode()
                    connect_error = stderr.read().decode()
                    
                    if connect_error:
                        logging.warning(f"Failed to connect to macvlan network via SSH: {connect_error}")
                    else:
                        logging.info(f"Successfully connected container to macvlan network with IP {macvlan_ip} via SSH")

                logging.info(f"Container deployed successfully with ID: {container_id}")
                
                # Get container details and check ports
                stdin, stdout, stderr = ssh_client.exec_command(f"docker inspect {container_name}")
                inspect_output = stdout.read().decode()
                
                # Check container status and ports
                stdin, stdout, stderr = ssh_client.exec_command(f"docker ps -a --filter name={container_name} --format 'table {{{{.Status}}}}\\t{{{{.Ports}}}}'")
                status_output = stdout.read().decode()
                logging.info(f"Container status and ports: {status_output}")
                
                # Get logs to check if container started properly
                stdin, stdout, stderr = ssh_client.exec_command(f"docker logs {container_name} --tail 20")
                logs_output = stdout.read().decode()
                logging.info(f"Container logs: {logs_output}")
                
                return {
                    'success': True,
                    'message': f"Container '{container_name}' deployed successfully via SSH to {self.ssh_config['host']}",
                    'container_name': container_name,
                    'container_id': container_id,
                    'output': output,
                    'status': status_output,
                    'logs': logs_output
                }
                
            finally:
                ssh_client.close()
                    
        except paramiko.AuthenticationException as e:
            return {
                'success': False,
                'error': f"SSH authentication failed: {str(e)}"
            }
        except paramiko.SSHException as e:
            return {
                'success': False,
                'error': f"SSH connection failed: {str(e)}"
            }
        except Exception as e:
            logging.error(f"SSH Docker deployment error: {e}")
            return {
                'success': False,
                'error': f"SSH deployment failed: {str(e)}"
            }
