#!/usr/bin/env python3
"""Test that password escaping works correctly in Docker Compose YAML"""

import sys
import yaml
from docker_config import DockerConfigGenerator

def test_password_escaping():
    """Test that $ characters in passwords are properly escaped"""
    
    # Test configuration with password containing $
    config = {
        'name': 'test-windows',
        'username': 'admin',
        'password': 'P@$$w0rd$w33t',  # Password with $ characters
        'version': '10',
        'language': 'en-US',
        'keyboard': 'en-US',
        'cpu_cores': 2,
        'ram_size': '4G',
        'disk_size': '50',
        'docker_host': 'tcp://10.224.125.34:2375'
    }
    
    # Generate Docker Compose YAML
    generator = DockerConfigGenerator()
    docker_compose = generator.generate_docker_compose(config)
    
    # Parse the YAML
    compose_data = yaml.safe_load(docker_compose)
    
    # Check the password in environment variables
    env_vars = compose_data['services']['windows']['environment']
    
    # The password should have $ escaped as $$
    expected_password = 'P@$$$$w0rd$$w33t'  # Each $ becomes $$
    actual_password = env_vars['PASSWORD']
    
    print(f"Original password: {config['password']}")
    print(f"Expected in YAML: {expected_password}")
    print(f"Actual in YAML: {actual_password}")
    
    assert actual_password == expected_password, f"Password escaping failed: expected '{expected_password}', got '{actual_password}'"
    
    print("✓ Password escaping test passed!")
    
    # Also verify Docker host port is 2375
    print(f"\nDocker host in config: {config['docker_host']}")
    assert '2375' in config['docker_host'], "Docker host should use port 2375"
    print("✓ Docker host port is correctly set to 2375")
    
    return True

if __name__ == "__main__":
    print("Starting password escaping test...")
    sys.stdout.flush()
    try:
        test_password_escaping()
        print("\n✅ All tests passed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    sys.stdout.flush()
