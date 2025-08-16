# Windows Version Flag Fix Documentation

## Issue Summary
Windows containers were failing to start because the frontend version strings (e.g., `11-enterprise`) were not being correctly normalized to Dockur's backend flags (e.g., `11e`).

## Root Cause
The bug was in `docker_config.py` at line 281, where the `VERSION` environment variable was incorrectly placed under the `ram_size` condition:

```python
# INCORRECT CODE (Before Fix)
if config.get('ram_size'):
    env_dict['VERSION'] = str(config['version'])  # Wrong! This sets VERSION only when ram_size exists
```

This caused the VERSION to be set with the wrong value and only when `ram_size` was present.

## The Fix
**File:** `docker_config.py`
**Location:** Lines 280-285

```python
# CORRECT CODE (After Fix)
if config.get('ram_size'):
    env_dict['RAM_SIZE'] = f"{config['ram_size']}G"

# Windows version
if config.get('version'):
    env_dict['VERSION'] = str(config['version'])
```

## Version Mapping
The version normalization happens in `routes.py` using the `version_map` dictionary:

| Frontend (UI) | Backend (Dockur) | Windows Version |
|--------------|------------------|-----------------|
| `11-enterprise` | `11e` | Windows 11 Enterprise |
| `11-pro` | `11` | Windows 11 Pro |
| `11-ltsc` | `11l` | Windows 11 LTSC |
| `10-enterprise` | `10e` | Windows 10 Enterprise |
| `10-pro` | `10` | Windows 10 Pro |
| `10-ltsc` | `10l` | Windows 10 LTSC |
| `8-enterprise` | `8e` | Windows 8 Enterprise |
| `7-ultimate` | `7u` | Windows 7 Ultimate |
| `vista-ultimate` | `vu` | Windows Vista Ultimate |
| `xp` | `xp` | Windows XP |

## Deployment Notes
After fixing the code, the Docker container must be rebuilt to pick up the changes:

```bash
# Stop and remove old container
docker stop dockwinterface && docker rm dockwinterface

# Rebuild with no cache to ensure fresh code
docker build --no-cache -t dockwinterface .

# Run the new container
docker run -d --name dockwinterface -p 5000:5000 --restart unless-stopped dockwinterface
```

## Testing
To verify the fix works:

```bash
curl -s -X POST http://localhost:5000/api/generate-config \
  -H "Content-Type: application/json" \
  -d '{"name": "test", "version": "11-enterprise", "username": "admin", "password": "test123", "ram_size": 4}' \
  | jq -r '.docker_compose' | grep VERSION
```

Should output: `VERSION: 11e`

## Device Requirements Fix

### Boot Issue Resolution
After fixing the version normalization, Windows containers were still unable to boot with the error:
```
BdsDxe: No bootable option or device was found.
```

**Root Cause:** Missing `/dev/net/tun` device in container deployments.

**Fix Applied:** Added `/dev/net/tun` to the devices list in `docker_config.py` line 26:

```python
# BEFORE:
'devices': ['/dev/kvm'],

# AFTER:
'devices': ['/dev/kvm', '/dev/net/tun'],
```

### Reference Implementation
The fix aligns with the official Dockurr/windows documentation which specifies both devices:

```bash
docker run -it --rm --name windows -p 8006:8006 \
  --device=/dev/kvm --device=/dev/net/tun \
  --cap-add NET_ADMIN \
  -v "${PWD:-.}/windows:/storage" \
  --stop-timeout 120 dockurr/windows
```

## Related Files
- `/opt/DockWINterface/routes.py` - Contains version mapping and normalization logic
- `/opt/DockWINterface/docker_config.py` - Generates Docker environment variables and device mappings
- `/opt/DockWINterface/ssh_docker.py` - Handles device pass-through for remote deployments
- `/opt/DockWINterface/tests/test_version_normalization.py` - Unit tests for version normalization
