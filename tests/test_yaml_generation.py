#!/usr/bin/env python3
"""Pytest for YAML generation with special character passwords."""

import yaml
from docker_config import DockerConfigGenerator


def test_password_embedded_in_yaml():
    """Ensure PASSWORD env appears unaltered in compose YAML."""
    config = {
        'name': 'test-windows',
        'version': '11',
        'username': 'DockerUser',
        'password': '$w33t@55T3a!',
        'docker_host': 'tcp://localhost:2375',
        'cpus': '4',
        'memory': '8G',
        'disk_size': '100',  # number; units added by generator if needed
    }

    generator = DockerConfigGenerator()
    docker_compose_yaml = generator.generate_docker_compose(config)

    compose_dict = yaml.safe_load(docker_compose_yaml)
    env = compose_dict['services'][config['name']]['environment']

    expected_pwd = config['password'].replace('$', '$$')
    assert env['PASSWORD'] == expected_pwd
