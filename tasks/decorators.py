from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Task, Subtask
from workspaces.models import WorkspaceMember


def task_member_required(allowed_roles=None):
    """
    Decorator to check if user is a member of the task's workspace.
    Supports both 'pk' and 'task_pk' URL parameter names.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Support both 'pk' and 'task_pk' parameter names
            task_id = kwargs.get('pk') or kwargs.get('task_pk')

            if not task_id:
                messages.error(request, 'Invalid task ID.')
                return redirect('workspaces:list')

            task = get_object_or_404(Task.objects.select_related('project__workspace'), pk=task_id)
            try:
                membership = WorkspaceMember.objects.get(
                    workspace=task.project.workspace,
                    user=request.user
                )
                if allowed_roles and membership.role not in allowed_roles:
                    messages.error(request, 'You do not have permission to perform this action.')
                    return redirect('tasks:detail', pk=task_id)
                request.workspace_membership = membership
                request.task = task
                return view_func(request, *args, **kwargs)
            except WorkspaceMember.DoesNotExist:
                messages.error(request, 'You are not a member of this task\'s workspace.')
                return redirect('workspaces:list')
        return wrapper
    return decorator


def task_admin_or_pm_required(view_func):
    """Decorator to check if user is an admin or PM in the task's workspace."""
    return task_member_required(['admin', 'pm'])(view_func)
