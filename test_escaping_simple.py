#!/usr/bin/env python3
"""Simple test for password escaping"""

import sys
import os
import pytest
pytest.skip("Skipping non-pytest script during unit test runs", allow_module_level=True)

# Write output to file for debugging
output_file = open('test_escaping_output.txt', 'w')

def log(msg):
    print(msg)
    output_file.write(msg + '\n')
    output_file.flush()

try:
    log("Starting test...")
    
    # Import after logging starts
    import yaml
    from docker_config import DockerConfigGenerator
    
    log("Imports successful")
    
    # Test configuration
    config = {
        'name': 'test-windows',
        'username': 'admin',
        'password': 'P@$$w0rd$w33t',
        'version': '10',
        'language': 'en-US',
        'keyboard': 'en-US',
        'cpu_cores': 2,
        'ram_size': '4G',
        'disk_size': '50',
        'docker_host': 'tcp://10.224.125.34:2375'
    }
    
    log(f"Config created with password: {config['password']}")
    
    # Generate Docker Compose YAML
    generator = DockerConfigGenerator()
    log("Generator created")
    
    docker_compose = generator.generate_docker_compose(config)
    log("Docker compose generated")
    
    # Parse the YAML
    compose_data = yaml.safe_load(docker_compose)
    log("YAML parsed")
    
    # Check the password
    env_vars = compose_data['services']['windows']['environment']
    actual_password = env_vars['PASSWORD']
    
    log(f"Original password: {config['password']}")
    log(f"Password in YAML: {actual_password}")
    
    # Check if escaping worked
    expected_password = 'P@$$$$w0rd$$w33t'
    if actual_password == expected_password:
        log("✅ Password escaping works correctly!")
    else:
        log(f"❌ Password escaping failed: expected '{expected_password}', got '{actual_password}'")
    
    # Check Docker port
    if '2375' in config['docker_host']:
        log("✅ Docker host port is correctly set to 2375")
    else:
        log("❌ Docker host port is not 2375")
        
except Exception as e:
    log(f"Error: {e}")
    import traceback
    log(traceback.format_exc())
finally:
    output_file.close()
    print("Test completed - check test_escaping_output.txt for results")
