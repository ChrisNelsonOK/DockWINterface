#!/usr/bin/env python3
"""Debug script for rollback feature"""
import requests
import json

# Test with minimal config
config = {
    "name": "test",
    "image": "dockurr/windows",
    "version": "win11",
    "vnc_port": "5900",
    "web_port": "8080",
    "network_mode": "bridge",
    "cpu_limit": "2",
    "memory_limit": "4G",
    "username": "admin",
    "password": "pass123",
    "volumes": [],
    "environment": {},
    "enable_rollback": True,
    "rollback_timeout": 5
}

print("Sending config with enable_rollback=True...")
print(f"Config keys: {config.keys()}")

response = requests.post(
    "http://localhost:5000/api/generate-config",
    json=config,
    headers={"Content-Type": "application/json"}
)

print(f"\nResponse status: {response.status_code}")
result = response.json()
print(f"Response keys: {result.keys()}")
print(f"Success: {result.get('success')}")
print(f"Has rollback info: {'rollback' in result}")

if 'rollback' in result:
    print(f"Rollback info: {json.dumps(result['rollback'], indent=2)}")
else:
    print("\nFull response:")
    print(json.dumps(result, indent=2))
