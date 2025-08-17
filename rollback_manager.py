#!/usr/bin/env python3
"""
Rollback Manager for DockWINterface
Integrates with RevertIT to provide automatic rollback capabilities
for Docker deployments
"""

import time
import json
import subprocess
import logging
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import shutil


class RollbackManager:
    """Manages configuration rollback and system state recovery"""

    def __init__(self):
        self.is_linux = platform.system().lower() == 'linux'
        self.revertit_available = self._check_revertit_available()
        self.snapshot_dir = Path("/var/lib/dockwinterface/snapshots")
        self.config_dir = Path("/etc/dockwinterface")
        self.rollback_enabled = False
        self.active_checkpoints = {}
        self.timeout_defaults = {
            'network': 300,  # 5 minutes for network changes
            'container': 180,  # 3 minutes for container deployments
            'system': 600,    # 10 minutes for system-wide changes
            'macvlan': 420    # 7 minutes for macvlan (higher risk)
        }

        # Create directories if they don't exist
        if self.is_linux:
            self.snapshot_dir.mkdir(parents=True, exist_ok=True)
            self.config_dir.mkdir(parents=True, exist_ok=True)

    def _check_revertit_available(self) -> bool:
        """Check if RevertIT is installed and available"""
        if not self.is_linux:
            return False

        try:
            result = subprocess.run(['which', 'revertit'],
                                    capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Execute a system command and return result"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=30)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_checkpoint(self, change_type: str, config: Dict[str, Any],
                          description: Optional[str] = None) -> Dict[str, Any]:
        """Create a checkpoint before making changes"""
        if not self.is_linux:
            return {
                'success': False,
                'error': 'Rollback feature only available on Linux',
                'checkpoint_id': None
            }

        checkpoint_id = f"{change_type}_{int(time.time())}"
        checkpoint_path = self.snapshot_dir / checkpoint_id

        try:
            # Create checkpoint directory
            checkpoint_path.mkdir(parents=True, exist_ok=True)

            # Save current configuration
            config_file = checkpoint_path / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            # Save Docker state
            self._save_docker_state(checkpoint_path)

            # Save network configuration
            self._save_network_state(checkpoint_path)

            # If RevertIT is available, create system snapshot
            if self.revertit_available:
                desc = description or \
                    f"DockWINterface checkpoint: {change_type}"
                cmd = ['revertit', 'snapshot', 'create', '--description', desc]
                result = self._run_command(cmd)
                if result['success']:
                    logging.info(f"RevertIT snapshot created: {desc}")

            # Store checkpoint info
            self.active_checkpoints[checkpoint_id] = {
                'created': datetime.now().isoformat(),
                'type': change_type,
                'timeout': self.timeout_defaults.get(change_type, 300),
                'config': config,
                'path': str(checkpoint_path),
                'confirmed': False
            }

            # Save checkpoint metadata
            meta_file = checkpoint_path / "metadata.json"
            with open(meta_file, 'w') as f:
                json.dump(self.active_checkpoints[checkpoint_id], f, indent=2)

            logging.info(f"Checkpoint created: {checkpoint_id}")

            return {
                'success': True,
                'checkpoint_id': checkpoint_id,
                'timeout': self.timeout_defaults.get(change_type, 300),
                'path': str(checkpoint_path)
            }

        except Exception as e:
            logging.error(f"Failed to create checkpoint: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'checkpoint_id': None
            }

    def _save_docker_state(self, checkpoint_path: Path):
        """Save current Docker state"""
        docker_state = {}

        # Get running containers
        result = self._run_command(['docker', 'ps', '--format', 'json'])
        if result['success']:
            docker_state['containers'] = result['stdout']

        # Get networks
        result = self._run_command(
            ['docker', 'network', 'ls', '--format', 'json']
        )
        if result['success']:
            docker_state['networks'] = result['stdout']

        # Get volumes
        result = self._run_command(['docker', 'volume', 'ls', '--format', 'json'])
        if result['success']:
            docker_state['volumes'] = result['stdout']

        # Save Docker compose files if they exist
        compose_files = Path(
            "/var/lib/dockwinterface/generated_configs"
        ).glob("*.yml")
        docker_state['compose_files'] = {}
        for file in compose_files:
            if file.exists():
                docker_state['compose_files'][file.name] = file.read_text()

        # Save state
        state_file = checkpoint_path / "docker_state.json"
        with open(state_file, 'w') as f:
            json.dump(docker_state, f, indent=2)

    def _save_network_state(self, checkpoint_path: Path):
        """Save current network configuration"""
        network_state = {}

        # Get network interfaces
        result = self._run_command(['ip', 'addr', 'show'])
        if result['success']:
            network_state['interfaces'] = result['stdout']

        # Get routing table
        result = self._run_command(['ip', 'route', 'show'])
        if result['success']:
            network_state['routes'] = result['stdout']

        # Get iptables rules
        result = self._run_command(['iptables-save'])
        if result['success']:
            network_state['iptables'] = result['stdout']

        # Backup critical network configs
        network_configs = [
            '/etc/network/interfaces',
            '/etc/netplan/',
            '/etc/systemd/network/',
            '/etc/NetworkManager/system-connections/'
        ]

        network_state['config_files'] = {}
        for config_path in network_configs:
            path = Path(config_path)
            if path.exists():
                if path.is_file():
                    network_state['config_files'][config_path] = path.read_text()
                elif path.is_dir():
                    # Backup directory contents
                    backup_dir = checkpoint_path / f"network_configs/{path.name}"
                    shutil.copytree(path, backup_dir,
                                    dirs_exist_ok=True)

        # Save state
        state_file = checkpoint_path / "network_state.json"
        with open(state_file, 'w') as f:
            json.dump(network_state, f, indent=2)

    def start_monitoring(self, checkpoint_id: str,
                         connectivity_check: bool = True) -> Dict[str, Any]:
        """Start monitoring for the checkpoint with auto-rollback on failure"""
        if checkpoint_id not in self.active_checkpoints:
            return {'success': False, 'error': 'Invalid checkpoint ID'}

        checkpoint = self.active_checkpoints[checkpoint_id]

        # If RevertIT is available, use it for monitoring
        if self.revertit_available and connectivity_check:
            timeout = checkpoint['timeout']
            cmd = ['revertit', 'monitor', '--timeout', str(timeout),
                   '--checkpoint', checkpoint_id]

            # Run in background
            subprocess.Popen(cmd)
            logging.info(f"RevertIT monitoring started for {checkpoint_id}")

        # Start our own monitoring thread
        import threading
        monitor_thread = threading.Thread(
            target=self._monitor_checkpoint,
            args=(checkpoint_id, connectivity_check)
        )
        monitor_thread.daemon = True
        monitor_thread.start()

        return {
            'success': True,
            'checkpoint_id': checkpoint_id,
            'timeout': checkpoint['timeout'],
            'monitoring': True
        }

    def _monitor_checkpoint(self, checkpoint_id: str,
                            connectivity_check: bool = True):
        """Monitor checkpoint and trigger rollback if needed"""
        checkpoint = self.active_checkpoints.get(checkpoint_id)
        if not checkpoint:
            return

        timeout = checkpoint['timeout']
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if confirmed
            if checkpoint.get('confirmed'):
                logging.info(f"Checkpoint {checkpoint_id} confirmed")
                return

            # Check connectivity if required
            if connectivity_check and not self._check_connectivity():
                logging.warning(f"Connectivity lost for {checkpoint_id}")
                self.trigger_rollback(checkpoint_id,
                                      reason="Connectivity lost")
                return

            # Check Docker health for container deployments
            if checkpoint['type'] in ['container', 'macvlan']:
                if not self._check_docker_health(checkpoint['config']):
                    logging.warning(
                        f"Docker health check failed for {checkpoint_id}"
                    )
                    self.trigger_rollback(
                        checkpoint_id,
                        reason="Container health check failed"
                    )
                    return

            time.sleep(5)  # Check every 5 seconds

        # Timeout reached without confirmation
        logging.warning(f"Checkpoint {checkpoint_id} timeout reached")
        self.trigger_rollback(checkpoint_id,
                              reason="Timeout without confirmation")

    def _check_connectivity(self) -> bool:
        """Check network connectivity"""
        test_hosts = ['8.8.8.8', '1.1.1.1', 'google.com']

        for host in test_hosts:
            result = self._run_command(['ping', '-c', '1', '-W', '2', host])
            if result['success']:
                return True

        return False

    def _check_docker_health(self, config: Dict[str, Any]) -> bool:
        """Check Docker container health"""
        container_name = config.get('name', 'windows')

        # Check if container exists and is running
        result = self._run_command([
            'docker', 'inspect',
            '--format', '{{.State.Running}}',
            container_name
        ])

        if not result['success'] or result['stdout'].strip() != 'true':
            return False

        # Check container health status if available
        result = self._run_command([
            'docker', 'inspect',
            '--format', '{{.State.Health.Status}}',
            container_name
        ])

        if result['success']:
            health_status = result['stdout'].strip()
            if health_status in ['healthy', 'starting', '']:
                return True

        return False

    def confirm_change(self, checkpoint_id: str) -> Dict[str, Any]:
        """Confirm a change to prevent rollback"""
        if checkpoint_id not in self.active_checkpoints:
            return {'success': False, 'error': 'Invalid checkpoint ID'}

        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint['confirmed'] = True

        # Update metadata file
        checkpoint_path = Path(checkpoint['path'])
        meta_file = checkpoint_path / "metadata.json"
        with open(meta_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        # If using RevertIT, confirm there too
        if self.revertit_available:
            cmd = ['revertit', 'confirm', checkpoint_id]
            self._run_command(cmd)

        logging.info(f"Checkpoint {checkpoint_id} confirmed")

        return {
            'success': True,
            'checkpoint_id': checkpoint_id,
            'confirmed': True
        }

    def confirm_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Backward-compatible alias used by routes.py.
        Delegates to confirm_change to maintain existing behavior.
        """
        return self.confirm_change(checkpoint_id)

    def trigger_rollback(self, checkpoint_id: str,
                         reason: str = "Manual trigger") -> Dict[str, Any]:
        """Trigger a rollback to a checkpoint"""
        if checkpoint_id not in self.active_checkpoints:
            return {'success': False, 'error': 'Invalid checkpoint ID'}

        checkpoint = self.active_checkpoints[checkpoint_id]
        checkpoint_path = Path(checkpoint['path'])

        logging.warning(f"Triggering rollback for {checkpoint_id}: {reason}")

        try:
            # Restore Docker state
            docker_state_file = checkpoint_path / "docker_state.json"
            if docker_state_file.exists():
                self._restore_docker_state(docker_state_file)

            # Restore network state
            network_state_file = checkpoint_path / "network_state.json"
            if network_state_file.exists():
                self._restore_network_state(checkpoint_path)

            # If using RevertIT, trigger its rollback
            if self.revertit_available:
                cmd = ['revertit', 'revert', checkpoint_id]
                self._run_command(cmd)

            # Mark as rolled back
            checkpoint['rolled_back'] = True
            checkpoint['rollback_reason'] = reason
            checkpoint['rollback_time'] = datetime.now().isoformat()

            # Save rollback info
            rollback_file = checkpoint_path / "rollback_info.json"
            with open(rollback_file, 'w') as f:
                json.dump({
                    'reason': reason,
                    'time': checkpoint['rollback_time'],
                    'checkpoint_id': checkpoint_id
                }, f, indent=2)

            logging.info(f"Rollback completed for {checkpoint_id}")

            return {
                'success': True,
                'checkpoint_id': checkpoint_id,
                'reason': reason,
                'rolled_back': True
            }

        except Exception as e:
            logging.error(f"Rollback failed for {checkpoint_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'checkpoint_id': checkpoint_id
            }

    def _restore_docker_state(self, state_file: Path):
        """Restore Docker state from checkpoint"""
        with open(state_file, 'r') as f:
            docker_state = json.load(f)

        # Restore compose files
        if 'compose_files' in docker_state:
            for filename, content in docker_state['compose_files'].items():
                target_path = Path(
                    f"/var/lib/dockwinterface/generated_configs/{filename}"
                )
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_path, 'w') as f:
                    f.write(content)

        # Note: Full container restoration would require more complex logic
        # This is a simplified version
        logging.info("Docker state restoration initiated")

    def _restore_network_state(self, checkpoint_path: Path):
        """Restore network configuration from checkpoint"""
        # Restore backed up network configs
        network_backup = checkpoint_path / "network_configs"
        if network_backup.exists():
            for backup_dir in network_backup.iterdir():
                if backup_dir.is_dir():
                    target = Path(f"/etc/{backup_dir.name}")
                    if target.exists():
                        shutil.rmtree(target, ignore_errors=True)
                    shutil.copytree(backup_dir, target)

        # Restart networking service
        self._run_command(['systemctl', 'restart', 'networking'])
        logging.info("Network state restoration completed")

    def get_rollback_history(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get history of rollbacks.
        If 'days' is provided, only include checkpoints created within
        the last 'days' days.
        """
        history: List[Dict[str, Any]] = []

        if not self.snapshot_dir.exists():
            return history

        for checkpoint_dir in self.snapshot_dir.iterdir():
            if checkpoint_dir.is_dir():
                meta_file = checkpoint_dir / "metadata.json"
                rollback_file = checkpoint_dir / "rollback_info.json"

                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)

                    entry = {
                        'checkpoint_id': checkpoint_dir.name,
                        'created': metadata.get('created'),
                        'type': metadata.get('type'),
                        'confirmed': metadata.get('confirmed', False)
                    }

                    if rollback_file.exists():
                        with open(rollback_file, 'r') as f:
                            rollback_info = json.load(f)
                        entry['rolled_back'] = True
                        entry['rollback_reason'] = rollback_info.get('reason')
                        entry['rollback_time'] = rollback_info.get('time')
                    else:
                        entry['rolled_back'] = False

                    history.append(entry)

        # Optionally filter by days
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)

            def _parse_created(ts: str) -> datetime:
                try:
                    return datetime.fromisoformat(ts)
                except Exception:
                    return datetime.min

            history = [
                h for h in history
                if h.get('created') and _parse_created(h['created']) >= cutoff_date
            ]

        # Sort by creation time
        history.sort(key=lambda x: x.get('created', ''), reverse=True)

        return history

    def cleanup_old_checkpoints(self, days_to_keep: int = 7):
        """Clean up old checkpoints"""
        if not self.snapshot_dir.exists():
            return

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        for checkpoint_dir in self.snapshot_dir.iterdir():
            if checkpoint_dir.is_dir():
                meta_file = checkpoint_dir / "metadata.json"

                if meta_file.exists():
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)

                    created = datetime.fromisoformat(
                        metadata.get('created', '')
                    )

                    if created < cutoff_date:
                        shutil.rmtree(checkpoint_dir)
                        logging.info(
                            f"Cleaned up old checkpoint: {checkpoint_dir.name}"
                        )
