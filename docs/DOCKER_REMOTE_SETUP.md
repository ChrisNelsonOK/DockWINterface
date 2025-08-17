# Docker Remote Host Setup

## Configure Docker Daemon to Listen on TCP

### Option 1: Using systemd (Ubuntu/Debian)

1. SSH into your remote host (10.224.125.34)

2. Edit Docker service configuration:
```bash
sudo systemctl edit docker.service
```

3. Add these lines:
```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
```

4. Reload and restart Docker:
```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### Option 2: Using daemon.json

1. Edit Docker daemon configuration:
```bash
sudo nano /etc/docker/daemon.json
```

2. Add or modify:
```json
{
  "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
}
```

3. Restart Docker:
```bash
sudo systemctl restart docker
```

### Option 3: Docker Desktop Settings

If using Docker Desktop:
1. Open Docker Desktop Settings
2. Go to "Advanced" or "Docker Engine"
3. Add to the configuration:
```json
{
  "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
}
```
4. Apply & Restart

## Security Warning

⚠️ **IMPORTANT**: Port 2375 is unencrypted and unauthenticated!

- Only use this on trusted networks
- Consider using port 2376 with TLS for production
- Use firewall rules to restrict access:
```bash
sudo ufw allow from <your-IP> to any port 2375
```

## Test the Connection

After configuration, test from your local machine:
```bash
# Test with curl
curl http://10.224.125.34:2375/version

# Test with docker CLI
DOCKER_HOST=tcp://10.224.125.34:2375 docker info
```

## Alternative: SSH Tunnel (More Secure)

Instead of exposing Docker on TCP, use SSH tunnel:
```bash
# Create SSH tunnel
ssh -L 2375:localhost:2375 user@10.224.125.34

# Then use localhost:2375 as your Docker host
```
