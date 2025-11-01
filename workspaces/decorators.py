from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Workspace, WorkspaceMember


def workspace_member_required(allowed_roles=None):
    """
    Decorator to check if user is a member of the workspace.
    Optionally can check for specific roles.

    Usage:
        @workspace_member_required()
        @workspace_member_required(['admin'])
        @workspace_member_required(['admin', 'pm'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, pk, *args, **kwargs):
            workspace = get_object_or_404(Workspace, pk=pk)
            try:
                membership = WorkspaceMember.objects.get(
                    workspace=workspace,
                    user=request.user
                )

                # Check if role is allowed
                if allowed_roles and membership.role not in allowed_roles:
                    messages.error(request, 'You do not have permission to perform this action.')
                    return redirect('workspaces:detail', pk=pk)

                # Add membership to request for easy access in views
                request.workspace_membership = membership
                request.workspace = workspace

                return view_func(request, pk, *args, **kwargs)
            except WorkspaceMember.DoesNotExist:
                messages.error(request, 'You are not a member of this workspace.')
                return redirect('workspaces:list')

        return wrapper
    return decorator


def workspace_admin_required(view_func):
    """
    Decorator to check if user is an admin of the workspace.
    """
    return workspace_member_required(['admin'])(view_func)


def workspace_admin_or_pm_required(view_func):
    """
    Decorator to check if user is an admin or PM of the workspace.
    """
    return workspace_member_required(['admin', 'pm'])(view_func)
