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


class WorkspaceFile(models.Model):
    """
    Files and links associated with a workspace.
    Admins can upload files or add links to external resources.
    """
    FILE_TYPE_CHOICES = [
        ('upload', 'Uploaded File'),
        ('link', 'External Link'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255, help_text="File or link name")
    description = models.TextField(blank=True, help_text="Optional description")
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES, default='upload')

    # For uploaded files
    file = models.FileField(upload_to='workspace_files/%Y/%m/%d/', blank=True, null=True, help_text="Upload a file")

    # For external links
    external_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to external file (Google Drive, Dropbox, etc.)")

    # Metadata
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_files')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(blank=True, null=True, help_text="File size in bytes")

    def __str__(self):
        return f"{self.name} - {self.workspace.name}"

    @property
    def file_size_display(self):
        """Return human-readable file size."""
        if not self.file_size:
            return "N/A"

        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    @property
    def file_extension(self):
        """Get file extension."""
        if self.file_type == 'upload' and self.file:
            return self.file.name.split('.')[-1].upper()
        return None

    def save(self, *args, **kwargs):
        # Auto-calculate file size for uploaded files
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'workspace_files'
        ordering = ['-uploaded_at']