"""
Signal handlers for task assignment notifications.
"""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Task, Subtask
from .utils import (
    send_task_assignment_email,
    send_task_assignment_sms,
    send_subtask_assignment_email,
    send_subtask_assignment_sms
)
import logging

logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=Task.assigned_to.through)
def task_assignment_notification(sender, instance, action, pk_set, **kwargs):
    """
    Send notifications when users are assigned to a task.
    Triggered when the assigned_to many-to-many relationship changes.

    Args:
        sender: The through model for the many-to-many relationship
        instance: The Task instance
        action: The type of update (pre_add, post_add, pre_remove, post_remove, etc.)
        pk_set: Set of primary keys of users being added/removed
        kwargs: Additional keyword arguments
    """
    if action == "post_add" and pk_set:
        # Users have been added to the task
        from accounts.models import User

        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)

                # Send email notification
                send_task_assignment_email(user, instance)

                # Send SMS notification
                send_task_assignment_sms(user, instance)

                logger.info(f"Notifications sent to {user.username} for task '{instance.title}'")
            except User.DoesNotExist:
                logger.error(f"User with ID {user_id} does not exist")
            except Exception as e:
                logger.error(f"Error sending notifications to user {user_id}: {str(e)}")


@receiver(m2m_changed, sender=Subtask.assigned_to.through)
def subtask_assignment_notification(sender, instance, action, pk_set, **kwargs):
    """
    Send notifications when users are assigned to a subtask.
    Triggered when the assigned_to many-to-many relationship changes.

    Args:
        sender: The through model for the many-to-many relationship
        instance: The Subtask instance
        action: The type of update (pre_add, post_add, pre_remove, post_remove, etc.)
        pk_set: Set of primary keys of users being added/removed
        kwargs: Additional keyword arguments
    """
    if action == "post_add" and pk_set:
        # Users have been added to the subtask
        from accounts.models import User

        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)

                # Send email notification
                send_subtask_assignment_email(user, instance)

                # Send SMS notification
                send_subtask_assignment_sms(user, instance)

                logger.info(f"Notifications sent to {user.username} for subtask '{instance.title}'")
            except User.DoesNotExist:
                logger.error(f"User with ID {user_id} does not exist")
            except Exception as e:
                logger.error(f"Error sending notifications to user {user_id}: {str(e)}")
