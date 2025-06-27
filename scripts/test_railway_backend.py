#!/usr/bin/env python3
"""
Test script for Railway backend API
"""

import requests
import json
import sys


def test_railway_backend():
    """Test Railway backend endpoints"""
    base_url = "https://adaptable-liberation-production.up.railway.app"

    print("🔍 Testing Railway backend...")

    # Test 1: Health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: User endpoint
    print("\n2. Testing user endpoint...")
    try:
        response = requests.get(
            f"{base_url}/api/auth/users/email/jeprasher@gmail.com", timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
            # Try to get more details
            try:
                error_data = response.json()
                print(f"   Error details: {json.dumps(error_data, indent=2)}")
            except:
                pass
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Create user endpoint (should fail with "already exists")
    print("\n3. Testing create user endpoint (should fail)...")
    try:
        user_data = {"email": "jeprasher@gmail.com", "name": "Test User"}
        response = requests.post(
            f"{base_url}/api/auth/users",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print(f"   Expected error: {response.json()}")
        else:
            print(f"   Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Check if there are any other endpoints
    print("\n4. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API docs available")
        else:
            print("   ❌ API docs not available")
    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    test_railway_backend()
