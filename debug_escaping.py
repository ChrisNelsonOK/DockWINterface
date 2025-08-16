#!/usr/bin/env python3

def escape_env_value(value, for_env_file=False):
    """Test the escaping logic directly"""
    if not isinstance(value, str):
        return str(value)
    
    if for_env_file:
        # For .env files, escape $ to prevent variable substitution
        has_dollar = '$' in value
        escaped = value.replace('$', '$$')
        # Always quote values containing $ or special characters in .env files
        if has_dollar or any(char in escaped for char in [' ', '"', "'", '\\', '&', '|', ';', '(', ')', '<', '>', '`']):
            escaped = escaped.replace('"', '\\"')
            escaped = f'"{escaped}"'
        return escaped
    else:
        # For Docker Compose YAML, only quote if value contains spaces
        if ' ' in value:
            escaped = value.replace('"', '\\"')
            escaped = f'"{escaped}"'
            return escaped
        
    return value

# Test the problematic password
test_password = "$w33t@55T3a!"
print(f"Original password: {test_password}")

escaped_env = escape_env_value(test_password, for_env_file=True)
print(f"Escaped for .env: {escaped_env}")

escaped_yaml = escape_env_value(test_password, for_env_file=False)  
print(f"Escaped for YAML: {escaped_yaml}")

# Test what the env line would look like
env_line = f"PASSWORD={escaped_env}"
print(f"Full .env line: {env_line}")

# Test if this would prevent variable substitution
print("\nTesting variable substitution prevention:")
print("If docker-compose sees PASSWORD=\"$$w33t@55T3a!\"")
print("It should interpret $$ as literal $ and result in: $w33t@55T3a!")
