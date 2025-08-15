#!/usr/bin/env python3
"""Simple test to debug rollback issue"""
import requests
import json

# Send request with curl equivalent
url = "http://localhost:5000/api/generate-config"
headers = {"Content-Type": "application/json"}
data = {
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
    "enable_rollback": True,
    "rollback_timeout": 5
}

print("Request data:")
print(json.dumps(data, indent=2))
print(f"\nenable_rollback in request: {data.get('enable_rollback')}")
print(f"Type of enable_rollback: {type(data.get('enable_rollback'))}")

try:
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    
    print(f"\nResponse status: {response.status_code}")
    print(f"Response has 'rollback' key: {'rollback' in result}")
    
    if 'rollback' in result:
        print("\nRollback info found:")
        print(json.dumps(result['rollback'], indent=2))
    else:
        print("\nNo rollback info in response")
        print("Response keys:", list(result.keys()))
        
except Exception as e:
    print(f"Error: {e}")
