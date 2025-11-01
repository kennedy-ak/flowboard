"""
Test script for Mnotify SMS integration
Run this script to test SMS sending functionality
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowboard.settings')
django.setup()

import httpx
from django.conf import settings


def test_mnotify_sms(phone_number, message):
    """
    Test SMS sending using Mnotify API

    Args:
        phone_number: Recipient phone number (e.g., '0557782728')
        message: SMS message to send
    """
    # Get Mnotify credentials from settings
    api_key = getattr(settings, 'MNOTIFY_API_KEY', '')
    sender = getattr(settings, 'MNOTIFY_SENDER', 'FlowBoard')

    if not api_key:
        print("❌ Error: MNOTIFY_API_KEY not configured in settings.py")
        print("Please add your API key to flowboard/settings.py:")
        print("MNOTIFY_API_KEY = 'your-api-key-here'")
        return

    print(f"📱 Testing Mnotify SMS Integration")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"To: {phone_number}")
    print(f"From: {sender}")
    print(f"Message: {message}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    try:
        # Mnotify API endpoint
        url = f"https://api.mnotify.com/api/sms/quick?key={api_key}"

        # Prepare payload
        payload = {
            "recipient": [phone_number],
            "sender": sender,
            "message": message,
            "is_schedule": False,
            "schedule_date": ""
        }

        headers = {"Content-Type": "application/json"}

        # Send SMS
        print("Sending SMS...")
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            result = response.json()

            if response.status_code == 200:
                print("✅ SMS sent successfully!")
                print(f"Response: {result}")
            else:
                print(f"❌ Failed to send SMS")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {result}")

    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Example usage
    print("\n" + "="*50)
    print("  MNOTIFY SMS TEST SCRIPT")
    print("="*50 + "\n")

    # Get phone number and message from user
    phone = input("Enter recipient phone number (e.g., 0557782728): ").strip()

    if not phone:
        print("❌ Phone number is required!")
        sys.exit(1)

    # Use default test message or get from user
    use_default = input("Use default test message? (y/n): ").strip().lower()

    if use_default == 'y':
        message = "Hello! This is a test SMS from FlowBoard. Your invitation system is working correctly!"
    else:
        message = input("Enter your message: ").strip()
        if not message:
            print("❌ Message is required!")
            sys.exit(1)

    print()
    test_mnotify_sms(phone, message)
    print("\n" + "="*50 + "\n")
