"""
Background task definitions for task notifications.
"""
from background_task import background
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import httpx
import logging

logger = logging.getLogger(__name__)


@background(schedule=0)
def send_task_assignment_email_async(user_id, task_id):
    """
    Background task to send email notification when a user is assigned to a task.

    Args:
        user_id: ID of User who was assigned
        task_id: ID of Task they were assigned to
    """
    from accounts.models import User
    from tasks.models import Task

    try:
        user = User.objects.get(pk=user_id)
        task = Task.objects.select_related('project__workspace', 'created_by').get(pk=task_id)

        # Generate the task detail URL
        task_path = reverse('tasks:detail', kwargs={'pk': task.pk})
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        task_url = f"{site_url.rstrip('/')}{task_path}"

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

View Task: {task_url}

Please log in to FlowBoard to view more details and update the task status.

Best regards,
FlowBoard Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Background email sent to {user.email} for task assignment: {task.title}")
    except Exception as e:
        logger.error(f"Failed to send background email: {str(e)}")
        raise  # Re-raise to trigger retry


@background(schedule=0)
def send_task_assignment_sms_async(user_id, task_id):
    """
    Background task to send SMS notification when a user is assigned to a task.

    Args:
        user_id: ID of User who was assigned
        task_id: ID of Task they were assigned to
    """
    from accounts.models import User
    from tasks.models import Task

    try:
        user = User.objects.get(pk=user_id)
        task = Task.objects.select_related('project__workspace').get(pk=task_id)

        # Check if user has a phone number
        if not user.phone_number:
            logger.warning(f"User {user.username} has no phone number. SMS not sent.")
            return

        # Generate the task detail URL
        task_path = reverse('tasks:detail', kwargs={'pk': task.pk})
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        task_url = f"{site_url.rstrip('/')}{task_path}"

        message_body = f"""FlowBoard: You've been assigned to '{task.title}' in project '{task.project.name}'.
Due: {task.due_date if task.due_date else 'Not set'}
View: {task_url}

- FlowBoard Team""".strip()

        # Check if Mnotify API key is configured
        mnotify_api_key = getattr(settings, 'MNOTIFY_API_KEY', None)
        mnotify_sender = getattr(settings, 'MNOTIFY_SENDER', 'FlowBoard')

        if not mnotify_api_key:
            logger.warning(f"Mnotify API key not configured. SMS to {user.phone_number} not sent.")
            logger.info(f"SMS MESSAGE (would be sent to {user.phone_number}):\n{message_body}")
            return

        # Mnotify API endpoint
        url = f"https://api.mnotify.com/api/sms/quick?key={mnotify_api_key}"

        # Prepare payload
        payload = {
            "recipient": [user.phone_number],
            "sender": mnotify_sender,
            "message": message_body,
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
                logger.info(f"Background SMS sent to {user.phone_number} for task: {task.title}. Response: {result}")
            else:
                logger.error(f"Failed to send SMS. Status: {response.status_code}, Response: {result}")
                raise Exception(f"SMS API error: {result}")

    except Exception as e:
        logger.error(f"Failed to send background SMS: {str(e)}")
        raise  # Re-raise to trigger retry


@background(schedule=0)
def send_subtask_assignment_email_async(user_id, subtask_id):
    """
    Background task to send email notification when a user is assigned to a subtask.

    Args:
        user_id: ID of User who was assigned
        subtask_id: ID of Subtask they were assigned to
    """
    from accounts.models import User
    from tasks.models import Subtask

    try:
        user = User.objects.get(pk=user_id)
        subtask = Subtask.objects.select_related('task__project__workspace', 'created_by').get(pk=subtask_id)

        # Generate the task detail URL (subtasks are viewed on the parent task page)
        task_path = reverse('tasks:detail', kwargs={'pk': subtask.task.pk})
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        task_url = f"{site_url.rstrip('/')}{task_path}"

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

View Task: {task_url}

Please log in to FlowBoard to view more details and update the subtask status.

Best regards,
FlowBoard Team
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Background email sent to {user.email} for subtask assignment: {subtask.title}")
    except Exception as e:
        logger.error(f"Failed to send background email: {str(e)}")
        raise  # Re-raise to trigger retry


@background(schedule=0)
def send_subtask_assignment_sms_async(user_id, subtask_id):
    """
    Background task to send SMS notification when a user is assigned to a subtask.

    Args:
        user_id: ID of User who was assigned
        subtask_id: ID of Subtask they were assigned to
    """
    from accounts.models import User
    from tasks.models import Subtask

    try:
        user = User.objects.get(pk=user_id)
        subtask = Subtask.objects.select_related('task__project__workspace').get(pk=subtask_id)

        # Check if user has a phone number
        if not user.phone_number:
            logger.warning(f"User {user.username} has no phone number. SMS not sent.")
            return

        # Generate the task detail URL (subtasks are viewed on the parent task page)
        task_path = reverse('tasks:detail', kwargs={'pk': subtask.task.pk})
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        task_url = f"{site_url.rstrip('/')}{task_path}"

        message_body = f"""FlowBoard: You've been assigned to subtask '{subtask.title}' in task '{subtask.task.title}'.
Due: {subtask.due_date if subtask.due_date else 'Not set'}
View: {task_url}

- FlowBoard Team""".strip()

        # Check if Mnotify API key is configured
        mnotify_api_key = getattr(settings, 'MNOTIFY_API_KEY', None)
        mnotify_sender = getattr(settings, 'MNOTIFY_SENDER', 'FlowBoard')

        if not mnotify_api_key:
            logger.warning(f"Mnotify API key not configured. SMS to {user.phone_number} not sent.")
            logger.info(f"SMS MESSAGE (would be sent to {user.phone_number}):\n{message_body}")
            return

        # Mnotify API endpoint
        url = f"https://api.mnotify.com/api/sms/quick?key={mnotify_api_key}"

        # Prepare payload
        payload = {
            "recipient": [user.phone_number],
            "sender": mnotify_sender,
            "message": message_body,
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
                logger.info(f"Background SMS sent to {user.phone_number} for subtask: {subtask.title}. Response: {result}")
            else:
                logger.error(f"Failed to send SMS. Status: {response.status_code}, Response: {result}")
                raise Exception(f"SMS API error: {result}")

    except Exception as e:
        logger.error(f"Failed to send background SMS: {str(e)}")
        raise  # Re-raise to trigger retry
