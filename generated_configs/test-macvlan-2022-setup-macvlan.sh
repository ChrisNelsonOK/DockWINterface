#!/bin/bash

# DockWINterface Macvlan Network Setup Script
# Generated for container: test-macvlan-2022

# Check if network already exists
if docker network ls | grep -q 'macvlan'; then
  echo 'Network macvlan already exists'
else
  echo 'Creating macvlan network...'
  docker network create -d macvlan \
    --subnet=10.224.125.0/24 \
    --gateway=10.224.125.1 \
    --ip-range=10.224.125.192/29 \
    --aux-address='host=10.224.125.193' \
    -o parent=bond0 \
    macvlan
fi

# Configure host access to macvlan network
echo 'Setting up host access via macvlan-shim...'
sudo ip link add macvlan-shim link bond0 type macvlan mode bridge
sudo ip addr add 10.224.125.193/32 dev macvlan-shim
sudo ip link set macvlan-shim up
sudo ip route add 10.224.125.192/29 dev macvlan-shim
echo 'Host can now communicate with containers via 10.224.125.193'

echo 'Macvlan network setup complete!'
