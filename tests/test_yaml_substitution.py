#!/usr/bin/env python3
"""Test if Docker Compose performs variable substitution on YAML environment values"""

import os
import tempfile
import subprocess
import yaml
import pytest
pytest.skip("Skipping docker-compose dependent test during unit test runs", allow_module_level=True)

def test_yaml_substitution():
    """Test different ways of escaping $ in YAML environment values"""
    
    password = "$test123"
    
    test_cases = [
        ("Raw string", password),
        ("Double dollar", password.replace("$", "$$")),
        ("Escaped with backslash", password.replace("$", "\\$")),
        ("Single quoted in YAML", f"'{password}'"),
        ("Double quoted in YAML", f'"{password}"'),
        ("YAML literal block", f"|-\n  {password}"),
    ]
    
    for description, test_value in test_cases:
        print(f"\n--- Testing: {description} ---")
        print(f"Value: {test_value}")
        
        # Create docker-compose.yml with environment directly embedded
        compose_content = {
            'services': {
                'test': {
                    'image': 'alpine:latest',
                    'container_name': 'test-container',
                    'environment': {
                        'PASSWORD': test_value,
                        'USERNAME': 'testuser'
                    },
                    'command': ['sh', '-c', 'echo "Password: $PASSWORD"']
                }
            }
        }
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(compose_content, f, default_flow_style=False)
            compose_file = f.name
        
        try:
            # Run docker-compose config to see how it interprets the values
            result = subprocess.run(
                ['docker-compose', '-f', compose_file, 'config'],
                capture_output=True,
                text=True
            )
            
            print("Exit code:", result.returncode)
            if result.stderr:
                print("Stderr:", result.stderr)
            
            # Check if the password is correctly preserved in the output
            if "$w33t@55T3a!" in result.stdout:
                print("✓ Password preserved correctly")
            elif "w33t@55T3a!" in result.stdout:
                print("✗ Dollar sign was stripped")
            else:
                print("? Password not found in output")
                
            # Check for variable substitution warning
            if "variable is not set" in result.stderr:
                print("✗ Variable substitution warning present")
            else:
                print("✓ No variable substitution warning")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            os.unlink(compose_file)

if __name__ == "__main__":
    print("Testing Docker Compose YAML environment variable substitution")
    print("=" * 60)
    test_yaml_substitution()
