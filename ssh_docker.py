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
        Deploy container via SSH tunnel
        
        Args:
            config: Container configuration
            docker_compose: Docker Compose YAML content
            
        Returns:
            Deployment result dictionary
        """
        try:
            # Create SSH tunnel
            tunnel = SSHDockerTunnel(
                ssh_host=self.ssh_config['host'],
                ssh_user=self.ssh_config['user'],
                ssh_password=self.ssh_config.get('password'),
                ssh_key_path=self.ssh_config.get('key_path'),
                ssh_port=self.ssh_config.get('port', 22)
            )
            
            # Use tunnel for deployment
            with tunnel as docker_endpoint:
                logging.info(f"SSH tunnel established: {docker_endpoint}")
                
                # Create temporary compose file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
                    f.write(docker_compose)
                    compose_path = f.name
                    
                try:
                    # Run docker-compose via tunnel
                    env = os.environ.copy()
                    env['DOCKER_HOST'] = docker_endpoint
                    
                    # Deploy container
                    cmd = ['docker-compose', '-f', compose_path, 'up', '-d']
                    result = subprocess.run(
                        cmd, 
                        env=env, 
                        capture_output=True, 
                        text=True, 
                        timeout=300
                    )
                    
                    if result.returncode == 0:
                        container_name = config.get('name', 'windows')
                        
                        # Get container info
                        info_cmd = ['docker', 'inspect', container_name]
                        info_result = subprocess.run(
                            info_cmd,
                            env=env,
                            capture_output=True,
                            text=True
                        )
                        
                        return {
                            'success': True,
                            'message': f"Container '{container_name}' deployed successfully via SSH",
                            'container_name': container_name,
                            'output': result.stdout
                        }
                    else:
                        return {
                            'success': False,
                            'error': f"Deployment failed: {result.stderr}"
                        }
                        
                finally:
                    # Clean up temp file
                    os.unlink(compose_path)
                    
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
