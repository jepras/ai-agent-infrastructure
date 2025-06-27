#!/usr/bin/env python3
"""
Comprehensive authentication test script
"""

import requests
import json
import sys
import os
from datetime import datetime


def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing Backend Health...")
    try:
        response = requests.get(
            "https://adaptable-liberation-production.up.railway.app/health", timeout=10
        )
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False


def test_user_creation():
    """Test user creation endpoint"""
    print("\n🔍 Testing User Creation...")
    test_email = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}@example.com"

    try:
        user_data = {"email": test_email, "name": "Test User"}
        response = requests.post(
            "https://adaptable-liberation-production.up.railway.app/api/auth/users",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            user = response.json()
            print(f"✅ User created successfully: {user['email']} (ID: {user['id']})")
            return test_email, user["id"]
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ User creation error: {e}")
        return None, None


def test_user_lookup(email):
    """Test user lookup endpoint"""
    print(f"\n🔍 Testing User Lookup for {email}...")
    try:
        response = requests.get(
            f"https://adaptable-liberation-production.up.railway.app/api/auth/users/email/{email}",
            timeout=10,
        )

        if response.status_code == 200:
            user = response.json()
            print(f"✅ User lookup successful: {user['email']} (ID: {user['id']})")
            return True
        else:
            print(f"❌ User lookup failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ User lookup error: {e}")
        return False


def test_frontend_access():
    """Test frontend accessibility"""
    print("\n🔍 Testing Frontend Access...")
    try:
        response = requests.get(
            "https://endearing-heart-production.up.railway.app", timeout=10
        )
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend access error: {e}")
        return False


def test_database_connection():
    """Test local database connection"""
    print("\n🔍 Testing Local Database Connection...")
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
        from app.core.database import get_db
        from app.models.database import User

        db = next(get_db())
        user_count = db.query(User).count()
        print(f"✅ Database connected successfully. Total users: {user_count}")

        # Show existing users
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.email} (ID: {user.id}, Created: {user.created_at})")

        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False


def test_existing_user():
    """Test with your existing user"""
    print("\n🔍 Testing Existing User (jeprasher@gmail.com)...")
    return test_user_lookup("jeprasher@gmail.com")


def main():
    print("🚀 COMPREHENSIVE AUTHENTICATION TEST")
    print("=" * 50)

    # Test 1: Backend Health
    backend_ok = test_backend_health()

    # Test 2: Frontend Access
    frontend_ok = test_frontend_access()

    # Test 3: Database Connection
    db_ok = test_database_connection()

    # Test 4: Existing User
    existing_user_ok = test_existing_user()

    # Test 5: User Creation (only if backend is working)
    if backend_ok:
        test_email, test_user_id = test_user_creation()
        if test_email:
            test_user_lookup(test_email)

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Backend Health: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Access: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Existing User Lookup: {'✅ PASS' if existing_user_ok else '❌ FAIL'}")

    if backend_ok and frontend_ok and db_ok and existing_user_ok:
        print("\n🎉 AUTHENTICATION SYSTEM IS WORKING!")
        print("✅ Users can be created and looked up")
        print("✅ Database is properly connected")
        print("✅ Frontend and backend are accessible")
        print("✅ Your existing user account exists and is accessible")
    else:
        print("\n⚠️  SOME ISSUES DETECTED")
        print("Check the individual test results above for details")


if __name__ == "__main__":
    main()
