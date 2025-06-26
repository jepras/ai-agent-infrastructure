#!/usr/bin/env python3
"""
Test script for Outlook and Pipedrive APIs using OAuth client credentials
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_pipedrive_oauth():
    """Test Pipedrive API with OAuth client credentials"""
    print("🔍 Testing Pipedrive OAuth...")

    client_id = os.getenv("PIPEDRIVE_CLIENT_ID")
    client_secret = os.getenv("PIPEDRIVE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ PIPEDRIVE_CLIENT_ID or PIPEDRIVE_CLIENT_SECRET not found")
        return False

    # Get access token using client credentials flow
    try:
        token_url = "https://oauth.pipedrive.com/oauth/token"
        token_data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        token_response = requests.post(token_url, data=token_data)

        if token_response.status_code == 200:
            token_info = token_response.json()
            access_token = token_info["access_token"]
            print("✅ Got Pipedrive access token")

            # Test API with token
            api_response = requests.get(
                "https://api.pipedrive.com/v1/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if api_response.status_code == 200:
                user_data = api_response.json()
                print(f"✅ Pipedrive API working! User: {user_data['data']['name']}")

                # Test deals endpoint
                deals_response = requests.get(
                    "https://api.pipedrive.com/v1/deals",
                    headers={"Authorization": f"Bearer {access_token}"},
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
                print(f"❌ Pipedrive API failed: {api_response.status_code}")
                return False
        else:
            print(
                f"❌ Failed to get Pipedrive token: {token_response.status_code} - {token_response.text}"
            )
            return False

    except Exception as e:
        print(f"❌ Pipedrive OAuth error: {e}")
        return False


def test_outlook_oauth():
    """Test Outlook API with OAuth client credentials"""
    print("\n🔍 Testing Outlook OAuth...")

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
                users_data = graph_response.json()
                print(
                    f"✅ Outlook Graph API working! Found {len(users_data.get('value', []))} users"
                )

                # Test mail endpoint
                mail_response = requests.get(
                    "https://graph.microsoft.com/v1.0/me/messages",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                )

                if mail_response.status_code == 200:
                    mail_data = mail_response.json()
                    print(
                        f"✅ Mail endpoint working! Found {len(mail_data.get('value', []))} messages"
                    )
                else:
                    print(f"⚠️ Mail endpoint failed: {mail_response.status_code}")

                return True
            else:
                print(f"❌ Outlook Graph API failed: {graph_response.status_code}")
                return False
        else:
            print(
                f"❌ Failed to get Outlook token: {token_response.status_code} - {token_response.text}"
            )
            return False

    except Exception as e:
        print(f"❌ Outlook OAuth error: {e}")
        return False


def main():
    """Run OAuth API tests"""
    print("🚀 Testing OAuth API Connections...\n")

    pipedrive_success = test_pipedrive_oauth()
    outlook_success = test_outlook_oauth()

    print(f"\n📊 Results:")
    print(f"Pipedrive OAuth: {'✅ Working' if pipedrive_success else '❌ Failed'}")
    print(f"Outlook OAuth: {'✅ Working' if outlook_success else '❌ Failed'}")

    if pipedrive_success and outlook_success:
        print("\n🎉 All OAuth APIs are working! Ready to proceed with development.")
    else:
        print(
            "\n⚠️ Some OAuth APIs failed. Check your client credentials and try again."
        )


if __name__ == "__main__":
    main()
