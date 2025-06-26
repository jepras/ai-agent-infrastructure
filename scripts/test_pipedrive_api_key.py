#!/usr/bin/env python3
"""
Test Pipedrive API with API key (simpler than OAuth)
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_pipedrive_api_key():
    """Test Pipedrive API with API key"""
    print("🔍 Testing Pipedrive API with API Key...")

    api_key = os.getenv("PIPEDRIVE_API_KEY")
    if not api_key:
        print("❌ PIPEDRIVE_API_KEY not found in .env file")
        print("💡 Get your API key from: https://app.pipedrive.com/settings/api")
        return False

    try:
        # Test user info
        response = requests.get(
            "https://api.pipedrive.com/v1/users/me",
            headers={"Authorization": f"Bearer {api_key}"},
        )

        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Pipedrive API working! User: {user_data['data']['name']}")

            # Test deals endpoint
            deals_response = requests.get(
                "https://api.pipedrive.com/v1/deals",
                headers={"Authorization": f"Bearer {api_key}"},
            )

            if deals_response.status_code == 200:
                deals_data = deals_response.json()
                print(
                    f"✅ Deals endpoint working! Found {len(deals_data.get('data', []))} deals"
                )
            else:
                print(f"⚠️ Deals endpoint failed: {deals_response.status_code}")

            # Test pipelines
            pipelines_response = requests.get(
                "https://api.pipedrive.com/v1/pipelines",
                headers={"Authorization": f"Bearer {api_key}"},
            )

            if pipelines_response.status_code == 200:
                pipelines_data = pipelines_response.json()
                print(
                    f"✅ Pipelines endpoint working! Found {len(pipelines_data.get('data', []))} pipelines"
                )
            else:
                print(f"⚠️ Pipelines endpoint failed: {pipelines_response.status_code}")

            return True
        else:
            print(f"❌ Pipedrive API failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Pipedrive API error: {e}")
        return False


if __name__ == "__main__":
    test_pipedrive_api_key()
