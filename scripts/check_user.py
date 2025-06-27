#!/usr/bin/env python3
"""
Script to check if a user exists in the database
"""

import sys
import os
import argparse

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))


def check_user_exists(email: str):
    """Check if a user exists in the database by email"""
    try:
        from app.core.database import get_db
        from app.models.database import User, UserProfile, UsageLimit

        print(f"🔍 Checking if user with email '{email}' exists...")

        # Get database session
        db = next(get_db())

        # Query for user
        user = db.query(User).filter(User.email == email).first()

        if user:
            print(f"✅ User found!")
            print(f"   ID: {user.id}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.name or 'Not set'}")
            print(f"   Email Verified: {user.email_verified}")
            print(f"   Created: {user.created_at}")
            print(f"   Updated: {user.updated_at}")

            # Check if profile exists
            profile = db.query(UserProfile).filter(UserProfile.id == user.id).first()
            if profile:
                print(f"   Profile: ✅ (Monitoring: {profile.monitoring_enabled})")
            else:
                print(f"   Profile: ❌ (Missing)")

            # Check if usage limits exist
            usage_limit = (
                db.query(UsageLimit).filter(UsageLimit.user_id == user.id).first()
            )
            if usage_limit:
                print(
                    f"   Usage Limits: ✅ (Daily emails: {usage_limit.daily_email_limit})"
                )
            else:
                print(f"   Usage Limits: ❌ (Missing)")

        else:
            print(f"❌ User with email '{email}' not found in database")

        db.close()
        return user is not None

    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return False


def list_all_users():
    """List all users in the database"""
    try:
        from app.core.database import get_db
        from app.models.database import User

        print("🔍 Listing all users in database...")

        # Get database session
        db = next(get_db())

        # Query all users
        users = db.query(User).all()

        if users:
            print(f"✅ Found {len(users)} user(s):")
            for user in users:
                print(f"   - {user.email} (ID: {user.id}, Created: {user.created_at})")
        else:
            print("❌ No users found in database")

        db.close()
        return len(users)

    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Check if a user exists in the database"
    )
    parser.add_argument("--email", help="Email address to check")
    parser.add_argument(
        "--list-all", action="store_true", help="List all users in database"
    )

    args = parser.parse_args()

    if args.list_all:
        list_all_users()
    elif args.email:
        check_user_exists(args.email)
    else:
        print("Please provide either --email or --list-all")
        parser.print_help()


if __name__ == "__main__":
    main()
