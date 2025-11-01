from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Project, Sprint
from .forms import ProjectForm, SprintForm
from .decorators import project_member_required, project_admin_or_pm_required
from workspaces.models import Workspace, WorkspaceMember


@login_required
def project_list(request):
    """
    List all projects in workspaces where the user is a member.
    """
    # Get workspace filter if provided
    workspace_id = request.GET.get('workspace')

    # Get all workspaces where user is a member
    user_workspaces = Workspace.objects.filter(members__user=request.user)

    if workspace_id:
        projects = Project.objects.filter(
            workspace_id=workspace_id,
            workspace__members__user=request.user
        ).select_related('workspace').distinct()
        current_workspace = get_object_or_404(Workspace, pk=workspace_id)
    else:
        projects = Project.objects.filter(
            workspace__members__user=request.user
        ).select_related('workspace').distinct()
        current_workspace = None

    projects = projects.annotate(
        task_count=Count('tasks', distinct=True),
        sprint_count=Count('sprints', distinct=True)
    ).order_by('-created_at')

    context = {
        'projects': projects,
        'workspaces': user_workspaces,
        'current_workspace': current_workspace,
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_create(request):
    """
    Create a new project. Only admins and PMs can create projects.
    """
    workspace_id = request.GET.get('workspace')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user

            # Check if user has permission in the workspace
            try:
                membership = WorkspaceMember.objects.get(
                    workspace=project.workspace,
                    user=request.user
                )
                if membership.role not in ['admin', 'pm']:
                    messages.error(request, 'You do not have permission to create projects in this workspace.')
                    return redirect('workspaces:list')

                project.save()
                messages.success(request, f'Project "{project.name}" created successfully!')
                return redirect('projects:detail', pk=project.pk)
            except WorkspaceMember.DoesNotExist:
                messages.error(request, 'You are not a member of this workspace.')
                return redirect('workspaces:list')
    else:
        form = ProjectForm()

    # Filter workspaces to only show those where user is admin or PM
    user_workspaces = Workspace.objects.filter(
        members__user=request.user,
        members__role__in=['admin', 'pm']
    ).distinct()

    form.fields['workspace'].queryset = user_workspaces

    # Pre-select workspace if provided
    if workspace_id:
        form.fields['workspace'].initial = workspace_id

    context = {'form': form}
    return render(request, 'projects/project_form.html', context)


@login_required
@project_member_required()
def project_detail(request, pk):
    """
    View project details with sprints and tasks.
    """
    project = request.project
    membership = request.workspace_membership

    # Get project statistics
    sprints = project.sprints.all().order_by('-start_date')
    recent_tasks = project.tasks.select_related('created_by').prefetch_related('assigned_to')[:10]

    # Calculate project progress
    total_tasks = project.tasks.count()
    completed_tasks = project.tasks.filter(status='done').count()
    progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    context = {
        'project': project,
        'membership': membership,
        'sprints': sprints,
        'recent_tasks': recent_tasks,
        'is_admin': membership.role == 'admin',
        'is_pm': membership.role in ['admin', 'pm'],
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
@project_admin_or_pm_required
def project_edit(request, pk):
    """
    Edit project details. Only admins and PMs can edit.
    """
    project = request.project

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('projects:detail', pk=pk)
    else:
        form = ProjectForm(instance=project)

    # Limit workspace choices to those where user is admin or PM
    user_workspaces = Workspace.objects.filter(
        members__user=request.user,
        members__role__in=['admin', 'pm']
    ).distinct()
    form.fields['workspace'].queryset = user_workspaces

    context = {
        'form': form,
        'project': project,
        'is_edit': True
    }
    return render(request, 'projects/project_form.html', context)


@login_required
@project_admin_or_pm_required
def project_delete(request, pk):
    """
    Delete project. Only admins and PMs can delete.
    """
    project = request.project

    if request.method == 'POST':
        project_name = project.name
        workspace_pk = project.workspace.pk
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('workspaces:detail', pk=workspace_pk)

    context = {'project': project}
    return render(request, 'projects/project_confirm_delete.html', context)


# Sprint Views

@login_required
@project_admin_or_pm_required
def sprint_create(request, project_pk):
    """
    Create a new sprint for a project. Only admins and PMs can create sprints.
    """
    project = request.project

    if request.method == 'POST':
        form = SprintForm(request.POST)
        if form.is_valid():
            sprint = form.save(commit=False)
            sprint.project = project
            sprint.save()
            messages.success(request, f'Sprint "{sprint.name}" created successfully!')
            return redirect('projects:detail', pk=project_pk)
    else:
        form = SprintForm()

    context = {
        'form': form,
        'project': project
    }
    return render(request, 'projects/sprint_form.html', context)


@login_required
@project_admin_or_pm_required
def sprint_edit(request, project_pk, pk):
    """
    Edit sprint details. Only admins and PMs can edit.
    """
    project = request.project
    sprint = get_object_or_404(Sprint, pk=pk, project=project)

    if request.method == 'POST':
        form = SprintForm(request.POST, instance=sprint)
        if form.is_valid():
            form.save()
            messages.success(request, f'Sprint "{sprint.name}" updated successfully!')
            return redirect('projects:detail', pk=project_pk)
    else:
        form = SprintForm(instance=sprint)

    context = {
        'form': form,
        'project': project,
        'sprint': sprint,
        'is_edit': True
    }
    return render(request, 'projects/sprint_form.html', context)


@login_required
@project_admin_or_pm_required
def sprint_delete(request, project_pk, pk):
    """
    Delete sprint. Only admins and PMs can delete.
    """
    project = request.project
    sprint = get_object_or_404(Sprint, pk=pk, project=project)

    if request.method == 'POST':
        sprint_name = sprint.name
        sprint.delete()
        messages.success(request, f'Sprint "{sprint_name}" deleted successfully!')
        return redirect('projects:detail', pk=project_pk)

    context = {
        'project': project,
        'sprint': sprint
    }
    return render(request, 'projects/sprint_confirm_delete.html', context)
