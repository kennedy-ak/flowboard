# SMS Setup Guide - Mnotify Integration

## Overview

FlowBoard uses **Mnotify API** to send SMS notifications for workspace invitations. This guide will help you set up SMS functionality in your FlowBoard application.

---

## Why Mnotify?

- **Affordable**: Cost-effective SMS rates
- **Reliable**: High delivery rates
- **Global**: Supports multiple countries
- **Simple API**: Easy to integrate
- **No Minimum**: No minimum balance requirements

---

## Setup Instructions

### Step 1: Create Mnotify Account

1. Visit [https://www.mnotify.com](https://www.mnotify.com)
2. Click **"Sign Up"** or **"Register"**
3. Fill in your details:
   - Full Name
   - Email Address
   - Phone Number
   - Password
4. Verify your email address
5. Log in to your dashboard

### Step 2: Get Your API Key

1. Log in to your Mnotify dashboard
2. Navigate to **"Settings"** or **"API Keys"**
3. Copy your API Key (looks like: `iGdCKQNz7p6aRQsJWA8xq5sHa`)
4. Keep this key secure - do not share it publicly

### Step 3: Add Credits (Optional for Testing)

- Mnotify usually provides free test credits for new accounts
- To add more credits:
  1. Go to **"Buy Credits"** or **"Top Up"**
  2. Select your preferred payment method
  3. Add credits to your account

### Step 4: Configure FlowBoard

1. Open `flowboard/settings.py`
2. Find the SMS Configuration section:
   ```python
   # SMS Configuration (Mnotify API - add your credentials)
   MNOTIFY_API_KEY = ''  # Add your Mnotify API key
   MNOTIFY_SENDER = 'FlowBoard'  # Sender name (max 11 characters)
   ```

3. Update with your credentials:
   ```python
   MNOTIFY_API_KEY = 'iGdCKQNz7p6aRQsJWA8xq5sHa'  # Your actual API key
   MNOTIFY_SENDER = 'FlowBoard'  # Or your preferred sender name
   ```

4. **Important Notes:**
   - `MNOTIFY_SENDER` must be 11 characters or less
   - Use only alphanumeric characters (no spaces or special characters)
   - Examples: `FlowBoard`, `MyCompany`, `TeamApp`

### Step 5: Install Required Package

Make sure `httpx` is installed:

```bash
pip install httpx
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

---

## Testing SMS Functionality

### Option 1: Use Test Script

We've provided a test script to verify your SMS setup:

```bash
python test_mnotify_sms.py
```

Follow the prompts:
1. Enter recipient phone number
2. Choose to use default message or enter custom message
3. Check if SMS is sent successfully

### Option 2: Test via Application

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Log in as workspace admin
3. Go to any workspace
4. Click **"Invite"** button
5. Fill in the invitation form:
   - Full Name: Test User
   - Email: test@example.com
   - **Phone Number: Your phone number**
   - Role: Member
6. Submit the form
7. Check your phone for the SMS

### Option 3: Check Console Logs

If API key is not configured, SMS messages will be logged to the console:

```
WARNING - Mnotify API key not configured. SMS to 0557782728 not sent.
INFO - SMS MESSAGE (would be sent to 0557782728):
Hi John Doe!

Alice invited you to join "My Workspace" on FlowBoard as Project Manager.
...
```

---

## Phone Number Format

Mnotify accepts various phone number formats:

### Recommended Format
- **With Country Code**: `+233557782728` (Ghana)
- **Local Format**: `0557782728` (depends on your Mnotify account settings)

### Examples by Country
- **Ghana**: `+233557782728` or `0557782728`
- **Nigeria**: `+2348012345678` or `08012345678`
- **Kenya**: `+254712345678` or `0712345678`
- **International**: Always use `+` followed by country code

---

## Troubleshooting

### Issue 1: SMS Not Received

**Possible Causes:**
- API key is incorrect
- Insufficient credits in Mnotify account
- Phone number format is wrong
- Network issues

**Solutions:**
1. Verify API key in settings.py
2. Check Mnotify dashboard for credit balance
3. Use correct phone number format
4. Check Mnotify SMS logs in dashboard

### Issue 2: Error "Mnotify API key not configured"

**Solution:**
Add your API key to `flowboard/settings.py`:
```python
MNOTIFY_API_KEY = 'your-api-key-here'
```

### Issue 3: SMS Logged but Not Sent

**Cause:**
API key is empty or not configured

**Solution:**
Configure your API key in settings.py (see Step 4 above)

### Issue 4: HTTP Error or Timeout

**Possible Causes:**
- Internet connection issues
- Mnotify API is down
- Firewall blocking requests

**Solutions:**
1. Check your internet connection
2. Visit https://www.mnotify.com to verify service status
3. Check firewall settings
4. Try again after a few minutes

---

## SMS Message Format

When a user is invited, they receive an SMS like this:

```
Hi John Doe!

Alice invited you to join "My Workspace" on FlowBoard as Project Manager.

Accept here: http://127.0.0.1:8000/workspaces/invite/abc123...

Expires: Dec 07, 2025

- FlowBoard Team
```

**Message Details:**
- Personalized with recipient's name
- Shows who sent the invitation
- Includes workspace name and role
- Provides clickable invitation link
- Shows expiration date

---

## Cost Considerations

### SMS Pricing (Approximate)
- **Ghana**: ₵0.04 - ₵0.06 per SMS
- **Nigeria**: ₦3 - ₦5 per SMS
- **Other Countries**: Varies by location

### Tips to Reduce Costs
1. Make phone number optional (email-only invitations)
2. Only send SMS for important invitations
3. Combine multiple invitations into one session
4. Monitor usage in Mnotify dashboard

---

## Production Deployment

### Security Best Practices

1. **Use Environment Variables**
   ```python
   # In settings.py
   import os
   MNOTIFY_API_KEY = os.environ.get('MNOTIFY_API_KEY', '')
   ```

2. **Never Commit API Keys**
   - Add to `.gitignore`:
     ```
     .env
     */settings.py
     ```

3. **Use Separate Keys**
   - Development: Use test API key
   - Production: Use production API key

### Environment Variables Setup

Create `.env` file:
```env
MNOTIFY_API_KEY=your-production-api-key
MNOTIFY_SENDER=FlowBoard
```

Update `settings.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()

MNOTIFY_API_KEY = os.environ.get('MNOTIFY_API_KEY', '')
MNOTIFY_SENDER = os.environ.get('MNOTIFY_SENDER', 'FlowBoard')
```

---

## Monitoring and Logs

### Check SMS Status

1. **In Application Logs**
   - Success: `Invitation SMS sent to 0557782728...`
   - Failure: `Failed to send SMS to 0557782728...`

2. **In Mnotify Dashboard**
   - View all sent SMS
   - Check delivery status
   - Monitor credit usage
   - See failed messages

### Django Logging

SMS events are logged using Django's logging system. Check your console or log files for:
- `INFO`: Successful sends
- `WARNING`: Configuration issues
- `ERROR`: Failed sends

---

## Alternative: Email-Only Mode

If you don't want to use SMS:

1. Leave `MNOTIFY_API_KEY` empty in settings.py
2. Don't fill in phone number when sending invitations
3. Invitations will be sent via email only
4. System will continue to work normally

---

## Support

### Mnotify Support
- Website: https://www.mnotify.com
- Email: support@mnotify.com
- Documentation: https://developers.mnotify.com

### FlowBoard SMS Issues
- Check `INVITATION_GUIDE.md` for invitation flow
- Run `test_mnotify_sms.py` to debug
- Check console logs for error messages
- Verify API key and credits in Mnotify dashboard

---

## Summary

✅ **Required:**
- Mnotify account with API key
- `httpx` package installed
- API key configured in settings.py

✅ **Optional:**
- Phone number in invitation form
- Credits in Mnotify account (for actual sending)

✅ **Features:**
- Personalized SMS messages
- Automatic fallback to email if SMS fails
- Console logging for development
- Production-ready error handling

---

**Last Updated:** 2025-10-31
