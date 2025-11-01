# FlowBoard Invitation System - User Guide

## How to Invite Users to Your Workspace

### Prerequisites
- You must be an **Admin** of the workspace
- The person you're inviting needs a valid email address

---

## Method 1: From Workspace Members Page

1. **Navigate to Workspace**
   - Go to: Dashboard → Workspaces → Click your workspace

2. **Go to Members**
   - Click "Members" in the workspace menu

3. **Click "Invite User"**
   - Blue button at the top of the page

4. **Fill the Form**
   - Full Name: Enter recipient's full name (for personalization)
   - Email: Enter recipient's email address
   - Phone Number: Enter recipient's phone number (optional - for SMS notifications)
   - Role: Choose Admin, Project Manager, or Member
   - Click "Send Invitation"

---

## Method 2: From Invitations Management

1. **Navigate to Workspace**
   - Dashboard → Workspaces → Click your workspace

2. **Click "Members"**
   - Then click "View Invitations" button

3. **Send New Invitation**
   - Click "Send Invitation" button
   - Fill out the form
   - Submit

---

## What the Invitation Includes

### Email Content (Personalized)
- Personalized greeting with recipient's name
- Sender's username (who invited them)
- Workspace name
- Role they're being invited as
- Recipient's email address
- Unique invitation link
- Expiration date (7 days from sending)
- Instructions for new and existing users

### SMS Notification (Optional)
If phone number is provided:
- Personalized message with recipient's name
- Sender's username
- Workspace name
- Role
- Invitation link (shortened in SMS)
- Expiration date
- Note: SMS is sent in addition to email, not instead of it

### Invitation Link
Format: `http://127.0.0.1:8000/workspaces/invite/[unique-token]/`

**Features:**
- Valid for 7 days
- Can only be used once
- Unique per invitation
- Works for both new and existing users

---

## Managing Sent Invitations

### View All Invitations
Go to: **Workspace → Members → View Invitations**

You'll see three sections:

#### 1. Pending Invitations (Green)
- Not yet accepted
- Still valid
- Can be copied or revoked

**Actions:**
- **Copy Link** - Share manually via chat, etc.
- **Revoke** - Cancel the invitation

#### 2. Accepted Invitations
- Successfully used
- Shows who accepted and when
- Cannot be revoked

#### 3. Expired Invitations (Yellow)
- Past expiration date
- No longer valid
- Can be deleted for cleanup

---

## Invitation Flow Diagrams

### For New Users:
```
1. Receive email
2. Click invitation link
3. Redirected to Registration page
   → Shows "Invitation to [Workspace]" banner
4. Fill registration form
5. Account created + Auto-added to workspace
6. Redirected to workspace
```

### For Existing Users:
```
1. Receive email
2. Click invitation link
3. Redirected to Login page
4. Login with credentials
5. Auto-added to workspace
6. Redirected to workspace
```

### For Logged-in Users:
```
1. Receive email
2. Click invitation link (while already logged in)
3. Immediately added to workspace
4. Redirected to workspace
```

---

## Important Notes

### Email Delivery
- In **development mode**, emails are printed to the console (terminal)
- To actually send emails, configure SMTP in `settings.py`:
  ```python
  EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
  EMAIL_HOST = 'smtp.gmail.com'
  EMAIL_HOST_USER = 'your-email@gmail.com'
  EMAIL_HOST_PASSWORD = 'your-app-password'
  ```

### SMS Delivery (Optional Feature)
- **Phone number field is optional** - you can leave it blank if you only want email notifications
- In **development mode**, SMS messages are logged to the console (won't actually send)
- To actually send SMS, you need to:
  1. Install httpx: `pip install httpx`
  2. Get your Mnotify API key:
     - Sign up at https://www.mnotify.com
     - Get your API key from the dashboard
  3. Configure Mnotify credentials in `settings.py`:
     ```python
     MNOTIFY_API_KEY = 'your-api-key-here'
     MNOTIFY_SENDER = 'FlowBoard'  # Max 11 characters
     ```
- If Mnotify is not configured, invitations will still work via email only
- Mnotify supports multiple countries and provides affordable SMS rates

### Invitation Expiration
- Default: **7 days**
- Configurable in `workspaces/models.py` (WorkspaceInvitation model)

### Duplicate Prevention
- Cannot invite someone already in the workspace
- Cannot send duplicate pending invitations to the same email

### Security
- Tokens are cryptographically secure (32-byte random)
- One-time use only
- Expire automatically after 7 days

---

## Troubleshooting

### "Invitation has expired"
- The link is older than 7 days
- **Solution:** Admin needs to send a new invitation

### "Invitation already used"
- Someone already accepted this invitation
- **Solution:** Send a new invitation if needed

### "Already a member"
- User is already in the workspace
- **Solution:** Check Members list

### Email not received
- Check spam/junk folder
- In development, check the terminal/console output
- **Alternative:** Copy the invitation link and send it manually via chat

---

## Quick Tips

1. **Copy Links Manually**
   - If email isn't working, copy the invitation link from the Invitations page
   - Share via Slack, Teams, WhatsApp, etc.

2. **Batch Invitations**
   - You can send multiple invitations at once
   - Each gets a unique link

3. **Role Selection**
   - Choose roles carefully - they determine permissions
   - You can change roles later from Members page

4. **Monitor Invitations**
   - Regularly check the Invitations page
   - Clean up expired invitations
   - Revoke unused ones if needed

---

## Role Descriptions

| Role | Permissions |
|------|-------------|
| **Admin** | Full control: manage workspace, members, projects, tasks |
| **Project Manager** | Manage projects, create/assign tasks, manage sprints |
| **Member** | View tasks, update assigned tasks, add comments |

---

## Example Workflow

**Scenario:** You want to add your team member John to your workspace

1. **Go to your workspace**
   - Dashboard → Click "My Team Workspace"

2. **Navigate to Members**
   - Click "Members" button

3. **Click "Invite User"**

4. **Fill the form:**
   - Full Name: `John Doe`
   - Email: `john.doe@company.com`
   - Phone Number: `+1234567890` (optional)
   - Role: `Project Manager`

5. **Click "Send Invitation"**

6. **John receives personalized notifications:**
   - **Email**: Personalized message with his name, workspace details, and role
   - **SMS** (if phone provided): Quick notification with invitation link
   - Clicks the link from either channel
   - Registers (if new) or Logs in (if existing)
   - Automatically added as Project Manager
   - Starts working immediately!

---

## For More Help

- Check the main README.md for setup instructions
- Contact support if you have issues
- Admin panel: `http://127.0.0.1:8000/admin/` for manual user management

---

**Last Updated:** 2025-10-31
