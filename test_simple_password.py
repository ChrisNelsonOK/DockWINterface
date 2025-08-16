#!/usr/bin/env python3
"""Simple test to verify password escaping works."""

import sys
import traceback

try:
    from docker_config import DockerConfigGenerator
    import yaml
    print("Imports successful")
    
    # Test configuration with problematic password
    config = {
        'name': 'test-windows',
        'version': '11', 
        'username': 'DockerUser',
        'password': '$w33t@55T3a!',
        'docker_host': 'tcp://localhost:2375',
        'cpus': '4',
        'memory': '8G',
        'disk_size': '100G'
    }
    print(f"Config created: {config}")
    
    # Generate docker-compose YAML
    generator = DockerConfigGenerator()
    print("Generator created")
    
    docker_compose_yaml = generator.generate_docker_compose(config)
    print(f"YAML generated, length: {len(docker_compose_yaml)}")
    print(f"First 200 chars of YAML:\n{docker_compose_yaml[:200]}")
    
    # Parse and check
    compose_dict = yaml.safe_load(docker_compose_yaml)
    print(f"YAML parsed successfully")
    
    # Navigate to the password field
    services = compose_dict.get('services', {})
    windows = services.get('windows', {})
    environment = windows.get('environment', {})
    password = environment.get('PASSWORD', None)
    
    print(f"Original password: {config['password']}")
    print(f"Embedded password: {password}")
    print(f"Match: {password == config['password']}")
    
    if password == config['password']:
        print("\n✅ SUCCESS: Password correctly embedded without substitution!")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Password mismatch!")
        sys.exit(1)
        
except Exception as e:
    print(f"ERROR: {e}")
    print(f"Traceback:\n{traceback.format_exc()}")
    sys.exit(1)
