#!/usr/bin/env python3
"""Unit tests for DockerConfigGenerator"""

import unittest
import tempfile
import os
import json
import yaml
from docker_config import DockerConfigGenerator


class TestDockerConfigGenerator(unittest.TestCase):
    """Test cases for DockerConfigGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = DockerConfigGenerator()
        # Override the output directory for testing
        self.generator.output_dir = self.temp_dir
        self.test_config = {
            'name': 'test-windows',
            'version': 'win11',
            'username': 'testuser',
            'password': 'TestPass123!',
            'cpu_cores': 4,
            'ram_size': 8,
            'disk_size': 64,
            'enable_kvm': True
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_config_valid(self):
        """Test validation with valid configuration"""
        result = self.generator.validate_config(self.test_config)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_config_missing_required(self):
        """Test validation with missing required fields"""
        invalid_config = {'name': 'test'}
        result = self.generator.validate_config(invalid_config)
        self.assertFalse(result['valid'])
        self.assertIn('Missing required field', str(result['errors']))
    
    def test_validate_config_invalid_name(self):
        """Test validation with invalid container name"""
        config = self.test_config.copy()
        config['name'] = 'invalid name!'
        result = self.generator.validate_config(config)
        self.assertFalse(result['valid'])
        self.assertIn('Container name can only contain', str(result['errors']))
    
    def test_validate_config_resource_limits(self):
        """Test validation with excessive resource limits"""
        config = self.test_config.copy()
        config['cpu_cores'] = 999
        result = self.generator.validate_config(config)
        # High CPU cores should trigger a warning, not an error
        self.assertTrue(result['valid'])
        self.assertIn('CPU cores should be between', str(result['warnings']))
    
    def test_generate_docker_compose(self):
        """Test Docker Compose generation"""
        compose_yaml = self.generator.generate_docker_compose(self.test_config)
        
        # Parse generated YAML
        compose_dict = yaml.safe_load(compose_yaml)
        
        # Verify structure
        self.assertIn('version', compose_dict)
        self.assertIn('services', compose_dict)
        self.assertIn('test-windows', compose_dict['services'])
        
        # Verify service configuration
        service = compose_dict['services']['test-windows']
        self.assertEqual(service['container_name'], 'test-windows')
        self.assertIn('dockurr/windows', service['image'])
        self.assertIn('environment', service)
        
    def test_generate_env_file(self):
        """Test environment file generation"""
        env_content = self.generator.generate_env_file(self.test_config)
        
        # Verify required environment variables
        self.assertIn('USERNAME=testuser', env_content)
        self.assertIn('PASSWORD=TestPass123!', env_content)
        self.assertIn('CPU_CORES=4', env_content)
        self.assertIn('RAM_SIZE=8G', env_content)
        self.assertIn('DISK_SIZE=64G', env_content)
        self.assertIn('KVM=Y', env_content)
    
    def test_save_config_files(self):
        """Test saving configuration files to disk"""
        result = self.generator.save_config_files(self.test_config)
        
        # Verify files were created
        self.assertTrue(os.path.exists(result['docker_compose_path']))
        self.assertTrue(os.path.exists(result['env_path']))
        self.assertTrue(os.path.exists(result['config_path']))
        
        # Verify content
        with open(result['config_path'], 'r') as f:
            saved_config = json.load(f)
        self.assertEqual(saved_config['name'], 'test-windows')
    
    def test_network_configuration(self):
        """Test advanced network configuration"""
        config = self.test_config.copy()
        config['network_mode'] = 'static'
        config['static_ip'] = '192.168.1.100'
        config['gateway'] = '192.168.1.1'
        config['subnet_mask'] = '255.255.255.0'
        
        env_content = self.generator.generate_env_file(config)
        
        # Verify network configuration in env file
        self.assertIn('IP=192.168.1.100', env_content)
        self.assertIn('GATEWAY=192.168.1.1', env_content)
        self.assertIn('NETMASK=255.255.255.0', env_content)
    
    def test_snmp_configuration(self):
        """Test SNMP service configuration"""
        config = self.test_config.copy()
        config['enable_snmp'] = True
        config['snmp_community'] = 'public'
        config['snmp_trap_destinations'] = '192.168.1.50'
        
        env_content = self.generator.generate_env_file(config)
        
        # Verify SNMP environment variables
        self.assertIn('SNMP_ENABLED=Y', env_content)
        self.assertIn('SNMP_COMMUNITY=public', env_content)
        self.assertIn('SNMP_TRAPS=192.168.1.50', env_content)
    
    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist"""
        # Use a non-existent directory path
        new_dir = os.path.join(self.temp_dir, 'new_generated_configs')
        generator = DockerConfigGenerator()
        generator.output_dir = new_dir
        
        # Save config should create the directory
        generator.save_config_files(self.test_config)
        
        # Verify directory was created
        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))


if __name__ == '__main__':
    unittest.main()
