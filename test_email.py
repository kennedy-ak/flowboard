#!/usr/bin/env python3
"""
Test script to verify Gmail SMTP credentials work with FlowBoard.
This script sends a test email to verify the provided app password.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowboard.settings')
django.setup()

# Import Django email functionality after setup
from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Test email functionality with the provided credentials."""
    
    # Configure email settings for Gmail
    email_config = {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': 'smtp.gmail.com',
        'EMAIL_PORT': 465,  # Use 465 for SSL
        'EMAIL_USE_TLS': False,  # Use SSL for port 465
        'EMAIL_USE_SSL': True,   # Enable SSL for port 465
        'EMAIL_HOST_USER': 'kennedyakogokweku@gmail.com',
        'EMAIL_HOST_PASSWORD': 'wzbrhlbyzxchrygz',
        'DEFAULT_FROM_EMAIL': 'kennedyakogokweku@gmail.com',
    }
    
    # Temporarily override settings for testing
    original_settings = {}
    for key, value in email_config.items():
        original_settings[key] = getattr(settings, key, None)
        setattr(settings, key, value)
    
    try:
        print("Testing Gmail SMTP credentials...")
        print(f"From: {email_config['EMAIL_HOST_USER']}")
        print(f"To: akogokennedy@gmail.com")
        print(f"SMTP Server: {email_config['EMAIL_HOST']}:{email_config['EMAIL_PORT']}")
        print("-" * 50)
        
        # Send test email
        subject = "FlowBoard Email Test"
        message = """
        Hello,
        
        This is a test email to verify that the Gmail app password is working correctly with FlowBoard.
        
        If you received this email, it means:
        1. The SMTP configuration is correct
        2. The app password is valid
        3. Gmail is allowing the connection
        
        Test Details:
        - Sent from: kennedyakogokweku@gmail.com
        - App Password: wzbrhlbyzxchrygz (first 8 chars: wzbrhlby)
        - Timestamp: {} 
        
        Best regards,
        FlowBoard Test Script
        """.format(__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
        
        # Send the email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=email_config['EMAIL_HOST_USER'],
            recipient_list=['akogokennedy@gmail.com'],
            fail_silently=False,
        )
        
        if result == 1:
            print("SUCCESS: Email sent successfully!")
            print("The Gmail app password is working correctly.")
            print("Check akogokennedy@gmail.com for the test email.")
        else:
            print("FAILED: Email was not sent successfully.")
            print("Result code:", result)
            
    except Exception as e:
        print("ERROR: Failed to send email")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nPossible issues:")
        print("1. App password might be incorrect")
        print("2. Gmail might be blocking the connection")
        print("3. 2-factor authentication might not be enabled")
        print("4. Less secure app access might be disabled")
        
    finally:
        # Restore original settings
        for key, value in original_settings.items():
            if value is not None:
                setattr(settings, key, value)

if __name__ == "__main__":
    print("FlowBoard Gmail SMTP Test")
    print("=" * 50)
    test_email()
    print("=" * 50)
    print("Test completed.")