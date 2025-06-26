#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))


def test_database_connection():
    """Test database connection and table creation"""
    print("🔍 Testing database connection...")

    try:
        from app.core.database import create_tables, get_db
        from app.models.database import User, UserProfile, UsageLimit

        # Create tables
        create_tables()
        print("✅ Database tables created successfully")

        # Test database session
        db = next(get_db())
        print("✅ Database session established")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_auth_manager():
    """Test AuthManager functionality"""
    print("\n🔍 Testing AuthManager...")

    try:
        from app.core.database import get_db
        from app.auth.manager import AuthManager
        from app.models.database import User

        db = next(get_db())
        auth_manager = AuthManager(db)

        # Test user creation
        test_email = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}@example.com"
        user = auth_manager.create_user(email=test_email, name="Test User")
        print(f"✅ User created: {user.email}")

        # Test user retrieval
        retrieved_user = auth_manager.get_user_by_email(test_email)
        if retrieved_user and retrieved_user.id == user.id:
            print("✅ User retrieval works")
        else:
            print("❌ User retrieval failed")
            return False

        # Test credential storage
        test_api_key = "sk-test123456789"
        credential = auth_manager.store_credential(
            user_id=str(user.id), credential_type="openai_api_key", data=test_api_key
        )
        print("✅ Credential storage works")

        # Test credential retrieval
        retrieved_key = auth_manager.get_credential(
            user_id=str(user.id), credential_type="openai_api_key"
        )
        if retrieved_key == test_api_key:
            print("✅ Credential retrieval and decryption works")
        else:
            print("❌ Credential retrieval failed")
            return False

        # Test service status
        status = auth_manager.get_service_status(str(user.id))
        if status["openai"]:
            print("✅ Service status detection works")
        else:
            print("❌ Service status detection failed")
            return False

        db.close()
        return True

    except Exception as e:
        print(f"❌ AuthManager test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")

    base_url = os.getenv("API_URL", "http://localhost:8000")

    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint works")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False

        # Test user creation endpoint
        test_email = f"api-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}@example.com"
        user_data = {"email": test_email, "name": "API Test User"}

        response = requests.post(
            f"{base_url}/api/auth/users",
            json=user_data,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            user = response.json()
            print(f"✅ User creation endpoint works: {user['email']}")

            # Test user retrieval endpoint
            response = requests.get(f"{base_url}/api/auth/users/{user['id']}")
            if response.status_code == 200:
                print("✅ User retrieval endpoint works")
            else:
                print(f"❌ User retrieval endpoint failed: {response.status_code}")
                return False

            # Test API key storage endpoint
            api_key_data = {"api_key": "sk-api-test123456789", "provider": "openai"}

            response = requests.post(
                f"{base_url}/api/auth/users/{user['id']}/api-keys",
                json=api_key_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                print("✅ API key storage endpoint works")
            else:
                print(f"❌ API key storage endpoint failed: {response.status_code}")
                return False

            # Test service status endpoint
            response = requests.get(
                f"{base_url}/api/auth/users/{user['id']}/service-status"
            )
            if response.status_code == 200:
                status = response.json()
                if status["openai"]:
                    print("✅ Service status endpoint works")
                else:
                    print("❌ Service status endpoint failed")
                    return False
            else:
                print(f"❌ Service status endpoint failed: {response.status_code}")
                return False

        else:
            print(f"❌ User creation endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API at {base_url}")
        print("Make sure the backend server is running")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting authentication system tests...\n")

    tests = [
        ("Database Connection", test_database_connection),
        ("AuthManager", test_auth_manager),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Authentication system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
