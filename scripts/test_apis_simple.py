#!/usr/bin/env python3
"""
Simple API test script with multiple authentication methods
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_pipedrive_simple():
    """Test Pipedrive API with different methods"""
    print("🔍 Testing Pipedrive API...")

    # Try API key first (if available)
    api_key = os.getenv("PIPEDRIVE_API_KEY")
    if api_key:
        print("  Trying API key method...")
        try:
            response = requests.get(
                "https://api.pipedrive.com/v1/users/me",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            if response.status_code == 200:
                user_data = response.json()
                print(f"  ✅ API key method works! User: {user_data['data']['name']}")
                return True
            else:
                print(f"  ❌ API key failed: {response.status_code}")
        except Exception as e:
            print(f"  ❌ API key error: {e}")

    # Try OAuth client credentials
    client_id = os.getenv("PIPEDRIVE_CLIENT_ID")
    client_secret = os.getenv("PIPEDRIVE_CLIENT_SECRET")

    if client_id and client_secret:
        print("  Trying OAuth client credentials...")
        try:
            # Try different grant types
            grant_types = ["client_credentials", "authorization_code"]

            for grant_type in grant_types:
                print(f"    Testing grant_type: {grant_type}")
                token_data = {
                    "grant_type": grant_type,
                    "client_id": client_id,
                    "client_secret": client_secret,
                }

                if grant_type == "authorization_code":
                    # This would need a redirect URI and user interaction
                    print(
                        "    ⚠️ authorization_code requires user interaction - skipping"
                    )
                    continue

                token_response = requests.post(
                    "https://oauth.pipedrive.com/oauth/token", data=token_data
                )

                print(f"    Response: {token_response.status_code}")
                if token_response.status_code == 200:
                    token_info = token_response.json()
                    access_token = token_info["access_token"]
                    print(f"    ✅ Got token with {grant_type}")

                    # Test API
                    api_response = requests.get(
                        "https://api.pipedrive.com/v1/users/me",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )

                    if api_response.status_code == 200:
                        user_data = api_response.json()
                        print(f"    ✅ API works! User: {user_data['data']['name']}")
                        return True
                    else:
                        print(f"    ❌ API failed: {api_response.status_code}")
                else:
                    print(f"    ❌ Token failed: {token_response.text}")

        except Exception as e:
            print(f"  ❌ OAuth error: {e}")

    print("  ❌ No working authentication method found")
    return False


def test_outlook_simple():
    """Test Outlook API with different methods"""
    print("\n🔍 Testing Outlook API...")

    client_id = os.getenv("OUTLOOK_CLIENT_ID")
    client_secret = os.getenv("OUTLOOK_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("  ❌ OUTLOOK_CLIENT_ID or OUTLOOK_CLIENT_SECRET not found")
        return False

    print("  Trying OAuth client credentials...")
    try:
        # Try different scopes
        scopes = [
            "https://graph.microsoft.com/.default",
            "https://graph.microsoft.com/User.Read",
            "https://graph.microsoft.com/User.Read.All",
        ]

        for scope in scopes:
            print(f"    Testing scope: {scope}")
            token_data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scope,
            }

            token_response = requests.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                data=token_data,
            )

            print(f"    Response: {token_response.status_code}")
            if token_response.status_code == 200:
                token_info = token_response.json()
                access_token = token_info["access_token"]
                print(f"    ✅ Got token with scope: {scope}")

                # Test API
                graph_response = requests.get(
                    "https://graph.microsoft.com/v1.0/users",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                )

                if graph_response.status_code == 200:
                    users_data = graph_response.json()
                    print(
                        f"    ✅ API works! Found {len(users_data.get('value', []))} users"
                    )
                    return True
                else:
                    print(f"    ❌ API failed: {graph_response.status_code}")
            else:
                print(f"    ❌ Token failed: {token_response.text}")

    except Exception as e:
        print(f"  ❌ OAuth error: {e}")

    print("  ❌ No working authentication method found")
    return False


def main():
    """Run simple API tests"""
    print("🚀 Testing API Connections (Simple Method)...\n")

    pipedrive_success = test_pipedrive_simple()
    outlook_success = test_outlook_simple()

    print(f"\n📊 Results:")
    print(f"Pipedrive API: {'✅ Working' if pipedrive_success else '❌ Failed'}")
    print(f"Outlook API: {'✅ Working' if outlook_success else '❌ Failed'}")

    if pipedrive_success and outlook_success:
        print("\n🎉 All APIs are working!")
    else:
        print("\n⚠️ Some APIs failed.")
        print("\n🔧 Troubleshooting tips:")
        print(
            "1. For Pipedrive: Check if your app supports client_credentials grant type"
        )
        print(
            "2. For Outlook: Try using a personal Microsoft account instead of work account"
        )
        print("3. Check your app permissions in the developer portals")


if __name__ == "__main__":
    main()
