#!/usr/bin/env python3
"""Check the structure of generated YAML"""

import yaml
from docker_config import DockerConfigGenerator
import pytest
pytest.skip("Skipping non-pytest script during unit test runs", allow_module_level=True)

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

# Generate Docker Compose YAML
generator = DockerConfigGenerator()
docker_compose = generator.generate_docker_compose(config)

# Write raw YAML to file
with open('generated_yaml.txt', 'w') as f:
    f.write("=== RAW YAML ===\n")
    f.write(docker_compose)
    f.write("\n\n=== PARSED STRUCTURE ===\n")
    
    # Parse and show structure
    compose_data = yaml.safe_load(docker_compose)
    
    # Show service names
    f.write(f"Services: {list(compose_data.get('services', {}).keys())}\n")
    
    # Get the actual service name
    for service_name, service_data in compose_data.get('services', {}).items():
        f.write(f"\nService '{service_name}':\n")
        
        # Check environment variables
        if 'environment' in service_data:
            env_vars = service_data['environment']
            f.write(f"  Environment variables:\n")
            for key, value in env_vars.items():
                if key == 'PASSWORD':
                    f.write(f"    {key}: {value}\n")
                    f.write(f"    Original password: {config['password']}\n")
                    f.write(f"    Expected escaped: P@$$$$w0rd$$w33t\n")
                    if value == 'P@$$$$w0rd$$w33t':
                        f.write(f"    ✅ Password correctly escaped!\n")
                    else:
                        f.write(f"    ❌ Password NOT correctly escaped\n")

print("Check generated_yaml.txt for results")
