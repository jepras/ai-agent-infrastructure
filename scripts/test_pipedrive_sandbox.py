#!/usr/bin/env python3
"""
Test Pipedrive API with API key (production and sandbox)
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_pipedrive_api():
    """Test Pipedrive API with API key"""
    print("🔍 Testing Pipedrive API...")

    api_key = os.getenv("PIPEDRIVE_API_KEY")
    if not api_key:
        print("❌ PIPEDRIVE_API_KEY not found in .env file")
        print("💡 Get your API key from: https://app.pipedrive.com/settings/api")
        return False

    # Try both production and sandbox URLs
    base_urls = [
        "https://api.pipedrive.com/v1",
        "https://sandbox-api.pipedrive.com/v1",  # If sandbox uses different URL
    ]

    for base_url in base_urls:
        print(f"\n  Testing: {base_url}")
        try:
            # Test user info
            response = requests.get(
                f"{base_url}/users/me", headers={"Authorization": f"Bearer {api_key}"}
            )

            print(f"    Response: {response.status_code}")

            if response.status_code == 200:
                user_data = response.json()
                print(f"    ✅ Working! User: {user_data['data']['name']}")

                # Test deals endpoint
                deals_response = requests.get(
                    f"{base_url}/deals", headers={"Authorization": f"Bearer {api_key}"}
                )

                if deals_response.status_code == 200:
                    deals_data = deals_response.json()
                    print(
                        f"    ✅ Deals working! Found {len(deals_data.get('data', []))} deals"
                    )

                return True
            else:
                print(f"    ❌ Failed: {response.text}")

        except Exception as e:
            print(f"    ❌ Error: {e}")

    print("\n❌ No working API endpoint found")
    print("\n💡 Troubleshooting:")
    print("1. Check if you're in sandbox environment")
    print("2. Get API key from the correct environment")
    print("3. Make sure your app is activated in Pipedrive")
    return False


if __name__ == "__main__":
    test_pipedrive_api()
