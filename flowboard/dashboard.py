"""
Dashboard views for different user roles.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Q, Count, Prefetch
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
@cache_page(60 * 5)  # Cache for 5 minutes
def admin_dashboard(request):
    """
    Admin dashboard - overview of all workspaces, projects, and users.
    Shows comprehensive statistics across all workspaces where user is admin.
    """
    # Get workspaces where user is admin (optimized with annotations)
    admin_workspaces = Workspace.objects.filter(
        members__user=request.user,
        members__role='admin'
    ).annotate(
        project_count=Count('projects', distinct=True),
        member_count=Count('members', distinct=True)
    ).distinct()

    # Get all projects in admin workspaces (optimized with prefetch)
    all_projects = Project.objects.filter(
        workspace__in=admin_workspaces
    ).select_related('workspace').prefetch_related('tasks').annotate(
        task_count=Count('tasks', distinct=True)
    )

    # Get all tasks in admin workspaces (optimized with select_related and prefetch_related)
    all_tasks = Task.objects.filter(
        project__workspace__in=admin_workspaces
    ).select_related('project__workspace', 'created_by', 'sprint').prefetch_related('assigned_to')

    # Calculate statistics using aggregate for better performance
    from django.db.models import Sum
    total_workspaces = admin_workspaces.count()
    total_projects = all_projects.count()

    # Use aggregate with conditional counting (single query instead of 4 separate queries)
    task_stats = all_tasks.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='done')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        todo=Count('id', filter=Q(status='todo'))
    )

    total_tasks = task_stats['total']
    completed_tasks = task_stats['completed']
    in_progress_tasks = task_stats['in_progress']
    todo_tasks = task_stats['todo']

    # Get recent activity (already optimized with select_related above)
    recent_projects = all_projects.order_by('-created_at')[:5]
    recent_tasks = all_tasks.order_by('-created_at')[:10]

    # Get overdue tasks (optimized with select_related)
    overdue_tasks = all_tasks.filter(
        due_date__lt=datetime.now().date(),
        status__in=['todo', 'in_progress']
    ).select_related('project__workspace', 'created_by').order_by('due_date')[:10]

    # Get upcoming tasks (next 7 days, optimized with select_related)
    upcoming_tasks = all_tasks.filter(
        due_date__gte=datetime.now().date(),
        due_date__lte=datetime.now().date() + timedelta(days=7),
        status__in=['todo', 'in_progress']
    ).select_related('project__workspace', 'created_by').order_by('due_date')[:10]

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
@cache_page(60 * 5)  # Cache for 5 minutes
def pm_dashboard(request):
    """
    Project Manager dashboard - projects they manage, sprint progress, upcoming tasks.
    Shows data from workspaces where user is PM or Admin.
    """
    # Get workspaces where user is PM or Admin (optimized with select_related)
    pm_workspaces = Workspace.objects.filter(
        members__user=request.user,
        members__role__in=['pm', 'admin']
    ).select_related('creator').distinct()

    # Get projects in these workspaces (optimized with prefetch)
    managed_projects = Project.objects.filter(
        workspace__in=pm_workspaces
    ).select_related('workspace').prefetch_related('tasks', 'sprints').annotate(
        task_count=Count('tasks', distinct=True),
        sprint_count=Count('sprints', distinct=True)
    ).order_by('-created_at')

    # Get all tasks in managed projects (optimized with select_related)
    all_tasks = Task.objects.filter(
        project__in=managed_projects
    ).select_related('project__workspace', 'sprint', 'created_by').prefetch_related('assigned_to')

    # Get active sprints (optimized with prefetch to avoid N+1)
    from projects.models import Sprint
    active_sprints = Sprint.objects.filter(
        project__in=managed_projects,
        status='active'
    ).select_related('project').prefetch_related(
        Prefetch('tasks', queryset=Task.objects.select_related('project'))
    ).order_by('end_date')

    # Calculate sprint progress for each active sprint (optimized - no N+1 queries)
    sprint_data = []
    for sprint in active_sprints:
        # Tasks are prefetched, no additional query
        sprint_tasks = sprint.tasks.all()
        total = len([t for t in sprint_tasks])
        completed = len([t for t in sprint_tasks if t.status == 'done'])
        progress = int((completed / total) * 100) if total > 0 else 0
        sprint_data.append({
            'sprint': sprint,
            'total_tasks': total,
            'completed_tasks': completed,
            'progress': progress,
        })

    # Statistics (optimized with aggregate)
    total_projects = managed_projects.count()

    task_stats = all_tasks.aggregate(
        total=Count('id'),
        completed=Count('id', filter=Q(status='done')),
        in_progress=Count('id', filter=Q(status='in_progress'))
    )

    total_tasks = task_stats['total']
    completed_tasks = task_stats['completed']
    in_progress_tasks = task_stats['in_progress']

    # Get overdue tasks (already optimized with select_related above)
    overdue_tasks = all_tasks.filter(
        due_date__lt=datetime.now().date(),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:10]

    # Get upcoming tasks (next 7 days, already optimized)
    upcoming_tasks = all_tasks.filter(
        due_date__gte=datetime.now().date(),
        due_date__lte=datetime.now().date() + timedelta(days=7),
        status__in=['todo', 'in_progress']
    ).order_by('due_date')[:10]

    # Recent activity (already optimized)
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
@cache_page(60 * 5)  # Cache for 5 minutes
def member_dashboard(request):
    """
    Member dashboard - tasks assigned to them, completion percentage, due dates.
    Shows only tasks assigned to the user.
    """
    # Get workspaces where user is a member
    user_workspaces = Workspace.objects.filter(
        members__user=request.user
    ).distinct()

    # Get tasks assigned to the user (optimized with select_related)
    assigned_tasks = Task.objects.filter(
        assigned_to=request.user
    ).select_related('project__workspace', 'sprint', 'created_by').order_by('-created_at')

    # Get subtasks assigned to the user (optimized with select_related)
    from tasks.models import Subtask
    assigned_subtasks = Subtask.objects.filter(
        assigned_to=request.user
    ).select_related('task__project__workspace', 'created_by')

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
