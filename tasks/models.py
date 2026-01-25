from django.db import models
from django.conf import settings
from projects.models import Project, Sprint


class Task(models.Model):
    """
    Task model - belongs to a project and optionally to a sprint.
    Can be assigned to multiple members.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', db_index=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_tasks', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def progress_percentage(self):
        """Calculate progress based on completed subtasks."""
        total_subtasks = self.subtasks.count()
        if total_subtasks == 0:
            return 0
        completed_subtasks = self.subtasks.filter(status='done').count()
        return int((completed_subtasks / total_subtasks) * 100)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']


class Subtask(models.Model):
    """
    Subtask model - belongs to a task.
    Can be assigned to multiple members.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', db_index=True)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_subtasks', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_subtasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.task.title} - {self.title}"
    
    class Meta:
        db_table = 'subtasks'
        ordering = ['created_at']


class Comment(models.Model):
    """
    Comment model - can be attached to tasks or subtasks.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    subtask = models.ForeignKey(Subtask, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} at {self.created_at}"
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']