from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets


class Workspace(models.Model):
    """
    Workspace model - top level of hierarchy.
    Users can belong to multiple workspaces with different roles.
    """
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_workspaces')
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'workspaces'
        ordering = ['-created_at']


class WorkspaceMember(models.Model):
    """
    Many-to-many relationship between User and Workspace with role information.
    Roles are workspace-specific.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('pm', 'Project Manager'),
        ('member', 'Member'),
    ]
    
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.workspace.name} ({self.role})"
    
    class Meta:
        db_table = 'workspace_members'
        unique_together = ['workspace', 'user']
        ordering = ['workspace', 'role']


class WorkspaceInvitation(models.Model):
    """
    Invitation model for inviting users to join a workspace.
    Each invitation has a unique token and can be used once.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('pm', 'Project Manager'),
        ('member', 'Member'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='invitations')
    recipient_name = models.CharField(max_length=200, default='Guest', help_text="Full name of the person being invited")
    email = models.EmailField(help_text="Email address to send invitation to")
    recipient_phone = models.CharField(max_length=20, blank=True, default='', help_text="Phone number for SMS notification (optional)")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    token = models.CharField(max_length=64, unique=True, editable=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_invitations')
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Generate unique token and set expiration if not set."""
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        if not self.expires_at:
            # Invitations expire in 7 days
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if invitation is still valid (not used and not expired)."""
        return not self.is_used and timezone.now() < self.expires_at

    def accept(self, user):
        """Mark invitation as used by a user."""
        self.is_used = True
        self.used_by = user
        self.used_at = timezone.now()
        self.save()

        # Add user to workspace
        WorkspaceMember.objects.get_or_create(
            workspace=self.workspace,
            user=user,
            defaults={'role': self.role}
        )

    def __str__(self):
        return f"Invitation to {self.recipient_name} ({self.email}) for {self.workspace.name} ({self.get_role_display()})"

    class Meta:
        db_table = 'workspace_invitations'
        ordering = ['-created_at']