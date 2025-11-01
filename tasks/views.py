from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Task, Subtask, Comment
from .forms import TaskForm, SubtaskForm, CommentForm
from .decorators import task_member_required, task_admin_or_pm_required
from projects.models import Project
from workspaces.models import Workspace, WorkspaceMember
from accounts.models import User


@login_required
def task_list(request):
    """List all tasks in projects where the user is a member."""
    project_id = request.GET.get('project')
    status_filter = request.GET.get('status')

    user_workspaces = Workspace.objects.filter(members__user=request.user)

    if project_id:
        tasks = Task.objects.filter(
            project_id=project_id,
            project__workspace__members__user=request.user
        ).select_related('project', 'created_by').prefetch_related('assigned_to').distinct()
        current_project = get_object_or_404(Project, pk=project_id)
    else:
        tasks = Task.objects.filter(
            project__workspace__members__user=request.user
        ).select_related('project', 'created_by').prefetch_related('assigned_to').distinct()
        current_project = None

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    tasks = tasks.order_by('-created_at')

    context = {
        'tasks': tasks,
        'current_project': current_project,
        'status_filter': status_filter,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    """Create a new task. Only admins and PMs can create tasks."""
    project_id = request.GET.get('project')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user

            try:
                membership = WorkspaceMember.objects.get(
                    workspace=task.project.workspace,
                    user=request.user
                )
                if membership.role not in ['admin', 'pm']:
                    messages.error(request, 'You do not have permission to create tasks in this project.')
                    return redirect('workspaces:list')

                task.save()
                form.save_m2m()  # Save many-to-many relationships
                messages.success(request, f'Task "{task.title}" created successfully!')
                return redirect('tasks:detail', pk=task.pk)
            except WorkspaceMember.DoesNotExist:
                messages.error(request, 'You are not a member of this workspace.')
                return redirect('workspaces:list')
    else:
        form = TaskForm()

    # Filter projects to only show those where user is admin or PM
    user_projects = Project.objects.filter(
        workspace__members__user=request.user,
        workspace__members__role__in=['admin', 'pm']
    ).distinct()

    form.fields['project'].queryset = user_projects

    # Pre-select project if provided
    if project_id:
        form.fields['project'].initial = project_id
        # Filter sprints based on selected project
        try:
            project = Project.objects.get(pk=project_id)
            form.fields['sprint'].queryset = project.sprints.all()
        except Project.DoesNotExist:
            pass

    # Filter assigned_to to workspace members
    if project_id:
        try:
            project = Project.objects.get(pk=project_id)
            workspace_members = User.objects.filter(workspace_memberships__workspace=project.workspace).distinct()
            form.fields['assigned_to'].queryset = workspace_members
        except Project.DoesNotExist:
            pass

    context = {'form': form}
    return render(request, 'tasks/task_form.html', context)


@login_required
@task_member_required()
def task_detail(request, pk):
    """View task details with subtasks and comments."""
    task = request.task
    membership = request.workspace_membership

    subtasks = task.subtasks.select_related('created_by').prefetch_related('assigned_to').all()
    comments = task.comments.select_related('user').order_by('created_at')

    # Check if user is assigned to this task
    is_assigned = request.user in task.assigned_to.all()

    context = {
        'task': task,
        'membership': membership,
        'subtasks': subtasks,
        'comments': comments,
        'is_admin': membership.role == 'admin',
        'is_pm': membership.role in ['admin', 'pm'],
        'is_assigned': is_assigned,
        'can_edit': membership.role in ['admin', 'pm'] or is_assigned,
        'comment_form': CommentForm(),
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
@task_admin_or_pm_required
def task_edit(request, pk):
    """Edit task details. Only admins and PMs can edit."""
    task = request.task

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('tasks:detail', pk=pk)
    else:
        form = TaskForm(instance=task)

    # Filter projects and sprints
    user_projects = Project.objects.filter(
        workspace__members__user=request.user,
        workspace__members__role__in=['admin', 'pm']
    ).distinct()
    form.fields['project'].queryset = user_projects
    form.fields['sprint'].queryset = task.project.sprints.all()

    # Filter assigned_to to workspace members
    workspace_members = User.objects.filter(workspace_memberships__workspace=task.project.workspace).distinct()
    form.fields['assigned_to'].queryset = workspace_members

    context = {
        'form': form,
        'task': task,
        'is_edit': True
    }
    return render(request, 'tasks/task_form.html', context)


@login_required
@task_admin_or_pm_required
def task_delete(request, pk):
    """Delete task. Only admins and PMs can delete."""
    task = request.task

    if request.method == 'POST':
        task_title = task.title
        project_pk = task.project.pk
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('projects:detail', pk=project_pk)

    context = {'task': task}
    return render(request, 'tasks/task_confirm_delete.html', context)


@login_required
@task_member_required()
def task_update_status(request, pk):
    """Update task status. Members can update if assigned, admins/PMs can always update."""
    task = request.task
    membership = request.workspace_membership
    is_assigned = request.user in task.assigned_to.all()

    if membership.role not in ['admin', 'pm'] and not is_assigned:
        messages.error(request, 'You do not have permission to update this task.')
        return redirect('tasks:detail', pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            messages.success(request, f'Task status updated to "{task.get_status_display()}"!')

    return redirect('tasks:detail', pk=pk)


# Subtask Views

@login_required
@task_admin_or_pm_required
def subtask_create(request, task_pk):
    """Create a new subtask. Only admins and PMs can create subtasks."""
    task = request.task

    if request.method == 'POST':
        form = SubtaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.task = task
            subtask.created_by = request.user
            subtask.save()
            form.save_m2m()
            messages.success(request, f'Subtask "{subtask.title}" created successfully!')
            return redirect('tasks:detail', pk=task_pk)
    else:
        form = SubtaskForm()

    # Filter assigned_to to workspace members
    workspace_members = User.objects.filter(workspace_memberships__workspace=task.project.workspace).distinct()
    form.fields['assigned_to'].queryset = workspace_members

    context = {
        'form': form,
        'task': task
    }
    return render(request, 'tasks/subtask_form.html', context)


@login_required
def subtask_edit(request, task_pk, pk):
    """Edit subtask details."""
    task = get_object_or_404(Task.objects.select_related('project__workspace'), pk=task_pk)
    subtask = get_object_or_404(Subtask, pk=pk, task=task)

    membership = WorkspaceMember.objects.filter(
        workspace=task.project.workspace,
        user=request.user
    ).first()

    if not membership:
        messages.error(request, 'You are not a member of this workspace.')
        return redirect('workspaces:list')

    if membership.role not in ['admin', 'pm']:
        messages.error(request, 'You do not have permission to edit subtasks.')
        return redirect('tasks:detail', pk=task_pk)

    if request.method == 'POST':
        form = SubtaskForm(request.POST, instance=subtask)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subtask "{subtask.title}" updated successfully!')
            return redirect('tasks:detail', pk=task_pk)
    else:
        form = SubtaskForm(instance=subtask)

    workspace_members = User.objects.filter(workspace_memberships__workspace=task.project.workspace).distinct()
    form.fields['assigned_to'].queryset = workspace_members

    context = {
        'form': form,
        'task': task,
        'subtask': subtask,
        'is_edit': True
    }
    return render(request, 'tasks/subtask_form.html', context)


@login_required
def subtask_delete(request, task_pk, pk):
    """Delete subtask."""
    task = get_object_or_404(Task.objects.select_related('project__workspace'), pk=task_pk)
    subtask = get_object_or_404(Subtask, pk=pk, task=task)

    membership = WorkspaceMember.objects.filter(
        workspace=task.project.workspace,
        user=request.user
    ).first()

    if not membership or membership.role not in ['admin', 'pm']:
        messages.error(request, 'You do not have permission to delete subtasks.')
        return redirect('tasks:detail', pk=task_pk)

    if request.method == 'POST':
        subtask_title = subtask.title
        subtask.delete()
        messages.success(request, f'Subtask "{subtask_title}" deleted successfully!')
        return redirect('tasks:detail', pk=task_pk)

    context = {
        'task': task,
        'subtask': subtask
    }
    return render(request, 'tasks/subtask_confirm_delete.html', context)


@login_required
def subtask_update_status(request, task_pk, pk):
    """Update subtask status."""
    task = get_object_or_404(Task.objects.select_related('project__workspace'), pk=task_pk)
    subtask = get_object_or_404(Subtask, pk=pk, task=task)

    membership = WorkspaceMember.objects.filter(
        workspace=task.project.workspace,
        user=request.user
    ).first()

    if not membership:
        messages.error(request, 'You are not a member of this workspace.')
        return redirect('workspaces:list')

    is_assigned = request.user in subtask.assigned_to.all()

    if membership.role not in ['admin', 'pm'] and not is_assigned:
        messages.error(request, 'You do not have permission to update this subtask.')
        return redirect('tasks:detail', pk=task_pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Subtask.STATUS_CHOICES):
            subtask.status = new_status
            subtask.save()
            messages.success(request, f'Subtask status updated to "{subtask.get_status_display()}"!')

    return redirect('tasks:detail', pk=task_pk)


# Comment Views

@login_required
@task_member_required()
def comment_add(request, task_pk):
    """Add a comment to a task."""
    task = request.task

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')

    return redirect('tasks:detail', pk=task_pk)


@login_required
def subtask_comment_add(request, task_pk, subtask_pk):
    """Add a comment to a subtask."""
    task = get_object_or_404(Task.objects.select_related('project__workspace'), pk=task_pk)
    subtask = get_object_or_404(Subtask, pk=subtask_pk, task=task)

    membership = WorkspaceMember.objects.filter(
        workspace=task.project.workspace,
        user=request.user
    ).first()

    if not membership:
        messages.error(request, 'You are not a member of this workspace.')
        return redirect('workspaces:list')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.subtask = subtask
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')

    return redirect('tasks:detail', pk=task_pk)
