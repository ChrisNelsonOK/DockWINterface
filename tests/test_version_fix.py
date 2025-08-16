#!/usr/bin/env python3
import requests
import json
import yaml

# Test the version normalization
test_cases = [
    ('11-enterprise', '11e'),
    ('10-pro', '10'),
    ('11-ltsc', '11l'),
    ('10-enterprise', '10e'),
]

print("Testing version normalization in API...")
for input_version, expected_version in test_cases:
    response = requests.post('http://localhost:5000/api/generate-config',
        json={
            'name': f'test-{input_version.replace("-", "")}',
            'version': input_version,
            'username': 'admin',
            'password': 'test123',
            'ram_size': 4
        })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            compose = yaml.safe_load(data['docker_compose'])
            service_name = f'test-{input_version.replace("-", "")}'
            actual_version = compose['services'][service_name]['environment'].get('VERSION')
            
            if actual_version == expected_version:
                print(f"✓ {input_version} -> {actual_version} (expected {expected_version})")
            else:
                print(f"✗ {input_version} -> {actual_version} (expected {expected_version})")
        else:
            print(f"✗ {input_version}: API returned error")
    else:
        print(f"✗ {input_version}: HTTP {response.status_code}")

print("\nDone!")
