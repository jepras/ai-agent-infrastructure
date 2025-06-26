#!/usr/bin/env python3
"""
Test script for Outlook and Pipedrive APIs
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
        print("❌ PIPEDRIVE_API_KEY not found in environment variables")
        return False

    # Test user info
    try:
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

            return True
        else:
            print(f"❌ Pipedrive API failed: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Pipedrive API error: {e}")
        return False


def test_outlook_api():
    """Test Outlook API with client credentials"""
    print("\n🔍 Testing Outlook API...")

    client_id = os.getenv("OUTLOOK_CLIENT_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ OUTLOOK_CLIENT_ID or OUTLOOK_CLIENT_SECRET not found")
        return False

    # Get access token using client credentials flow
    try:
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
        }

        token_response = requests.post(token_url, data=token_data)

        if token_response.status_code == 200:
            token_info = token_response.json()
            access_token = token_info["access_token"]
            print("✅ Got Outlook access token")

            # Test Graph API
            graph_response = requests.get(
                "https://graph.microsoft.com/v1.0/users",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )

            if graph_response.status_code == 200:
                print("✅ Outlook Graph API working!")
                return True
            else:
                print(f"❌ Outlook Graph API failed: {graph_response.status_code}")
                return False
        else:
            print(f"❌ Failed to get Outlook token: {token_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Outlook API error: {e}")
        return False


def main():
    """Run API tests"""
    print("🚀 Testing API Connections...\n")

    pipedrive_success = test_pipedrive_api()
    outlook_success = test_outlook_api()

    print(f"\n📊 Results:")
    print(f"Pipedrive API: {'✅ Working' if pipedrive_success else '❌ Failed'}")
    print(f"Outlook API: {'✅ Working' if outlook_success else '❌ Failed'}")

    if pipedrive_success and outlook_success:
        print("\n🎉 All APIs are working! Ready to proceed with development.")
    else:
        print("\n⚠️ Some APIs failed. Check your credentials and try again.")


if __name__ == "__main__":
    main()
