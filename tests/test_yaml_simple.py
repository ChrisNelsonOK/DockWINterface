#!/usr/bin/env python3
"""Simple test for YAML environment variable substitution"""

import yaml
import json

def test_yaml_generation():
    """Test how YAML handles passwords with special characters"""
    
    password = "test123"
    
    # Test different escaping methods
    test_cases = {
        "raw": password,
        "double_dollar": password.replace("$", "$$"),
        "escaped_dollar": password.replace("$", "\\$"),
    }
    
    for name, value in test_cases.items():
        print(f"\n=== Testing {name} ===")
        print(f"Input value: {repr(value)}")
        
        # Create environment dict
        env_dict = {
            'PASSWORD': value,
            'USERNAME': 'testuser'
        }
        
        # Convert to YAML
        yaml_str = yaml.dump({'environment': env_dict}, default_flow_style=False)
        print(f"YAML output:\n{yaml_str}")
        
        # Parse it back to see what we get
        parsed = yaml.safe_load(yaml_str)
        parsed_password = parsed['environment']['PASSWORD']
        print(f"Parsed back: {repr(parsed_password)}")
        print(f"Match original: {parsed_password == password}")

if __name__ == "__main__":
    print("Testing YAML handling of passwords with $ characters")
    test_yaml_generation()
