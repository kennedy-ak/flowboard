"""
Notification utility functions for Email and SMS.
"""
from django.core.mail import send_mail
from django.conf import settings
import logging

# Try to import Twilio, but don't fail if it's not installed
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    Client = None

logger = logging.getLogger(__name__)


def send_task_assignment_email(user, task):
    """
    Send email notification when a user is assigned to a task.

    Args:
        user: User object who was assigned
        task: Task object they were assigned to
    """
    subject = f'You have been assigned to: {task.title}'
    message = f"""
Hello {user.username},

You have been assigned to a new task in FlowBoard.

Task: {task.title}
Project: {task.project.name}
Workspace: {task.project.workspace.name}
Status: {task.get_status_display()}
Due Date: {task.due_date if task.due_date else 'Not set'}

Description:
{task.description if task.description else 'No description provided'}

Please log in to FlowBoard to view more details and update the task status.

Best regards,
FlowBoard Team
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {user.email} for task assignment: {task.title}")
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {str(e)}")


def send_task_assignment_sms(user, task):
    """
    Send SMS notification when a user is assigned to a task.
    Uses Twilio for SMS delivery.

    Args:
        user: User object who was assigned
        task: Task object they were assigned to
    """
    # Check if Twilio is available
    if not TWILIO_AVAILABLE:
        logger.warning("Twilio package is not installed. SMS not sent.")
        return

    # Check if user has a phone number
    if not user.phone_number:
        logger.warning(f"User {user.username} has no phone number. SMS not sent.")
        return

    # Check if Twilio credentials are configured
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not configured. SMS not sent.")
        return

    message_body = f"""
FlowBoard: You've been assigned to '{task.title}' in project '{task.project.name}'.
Due: {task.due_date if task.due_date else 'Not set'}
Log in to view details.
    """.strip()

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        logger.info(f"SMS sent to {user.phone_number} for task assignment: {task.title}. SID: {message.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS to {user.phone_number}: {str(e)}")


def send_subtask_assignment_email(user, subtask):
    """
    Send email notification when a user is assigned to a subtask.

    Args:
        user: User object who was assigned
        subtask: Subtask object they were assigned to
    """
    subject = f'You have been assigned to subtask: {subtask.title}'
    message = f"""
Hello {user.username},

You have been assigned to a new subtask in FlowBoard.

Subtask: {subtask.title}
Parent Task: {subtask.task.title}
Project: {subtask.task.project.name}
Workspace: {subtask.task.project.workspace.name}
Status: {subtask.get_status_display()}
Due Date: {subtask.due_date if subtask.due_date else 'Not set'}

Description:
{subtask.description if subtask.description else 'No description provided'}

Please log in to FlowBoard to view more details and update the subtask status.

Best regards,
FlowBoard Team
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Email sent to {user.email} for subtask assignment: {subtask.title}")
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {str(e)}")


def send_subtask_assignment_sms(user, subtask):
    """
    Send SMS notification when a user is assigned to a subtask.
    Uses Twilio for SMS delivery.

    Args:
        user: User object who was assigned
        subtask: Subtask object they were assigned to
    """
    # Check if Twilio is available
    if not TWILIO_AVAILABLE:
        logger.warning("Twilio package is not installed. SMS not sent.")
        return

    # Check if user has a phone number
    if not user.phone_number:
        logger.warning(f"User {user.username} has no phone number. SMS not sent.")
        return

    # Check if Twilio credentials are configured
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not configured. SMS not sent.")
        return

    message_body = f"""
FlowBoard: You've been assigned to subtask '{subtask.title}' in task '{subtask.task.title}'.
Due: {subtask.due_date if subtask.due_date else 'Not set'}
Log in to view details.
    """.strip()

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone_number
        )
        logger.info(f"SMS sent to {user.phone_number} for subtask assignment: {subtask.title}. SID: {message.sid}")
    except Exception as e:
        logger.error(f"Failed to send SMS to {user.phone_number}: {str(e)}")
