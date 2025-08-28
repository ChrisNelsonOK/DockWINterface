# DockWINterface Deployment Update - August 28, 2024

## 🚀 Multi-Version Windows Support Enhancement

This update adds comprehensive support for Windows Server 2022 deployments alongside existing Windows 10/11 support, resolving the "unknown server OS" error.

## ✅ Changes Made

### 1. Version-Specific Volume Mapping
- **Windows 10/11 (All editions)**: Continue using `/opt/windows/xfer`
- **Windows Server 2022**: Now automatically uses `/opt/windows/xfer2`
- **Windows Server 2019**: Now automatically uses `/opt/windows/xfer4`
- **Windows Server 2025**: Now automatically uses `/opt/windows/xfer3`

### 2. Enhanced Docker Configuration Generator
- Added `_get_version_specific_volume_path()` method for intelligent version detection
- Enhanced `_generate_volumes()` method with automatic path selection
- Added `_ensure_volume_directory()` method for automatic directory creation
- Implemented fallback logic for unsupported versions

### 3. Updated Docker Compose Configuration
- Added `/opt/windows:/opt/windows` volume mount to the container
- Fixed network name from `dokwinterface` to `dockwinterface`
- Added default value for `SESSION_SECRET` environment variable

### 4. Permission and Ownership Fixes
- Corrected ownership of `/opt/windows/xfer*` directories to match container user (uid=1000)
- Ensured proper write permissions for volume directory creation

## 🔧 Deployment Changes Required

### For New Deployments
Use the updated docker-compose file:
```bash
cd /opt/DockWINterface
docker-compose -f docker-compose.production.yml up -d
```

### For Existing Deployments
1. **Stop and remove existing container**:
```bash
docker stop DockWINterface
docker rm DockWINterface
```

2. **Rebuild the image**:
```bash
docker build -t dockwinterface:latest .
```

3. **Fix volume directory permissions**:
```bash
chown -R 1000:1000 /opt/windows/xfer*
```

4. **Deploy updated container**:
```bash
docker run -d \
  --name DockWINterface \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/DockWINterface/generated_configs:/app/generated_configs \
  -v /opt/windows:/opt/windows \
  --health-cmd "curl -f http://localhost:5000/" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  --health-start-period 40s \
  dockwinterface:latest
```

Or use docker-compose:
```bash
docker-compose -f docker-compose.production.yml up -d
```

## ✨ New Features

### Automatic Volume Path Selection
- **No manual configuration required** - volume paths are assigned automatically based on Windows version
- **Concurrent deployments supported** - multiple Windows versions can run simultaneously
- **ISO/file isolation** - each version uses its dedicated volume mount
- **Backward compatible** - existing Windows 11 deployments continue to work unchanged

### Manual Volume Override
Users can still specify custom volume paths in the "Data Volume" field during deployment if needed.

## 🐛 Issues Resolved

1. **"Unknown server OS" Error**: Fixed by implementing proper version detection and volume mapping
2. **Windows Server 2022 Deployment Failures**: Resolved through version-specific volume path selection
3. **Container Permission Issues**: Fixed by proper volume mounting and ownership configuration
4. **Docker Compose Network Issues**: Corrected network naming and configuration

## 📋 Verification Steps

After deployment, verify the changes work correctly:

1. **Test Windows Server 2022 Configuration**:
```bash
curl -X POST http://localhost:5000/api/generate-config \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-win2022",
    "version": "2022-standard",
    "username": "admin",
    "password": "TestPassword123!",
    "ram_size": 4,
    "cpu_cores": 2,
    "disk_size": 40
  }' | jq -r .docker_compose | grep xfer
```
Expected output: `- /opt/windows/xfer2:/storage`

2. **Test Windows 11 Backward Compatibility**:
```bash
curl -X POST http://localhost:5000/api/generate-config \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-win11",
    "version": "11-pro",
    "username": "admin",
    "password": "TestPassword123!",
    "ram_size": 4,
    "cpu_cores": 2,
    "disk_size": 40
  }' | jq -r .docker_compose | grep xfer
```
Expected output: `- /opt/windows/xfer:/storage`

3. **Check Application Logs**:
```bash
docker logs DockWINterface
```
Should show no errors related to volume directory creation or permissions.

## 📁 File Changes Summary

### Modified Files
- `docker_config.py`: Added version-specific volume mapping logic
- `docker-compose.production.yml`: Added Windows volume mount and fixed configuration
- `README.md`: Updated with multi-version support documentation

### New Files
- `DEPLOYMENT_UPDATE_2024-08-28.md`: This deployment guide

### Backup Files Created
- `docker_config.py.backup`: Backup of original configuration
- `docker-compose.production.yml.backup`: Backup of original compose file

## 🔄 Rollback Instructions

If issues arise, rollback using the backup files:

1. **Restore original configuration**:
```bash
cp docker_config.py.backup docker_config.py
cp docker-compose.production.yml.backup docker-compose.production.yml
```

2. **Rebuild and redeploy**:
```bash
docker build -t dockwinterface:latest .
docker-compose -f docker-compose.production.yml up -d --force-recreate
```

## 🎯 Next Steps

1. Test Windows Server 2022 deployment through the web interface
2. Verify that existing Windows 11 deployments continue to work
3. Monitor logs for any issues with the new volume mapping system
4. Update any deployment scripts or documentation to reflect the new container requirements

---

**Note**: This update requires a container rebuild and restart but does not affect existing deployed Windows containers.
