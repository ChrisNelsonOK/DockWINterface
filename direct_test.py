#!/usr/bin/env python3

import os
import tempfile
import subprocess

def test_escaping_directly():
    """Test different escaping approaches directly with docker-compose"""
    
    # Test password
    password = "$w33t@55T3a!"
    
    # Create different .env file versions
    env_tests = {
        "double_quotes": f'PASSWORD="{password}"',
        "double_escape": f'PASSWORD="$$w33t@55T3a!"',
        "single_quotes": f"PASSWORD='{password}'",
        "no_quotes": f"PASSWORD={password}"
    }
    
    # Simple docker-compose content
    compose_content = """version: '3.8'
services:
  test:
    image: alpine:latest
    command: sh -c 'echo "Password is: $PASSWORD"'
    env_file:
      - .env
"""
    
    for test_name, env_line in env_tests.items():
        print(f"\n=== Testing {test_name} ===")
        print(f"Env line: {env_line}")
        
        # Create temp files
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, '.env')
            compose_file = os.path.join(tmpdir, 'docker-compose.yml')
            
            # Write files
            with open(env_file, 'w') as f:
                f.write(env_line + '\n')
            
            with open(compose_file, 'w') as f:
                f.write(compose_content)
            
            # Test with docker-compose config
            try:
                result = subprocess.run([
                    'docker-compose', '-f', compose_file, 
                    '--env-file', env_file, 'config'
                ], capture_output=True, text=True, cwd=tmpdir, timeout=10)
                
                if result.returncode == 0:
                    print("✓ Config validation passed")
                    # Look for the password in the output
                    if "$w33t@55T3a!" in result.stdout:
                        print("✓ Password preserved correctly")
                    elif "w33t" in result.stderr:
                        print("✗ Variable substitution warning detected")
                    else:
                        print("? Password transformation unclear")
                else:
                    print(f"✗ Config failed: {result.stderr}")
                    if "w33t" in result.stderr:
                        print("✗ Variable substitution error confirmed")
                        
            except Exception as e:
                print(f"✗ Test failed: {e}")

if __name__ == "__main__":
    test_escaping_directly()
