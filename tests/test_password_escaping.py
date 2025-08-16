#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docker_config import DockerConfigGenerator

def test_password_escaping():
    """Test password escaping functionality"""
    generator = DockerConfigGenerator()
    
    # Test password with $ character
    test_password = "$w33t@55T3a!"
    
    print("Testing password escaping:")
    print(f"Original password: {test_password}")
    
    # Test for .env file escaping
    escaped_env = generator._escape_env_value(test_password, for_env_file=True)
    print(f"Escaped for .env file: {escaped_env}")
    
    # Test for YAML escaping  
    escaped_yaml = generator._escape_env_value(test_password, for_env_file=False)
    print(f"Escaped for YAML: {escaped_yaml}")
    
    # Test full config generation
    test_config = {
        'name': 'test-container',
        'username': 'Administrator',
        'password': test_password,
        'version': 'win11',
        'language': 'en',
        'keyboard': 'en-us',
        'rdp_port': '3389',
        'vnc_port': '8006'
    }
    
    print("\n" + "="*50)
    print("FULL .ENV FILE CONTENT:")
    print("="*50)
    env_content = generator.generate_env_file(test_config)
    print(env_content)
    
    print("\n" + "="*50)
    print("FULL DOCKER-COMPOSE CONTENT:")
    print("="*50)
    compose_content = generator.generate_docker_compose(test_config)
    print(compose_content)

if __name__ == "__main__":
    test_password_escaping()
