from functools import wraps
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Project
from workspaces.models import WorkspaceMember


def project_member_required(allowed_roles=None):
    """
    Decorator to check if user is a member of the project's workspace.
    Optionally can check for specific roles.
    Supports both 'pk' and 'project_pk' URL parameter names.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Support both 'pk' and 'project_pk' parameter names
            project_id = kwargs.get('pk') or kwargs.get('project_pk')

            if not project_id:
                messages.error(request, 'Invalid project ID.')
                return redirect('workspaces:list')

            project = get_object_or_404(Project.objects.select_related('workspace'), pk=project_id)
            try:
                membership = WorkspaceMember.objects.get(
                    workspace=project.workspace,
                    user=request.user
                )

                # Check if role is allowed
                if allowed_roles and membership.role not in allowed_roles:
                    messages.error(request, 'You do not have permission to perform this action.')
                    return redirect('projects:detail', pk=project_id)

                # Add membership and project to request for easy access in views
                request.workspace_membership = membership
                request.project = project

                return view_func(request, *args, **kwargs)
            except WorkspaceMember.DoesNotExist:
                messages.error(request, 'You are not a member of this project\'s workspace.')
                return redirect('workspaces:list')

        return wrapper
    return decorator


def project_admin_or_pm_required(view_func):
    """
    Decorator to check if user is an admin or PM in the project's workspace.
    """
    return project_member_required(['admin', 'pm'])(view_func)
