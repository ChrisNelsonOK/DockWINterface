#!/usr/bin/env python3
"""Test script to verify password escaping fix works correctly."""

import sys
import traceback

try:
    import yaml
    import json
    from docker_config import DockerConfigGenerator
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

def test_password_escaping():
    """Test that passwords with special characters are handled correctly."""
    
    # Test configuration with complex password
    config = {
        'name': 'test-windows',
        'version': '11',
        'username': 'DockerUser',
        'password': '$w33t@55T3a!',  # Password with $ that was causing issues
        'docker_host': 'tcp://localhost:2375',
        'cpus': '4',
        'memory': '8G',
        'disk_size': '100G'
    }
    
    # Initialize generator
    generator = DockerConfigGenerator()
    
    # Generate docker-compose YAML
    docker_compose_yaml = generator.generate_docker_compose(config)
    
    # Parse the YAML to verify structure
    compose_dict = yaml.safe_load(docker_compose_yaml)
    
    print("Generated Docker Compose YAML:")
    print("-" * 50)
    print(docker_compose_yaml)
    print("-" * 50)
    
    # Check that environment variables are embedded correctly
    service = compose_dict['services']['windows']
    env_vars = service.get('environment', {})
    
    print("\nEnvironment Variables in YAML:")
    print(json.dumps(env_vars, indent=2))
    
    # Verify password is correctly set
    if env_vars.get('PASSWORD') == '$w33t@55T3a!':
        print("\n✅ SUCCESS: Password with special characters is correctly embedded!")
        print(f"   PASSWORD value: {env_vars.get('PASSWORD')}")
    else:
        print("\n❌ FAILURE: Password not correctly set")
        print(f"   Expected: $w33t@55T3a!")
        print(f"   Got: {env_vars.get('PASSWORD')}")
    
    # Test with other problematic passwords
    test_passwords = [
        "test$123",
        "p@$$w0rd",
        "complex!@#$%^&*()",
        "${VAR}test",
        "normal_password"
    ]
    
    print("\n" + "=" * 50)
    print("Testing various passwords:")
    print("=" * 50)
    
    for pwd in test_passwords:
        test_config = config.copy()
        test_config['password'] = pwd
        
        compose_yaml = generator.generate_docker_compose(test_config)
        compose_data = yaml.safe_load(compose_yaml)
        
        embedded_pwd = compose_data['services']['windows']['environment'].get('PASSWORD')
        
        if embedded_pwd == pwd:
            print(f"✅ '{pwd}' -> Correctly embedded")
        else:
            print(f"❌ '{pwd}' -> Failed (got: '{embedded_pwd}')")

if __name__ == "__main__":
    try:
        test_password_escaping()
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)
