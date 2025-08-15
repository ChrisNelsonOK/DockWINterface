#!/usr/bin/env python3
"""Direct test of the API endpoint"""
import subprocess
import time
import requests

# Kill any existing server
subprocess.run(["pkill", "-9", "-f", "python"], capture_output=True)
time.sleep(1)

# Start server in background
server = subprocess.Popen(
    ["python", "app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

# Wait for server to start
time.sleep(3)

# Make request

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

try:
    response = requests.post(
        "http://localhost:5000/api/generate-config", json=data
    )
    result = response.json()
    
    print("Response has rollback:", "rollback" in result)
    print("Response keys:", list(result.keys()))
    
    # Check server output for debug messages
    server.terminate()
    time.sleep(1)
    output = server.stdout.read() if server.stdout else ''
    
    print("\nServer output:")
    for line in output.split('\n'):
        if 'DEBUG' in line or 'enable_rollback' in line:
            print(line)
            
except Exception as e:
    print(f"Error: {e}")
finally:
    server.terminate()
