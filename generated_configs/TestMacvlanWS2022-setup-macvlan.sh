#!/bin/bash

# DockWINterface Macvlan Network Setup Script
# Generated for container: TestMacvlanWS2022

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

echo 'Macvlan network setup complete!'
