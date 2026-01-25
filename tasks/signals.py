"""
Signal handlers for task assignment notifications.
"""
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Task, Subtask
from .tasks import (
    send_task_assignment_email_async,
    send_task_assignment_sms_async,
    send_subtask_assignment_email_async,
    send_subtask_assignment_sms_async
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
        for user_id in pk_set:
            try:
                # Queue background tasks (non-blocking)
                send_task_assignment_email_async(user_id, instance.id)
                send_task_assignment_sms_async(user_id, instance.id)

                logger.info(f"Background notifications queued for user {user_id}, task '{instance.title}'")
            except Exception as e:
                logger.error(f"Error queuing notifications for user {user_id}: {str(e)}")


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
        for user_id in pk_set:
            try:
                # Queue background tasks (non-blocking)
                send_subtask_assignment_email_async(user_id, instance.id)
                send_subtask_assignment_sms_async(user_id, instance.id)

                logger.info(f"Background notifications queued for user {user_id}, subtask '{instance.title}'")
            except Exception as e:
                logger.error(f"Error queuing notifications for user {user_id}: {str(e)}")
