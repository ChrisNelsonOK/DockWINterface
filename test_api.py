#!/usr/bin/env python3

import requests
import json

# Test data similar to what the wizard would send
test_config = {
    "name": "test-windows",
    "version": "11",
    "username": "testuser", 
    "password": "testpass123",
    "language": "en-US",
    "keyboard": "us",
    "cpu_cores": "4",
    "ram_size": "4",
    "disk_size": "40",
    "rdp_port": "3389",
    "vnc_port": "8006",
    "network_mode": "macvlan",
    "macvlan_subnet": "192.168.1.0/24",
    "macvlan_gateway": "192.168.1.1", 
    "macvlan_parent": "bond0",
    "enable_rollback": False
}

try:
    print("Testing /api/generate-config endpoint...")
    response = requests.post(
        "http://localhost:5000/api/generate-config",
        json=test_config,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("SUCCESS!")
        result = response.json()
        print(f"Response keys: {result.keys()}")
    else:
        print(f"ERROR: {response.status_code}")
        print(f"Response text: {response.text}")
        
except Exception as e:
    print(f"Request failed: {str(e)}")
