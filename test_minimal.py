#!/usr/bin/env python3
import sys
print("Test starting", file=sys.stderr, flush=True)

try:
    from docker_config import DockerConfigGenerator
    print("Import successful", file=sys.stderr, flush=True)
    
    config = {
        'name': 'test',
        'version': '11',
        'username': 'user',
        'password': '$test',
        'docker_host': 'tcp://localhost:2375',
        'cpus': '4',
        'memory': '8G',
        'disk_size': '100G'
    }
    
    gen = DockerConfigGenerator()
    yaml_content = gen.generate_docker_compose(config)
    print("YAML generated successfully", file=sys.stderr, flush=True)
    print(f"Length: {len(yaml_content)}", file=sys.stderr, flush=True)
    
except Exception as e:
    print(f"Error occurred: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("Test completed", file=sys.stderr, flush=True)
