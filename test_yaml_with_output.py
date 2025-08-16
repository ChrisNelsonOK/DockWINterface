#!/usr/bin/env python3
"""Test YAML generation with output to file."""

import yaml
from docker_config import DockerConfigGenerator
import pytest
pytest.skip("Skipping non-pytest script during unit test runs", allow_module_level=True)

# Open output file
with open('test_output.txt', 'w') as f:
    f.write("Starting test...\n")
    
    # Test configuration with password containing special characters
    config = {
        'name': 'test-windows',
        'version': '11',
        'username': 'DockerUser', 
        'password': '$w33t@55T3a!',
        'docker_host': 'tcp://localhost:2375',
        'cpus': '4',
        'memory': '8G',
        'disk_size': '100'
    }
    f.write(f"Config: {config}\n")
    
    try:
        # Generate docker-compose YAML
        generator = DockerConfigGenerator()
        f.write("Generator created\n")
        
        docker_compose_yaml = generator.generate_docker_compose(config)
        f.write(f"YAML generated, length: {len(docker_compose_yaml)}\n")
        f.write(f"YAML content:\n{docker_compose_yaml}\n")
        
        # Parse the YAML to verify it's valid
        compose_dict = yaml.safe_load(docker_compose_yaml)
        f.write(f"YAML parsed successfully\n")
        
        # Extract the password from the parsed YAML
        services = compose_dict.get('services', {})
        windows = services.get('test-windows', {})
        environment = windows.get('environment', {})
        password = environment.get('PASSWORD', None)
        
        f.write(f"Original password: {config['password']}\n")
        f.write(f"Password in YAML:  {password}\n")
        f.write(f"Passwords match:   {password == config['password']}\n")
        
        if password == config['password']:
            f.write("SUCCESS: Password correctly embedded in YAML!\n")
            print("SUCCESS: Test passed! Check test_output.txt for details.")
            exit(0)
        else:
            f.write("FAILURE: Password mismatch in YAML!\n")
            print("FAILURE: Test failed! Check test_output.txt for details.")
            exit(1)
            
    except Exception as e:
        f.write(f"ERROR: {e}\n")
        import traceback
        f.write(traceback.format_exc())
        print(f"ERROR: {e} - Check test_output.txt for details.")
        exit(1)
