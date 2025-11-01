"""
Utility functions for workspace invitations.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import logging
import httpx

logger = logging.getLogger(__name__)


def send_invitation_email(invitation, request):
    """
    Send email invitation to join a workspace.

    Args:
        invitation: WorkspaceInvitation object
        request: HTTP request object (to build absolute URL)
    """
    # Build invitation URL
    invitation_url = request.build_absolute_uri(
        reverse('workspaces:accept_invitation', args=[invitation.token])
    )

    subject = f'You\'re invited to join {invitation.workspace.name} on FlowBoard'

    # Personalized greeting
    greeting = f"Hello {invitation.recipient_name}," if invitation.recipient_name else "Hello,"

    message = f"""
{greeting}

{invitation.created_by.username} has invited you to join the workspace "{invitation.workspace.name}" on FlowBoard!

Your Invitation Details:
━━━━━━━━━━━━━━━━━━━━
👤 Name: {invitation.recipient_name}
📧 Email: {invitation.email}
🏢 Workspace: {invitation.workspace.name}
👔 Role: {invitation.get_role_display()}
⏰ Expires: {invitation.expires_at.strftime('%B %d, %Y at %I:%M %p')}

Click the link below to accept this invitation:
{invitation_url}

What happens next?
• If you already have an account: Simply log in and you'll be added to the workspace
• If you're new: You'll be guided through a quick registration process

This is an exclusive invitation for you. The link can only be used once and will expire in 7 days.

Welcome to FlowBoard!
Best regards,
The FlowBoard Team
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        logger.info(f"Invitation email sent to {invitation.email} for workspace {invitation.workspace.name}")
    except Exception as e:
        logger.error(f"Failed to send invitation email to {invitation.email}: {str(e)}")


def send_invitation_sms(invitation, request):
    """
    Send SMS invitation to join a workspace using Mnotify API.

    Args:
        invitation: WorkspaceInvitation object
        request: HTTP request object (to build absolute URL)
    """
    # Check if phone number is provided
    if not invitation.recipient_phone:
        logger.info(f"No phone number provided for invitation to {invitation.email}")
        return

    # Build invitation URL
    invitation_url = request.build_absolute_uri(
        reverse('workspaces:accept_invitation', args=[invitation.token])
    )

    # Personalized SMS message (keep it concise for SMS)
    message = f"""Hi {invitation.recipient_name}!

{invitation.created_by.username} invited you to join "{invitation.workspace.name}" on FlowBoard as {invitation.get_role_display()}.

Accept here: {invitation_url}

Expires: {invitation.expires_at.strftime('%b %d, %Y')}

- FlowBoard Team"""

    # Check if Mnotify API key is configured
    mnotify_api_key = getattr(settings, 'MNOTIFY_API_KEY', None)
    mnotify_sender = getattr(settings, 'MNOTIFY_SENDER', 'FlowBoard')

    if not mnotify_api_key:
        logger.warning(f"Mnotify API key not configured. SMS to {invitation.recipient_phone} not sent.")
        # For development, log the SMS message
        logger.info(f"SMS MESSAGE (would be sent to {invitation.recipient_phone}):\n{message}")
        return

    try:
        # Mnotify API endpoint
        url = f"https://api.mnotify.com/api/sms/quick?key={mnotify_api_key}"

        # Prepare payload
        payload = {
            "recipient": [invitation.recipient_phone],
            "sender": mnotify_sender,
            "message": message,
            "is_schedule": False,
            "schedule_date": ""
        }

        headers = {"Content-Type": "application/json"}

        # Send SMS using httpx synchronous client
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            result = response.json()

            # Check if SMS was sent successfully
            if response.status_code == 200:
                logger.info(f"Invitation SMS sent to {invitation.recipient_phone} for workspace {invitation.workspace.name}. Response: {result}")
            else:
                logger.error(f"Failed to send SMS to {invitation.recipient_phone}. Status: {response.status_code}, Response: {result}")

    except httpx.HTTPError as e:
        logger.error(f"HTTP error while sending SMS to {invitation.recipient_phone}: {str(e)}")
        # Log the message that would have been sent
        logger.info(f"SMS MESSAGE (failed to send to {invitation.recipient_phone}):\n{message}")
    except Exception as e:
        logger.error(f"Failed to send invitation SMS to {invitation.recipient_phone}: {str(e)}")
        # Log the message that would have been sent
        logger.info(f"SMS MESSAGE (failed to send to {invitation.recipient_phone}):\n{message}")
