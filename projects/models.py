from django.db import models
from django.conf import settings
from workspaces.models import Workspace


class Project(models.Model):
    """
    Project model - belongs to a workspace.
    """
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_projects')
    
    def __str__(self):
        return f"{self.workspace.name} - {self.name}"
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']


class Sprint(models.Model):
    """
    Sprint model - belongs to a project.
    Each project can have multiple sprints.
    """
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sprints')
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.project.name} - {self.name}"
    
    class Meta:
        db_table = 'sprints'
        ordering = ['start_date']