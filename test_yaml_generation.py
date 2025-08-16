#!/usr/bin/env python3
"""Direct test of YAML generation with special character passwords."""

import yaml
from docker_config import DockerConfigGenerator

# Test configuration with password containing special characters
config = {
    'name': 'test-windows',
    'version': '11',
    'username': 'DockerUser', 
    'password': '$w33t@55T3a!',
    'docker_host': 'tcp://localhost:2375',
    'cpus': '4',
    'memory': '8G',
    'disk_size': '100'  # Note: should be just number, G is added in the method
}

try:
    # Generate docker-compose YAML
    generator = DockerConfigGenerator()
    docker_compose_yaml = generator.generate_docker_compose(config)
    
    print("Generated YAML:")
    print("-" * 50)
    print(docker_compose_yaml)
    print("-" * 50)
    
    # Parse the YAML to verify it's valid
    compose_dict = yaml.safe_load(docker_compose_yaml)
    
    # Extract the password from the parsed YAML
    services = compose_dict.get('services', {})
    windows = services.get('test-windows', {})
    environment = windows.get('environment', {})
    password = environment.get('PASSWORD', None)
    
    print(f"\nOriginal password: {config['password']}")
    print(f"Password in YAML:  {password}")
    print(f"Passwords match:   {password == config['password']}")
    
    if password == config['password']:
        print("\n✅ SUCCESS: Password correctly embedded in YAML!")
        exit(0)
    else:
        print("\n❌ FAILURE: Password mismatch in YAML!")
        exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
