#!/usr/bin/env python3
"""
Test script for rollback integration functionality
"""

import requests
import json
import time
import sys
import pytest
pytest.skip("Skipping integration tests that require a running server", allow_module_level=True)

BASE_URL = "http://localhost:5000"

def test_rollback_flow():
    """Test the complete rollback flow"""
    
    print("Testing DockWINterface Rollback Integration...")
    print("-" * 50)
    
    # Test configuration with rollback enabled
    config_data = {
        "name": "test-rollback-container",
        "image": "dockurr/windows:latest",
        "version": "win11",
        "vnc_port": "5900",
        "web_port": "8080",
        "network_mode": "bridge",
        "cpu_limit": "2",
        "memory_limit": "4G",
        "username": "admin",
        "password": "password123",
        "volumes": [],
        "environment": {},
        "enable_rollback": True,
        "rollback_timeout": 5  # 5 minutes
    }
    
    print("\n1. Generating configuration with rollback protection...")
    response = requests.post(
        f"{BASE_URL}/api/generate-config",
        json=config_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Failed to generate config: {response.text}")
        return False
    
    result = response.json()
    
    if not result.get("success"):
        print(f"   ❌ Config generation failed: {result.get('error')}")
        return False
    
    print(f"   ✅ Configuration generated successfully")
    
    # Debug: print the actual response
    print(f"   DEBUG: Response keys: {result.keys()}")
    print(f"   DEBUG: enable_rollback sent: {config_data.get('enable_rollback')}")
    
    # Check if rollback was enabled
    rollback_info = result.get("rollback")
    if rollback_info:
        checkpoint_id = rollback_info.get("checkpoint_id")
        timeout = rollback_info.get("timeout")
        print(f"   ✅ Rollback protection enabled")
        print(f"      - Checkpoint ID: {checkpoint_id}")
        print(f"      - Timeout: {timeout} seconds")
        
        # Test getting rollback status
        print("\n2. Checking rollback status...")
        status_response = requests.get(
            f"{BASE_URL}/api/rollback/status/{checkpoint_id}"
        )
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            checkpoint = status_data.get("checkpoint", {})
            print(f"   ✅ Status retrieved: {checkpoint.get('status', 'unknown')}")
        else:
            print(f"   ⚠️  Could not retrieve status")
        
        # Test rollback history
        print("\n3. Checking rollback history...")
        history_response = requests.get(
            f"{BASE_URL}/api/rollback/history?days=1"
        )
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            history = history_data.get("history", [])
            print(f"   ✅ Found {len(history)} checkpoint(s) in history")
            
            if history:
                latest = history[0]
                print(f"      - Latest: {latest.get('id')}")
                print(f"      - Type: {latest.get('id', '').split('_')[0]}")
                print(f"      - Created: {latest.get('created')}")
        else:
            print(f"   ⚠️  Could not retrieve history")
        
        # Wait a moment then confirm the checkpoint
        print("\n4. Simulating confirmation after 3 seconds...")
        time.sleep(3)
        
        confirm_response = requests.post(
            f"{BASE_URL}/api/rollback/confirm",
            json={"checkpoint_id": checkpoint_id},
            headers={"Content-Type": "application/json"}
        )
        
        if confirm_response.status_code == 200:
            confirm_data = confirm_response.json()
            if confirm_data.get("success"):
                print(f"   ✅ Checkpoint confirmed successfully")
            else:
                print(f"   ❌ Confirmation failed: {confirm_data.get('error')}")
        else:
            print(f"   ❌ Confirmation request failed: {confirm_response.text}")
        
        # Check final status
        print("\n5. Checking final status...")
        final_status_response = requests.get(
            f"{BASE_URL}/api/rollback/status/{checkpoint_id}"
        )
        
        if final_status_response.status_code == 200:
            final_data = final_status_response.json()
            checkpoint = final_data.get("checkpoint", {})
            if checkpoint.get("confirmed"):
                print(f"   ✅ Checkpoint is confirmed")
            else:
                print(f"   ⚠️  Checkpoint status: {checkpoint.get('status', 'unknown')}")
    else:
        print("   ⚠️  Rollback was not enabled in response")
    
    print("\n" + "-" * 50)
    print("✅ Rollback integration test completed!")
    return True


def test_rollback_trigger():
    """Test manual rollback trigger"""
    
    print("\nTesting Manual Rollback Trigger...")
    print("-" * 50)
    
    # First create a checkpoint
    config_data = {
        "name": "test-trigger-container",
        "version": "latest",
        "username": "testuser2",
        "password": "testpass456",
        "windows_version": "win10",
        "ram_size": 4,
        "cpu_cores": 2,
        "disk_size": 32,
        "network_mode": "bridge",
        "enable_gpu": False,
        "enable_audio": False,
        "enable_usb": False,
        "mount_paths": [],
        "additional_env": {},
        "enable_rollback": True,
        "rollback_timeout": 10,
        "rollback_monitoring": "both"
    }
    
    print("\n1. Creating test checkpoint...")
    response = requests.post(
        f"{BASE_URL}/api/generate-config",
        json=config_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"   ❌ Failed to generate config: {response.text}")
        return False
    
    result = response.json()
    rollback_info = result.get("rollback")
    
    if not rollback_info:
        print("   ❌ No rollback info in response")
        return False
    
    checkpoint_id = rollback_info.get("checkpoint_id")
    print(f"   ✅ Checkpoint created: {checkpoint_id}")
    
    # Wait a moment then trigger rollback
    print("\n2. Triggering manual rollback after 2 seconds...")
    time.sleep(2)
    
    rollback_response = requests.post(
        f"{BASE_URL}/api/rollback/trigger",
        json={
            "checkpoint_id": checkpoint_id,
            "reason": "Test rollback trigger"
        },
        headers={"Content-Type": "application/json"}
    )
    
    if rollback_response.status_code == 200:
        rollback_data = rollback_response.json()
        if rollback_data.get("success"):
            print(f"   ✅ Rollback triggered successfully")
            print(f"      - Files restored: {rollback_data.get('files_restored', 0)}")
        else:
            print(f"   ❌ Rollback failed: {rollback_data.get('error')}")
    else:
        print(f"   ❌ Rollback request failed: {rollback_response.text}")
    
    print("\n" + "-" * 50)
    print("✅ Manual rollback test completed!")
    return True


if __name__ == "__main__":
    try:
        # Check if server is running
        print("Checking if DockWINterface server is running...")
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("❌ Server is not responding. Please start the server first.")
            sys.exit(1)
        print("✅ Server is running\n")
        
        # Run tests
        test_rollback_flow()
        print("\n" + "=" * 50 + "\n")
        test_rollback_trigger()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at", BASE_URL)
        print("Please ensure the DockWINterface server is running.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
