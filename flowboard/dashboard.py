"""
Dashboard views for different user roles.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from workspaces.models import Workspace, WorkspaceMember
from projects.models import Project
from tasks.models import Task
from datetime import datetime, timedelta


@login_required
def dashboard(request):
    """
    Role-based dashboard that redirects to appropriate view based on user's primary role.
    Shows the dashboard for the highest role the user has across all workspaces.
    """
    # Get user's memberships
    memberships = WorkspaceMember.objects.filter(user=request.user).select_related('workspace')

    if not memberships.exists():
        # User is not part of any workspace, show empty state
        return render(request, 'dashboard/no_workspace.html')

    # Determine highest role
    has_admin = memberships.filter(role='admin').exists()
    has_pm = memberships.filter(role='pm').exists()

    if has_admin:
        return admin_dashboard(request)
    elif has_pm:
        return pm_dashboard(request)
    else:
        return member_dashboard(request)


@login_required
def admin_dashboard(request):
    """
    Admin dashboard - overview of all workspaces, projects, and users.
    Shows comprehensive statistics across all workspaces where user is admin.
    """
    # Get workspaces where user is admin
    admin_workspaces = Workspace.objects.filter(
        members__user=request.user,
        members__role='admin'
    ).annotate(
        project_count=Count('projects', distinct=True),
        member_count=Count('members', distinct=True)
    ).distinct()

    # Get all projects in admin workspaces
    all_projects = Project.objects.filter(
        workspace__in=admin_workspaces
    ).select_related('workspace').annotate(
        task_count=Count('tasks', distinct=True)
    )

    # Get all tasks in admin workspaces
    all_tasks = Task.objects.filter(
        project__workspace__in=admin_workspaces
    ).select_related('project', 'created_by')

    # Calculate statistics
    total_workspaces = admin_workspaces.count()
    total_projects = all_projects.count()
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(status='done').count()
    in_progress_tasks = all_tasks.filter(status='in_progress').count()
    todo_tasks = all_tasks.filter(status='todo').count()

    # Get recent activity
    recent_projects = all_projects.order_by('-created_at')[:5]
    recent_tasks = all_tasks.order_by('-created_at')[:10]

    # Get overdue tasks
    overdue_tasks = all_tasks.filter(
        due_date__lt=datetime.now().date(),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:10]

    # Get upcoming tasks (next 7 days)
    upcoming_tasks = all_tasks.filter(
        due_date__gte=datetime.now().date(),
        due_date__lte=datetime.now().date() + timedelta(days=7),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:10]

    context = {
        'role': 'admin',
        'workspaces': admin_workspaces,
        'total_workspaces': total_workspaces,
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'todo_tasks': todo_tasks,
        'recent_projects': recent_projects,
        'recent_tasks': recent_tasks,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def pm_dashboard(request):
    """
    Project Manager dashboard - projects they manage, sprint progress, upcoming tasks.
    Shows data from workspaces where user is PM or Admin.
    """
    # Get workspaces where user is PM or Admin
    pm_workspaces = Workspace.objects.filter(
        members__user=request.user,
        members__role__in=['pm', 'admin']
    ).distinct()

    # Get projects in these workspaces
    managed_projects = Project.objects.filter(
        workspace__in=pm_workspaces
    ).select_related('workspace').annotate(
        task_count=Count('tasks', distinct=True),
        sprint_count=Count('sprints', distinct=True)
    ).order_by('-created_at')

    # Get all tasks in managed projects
    all_tasks = Task.objects.filter(
        project__in=managed_projects
    ).select_related('project', 'sprint')

    # Get active sprints
    from projects.models import Sprint
    active_sprints = Sprint.objects.filter(
        project__in=managed_projects,
        status='active'
    ).select_related('project').order_by('end_date')

    # Calculate sprint progress for each active sprint
    sprint_data = []
    for sprint in active_sprints:
        sprint_tasks = all_tasks.filter(sprint=sprint)
        total = sprint_tasks.count()
        completed = sprint_tasks.filter(status='done').count()
        progress = int((completed / total) * 100) if total > 0 else 0
        sprint_data.append({
            'sprint': sprint,
            'total_tasks': total,
            'completed_tasks': completed,
            'progress': progress,
        })

    # Statistics
    total_projects = managed_projects.count()
    total_tasks = all_tasks.count()
    completed_tasks = all_tasks.filter(status='done').count()
    in_progress_tasks = all_tasks.filter(status='in_progress').count()

    # Get overdue tasks
    overdue_tasks = all_tasks.filter(
        due_date__lt=datetime.now().date(),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:10]

    # Get upcoming tasks (next 7 days)
    upcoming_tasks = all_tasks.filter(
        due_date__gte=datetime.now().date(),
        due_date__lte=datetime.now().date() + timedelta(days=7),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:10]

    # Recent activity
    recent_tasks = all_tasks.order_by('-created_at')[:10]

    context = {
        'role': 'pm',
        'workspaces': pm_workspaces,
        'managed_projects': managed_projects[:5],  # Show top 5 on dashboard
        'total_projects': total_projects,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'sprint_data': sprint_data,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'recent_tasks': recent_tasks,
    }

    return render(request, 'dashboard/pm_dashboard.html', context)


@login_required
def member_dashboard(request):
    """
    Member dashboard - tasks assigned to them, completion percentage, due dates.
    Shows only tasks assigned to the user.
    """
    # Get workspaces where user is a member
    user_workspaces = Workspace.objects.filter(
        members__user=request.user
    ).distinct()

    # Get tasks assigned to the user
    assigned_tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('project', 'sprint').order_by('-created_at')

    # Get subtasks assigned to the user
    from tasks.models import Subtask
    assigned_subtasks = Subtask.objects.filter(
        assigned_to=request.user
    ).select_related('task', 'task__project')

    # Calculate statistics
    total_tasks = assigned_tasks.count()
    completed_tasks = assigned_tasks.filter(status='done').count()
    in_progress_tasks = assigned_tasks.filter(status='in_progress').count()
    todo_tasks = assigned_tasks.filter(status='todo').count()

    # Calculate completion percentage
    completion_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    # Get overdue tasks
    overdue_tasks = assigned_tasks.filter(
        due_date__lt=datetime.now().date(),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')

    # Get upcoming tasks (next 7 days)
    upcoming_tasks = assigned_tasks.filter(
        due_date__gte=datetime.now().date(),
        due_date__lte=datetime.now().date() + timedelta(days=7),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')

    # Get tasks by status for display
    tasks_in_progress = assigned_tasks.filter(status='in_progress')[:5]
    tasks_todo = assigned_tasks.filter(status='todo')[:5]
    tasks_completed = assigned_tasks.filter(status='done')[:5]

    # Subtask statistics
    total_subtasks = assigned_subtasks.count()
    completed_subtasks = assigned_subtasks.filter(status='done').count()

    context = {
        'role': 'member',
        'workspaces': user_workspaces,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'todo_tasks': todo_tasks,
        'completion_percentage': completion_percentage,
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'tasks_in_progress': tasks_in_progress,
        'tasks_todo': tasks_todo,
        'tasks_completed': tasks_completed,
        'total_subtasks': total_subtasks,
        'completed_subtasks': completed_subtasks,
    }

    return render(request, 'dashboard/member_dashboard.html', context)
