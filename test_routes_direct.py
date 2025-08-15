#!/usr/bin/env python3
"""Test routes module directly"""
import sys
import json

sys.path.insert(0, '.')



class MockRequest:
    def __init__(self, data):
        self.data = data

    def get_json(self):
        return self.data



# Import and test
print("Importing routes module...")
import routes

# Monkey-patch request
original_request = routes.request
routes.request = MockRequest({
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
})

print("\nCalling generate_config directly...")
try:
    # Call the function directly
    response = routes.generate_config()
    
    # Extract JSON data from response
    if hasattr(response, 'get_json'):
        result = response.get_json()
    else:
        result = (response[0].get_json() if isinstance(response, tuple) 
                 else response.json)
    
    print(f"\nResponse type: {type(response)}")
    print(f"Response has rollback: {'rollback' in result}")
    print(f"Response keys: {list(result.keys())}")

    if 'rollback' in result:
        print("\nRollback info:")
        print(json.dumps(result['rollback'], indent=2))
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    routes.request = original_request
