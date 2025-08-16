#!/bin/bash

# DockWINterface Macvlan Network Setup Script
# Generated for container: rb-test-macvlan-10pro

# Check if network already exists
if docker network ls | grep -q 'macvlan-net'; then
  echo 'Network macvlan-net already exists'
else
  echo 'Creating macvlan network...'
  docker network create -d macvlan \
    --subnet=192.168.1.0/24 \
    --gateway=192.168.1.1 \
    --ip-range=192.168.1.192/27 \
    -o parent=eth0 \
    macvlan-net
fi

echo 'Macvlan network setup complete!'
