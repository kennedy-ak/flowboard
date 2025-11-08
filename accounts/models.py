from django.contrib.auth.models import AbstractUser
from django.db import models
import secrets
import string


class Organization(models.Model):
    """
    Organization model for grouping users.
    Users can only add members from their own organization to workspaces.
    """
    name = models.CharField(max_length=200, help_text="Organization name")
    code = models.CharField(max_length=20, unique=True, help_text="Unique organization code for inviting members")
    description = models.TextField(blank=True, null=True, help_text="Organization description")
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @staticmethod
    def generate_unique_code():
        """Generate a unique organization code like ORG-ABC123"""
        while True:
            # Generate random code: ORG-XXXXXX (6 characters: letters and numbers)
            code = 'ORG-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not Organization.objects.filter(code=code).exists():
                return code

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['-created_at']


class UserOrganizationMembership(models.Model):
    """
    Junction table for User-Organization many-to-many relationship.
    Allows users to belong to multiple organizations with different roles.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='organization_memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='user_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', help_text="User's role in this organization")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_organization_memberships'
        unique_together = ['user', 'organization']
        verbose_name = 'User Organization Membership'
        verbose_name_plural = 'User Organization Memberships'
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds phone number for SMS notifications and organization membership.
    Users can now belong to multiple organizations.
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number for SMS notifications")
    email = models.EmailField(unique=True)

    # New: Many-to-many relationship with organizations
    organizations = models.ManyToManyField(
        Organization,
        through='UserOrganizationMembership',
        related_name='all_members',
        help_text="Organizations this user belongs to"
    )

    # New: Current active organization for UI context
    current_organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_members',
        help_text="User's currently active organization"
    )

    # Old field: Keep for backward compatibility during migration, will be deprecated
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="[DEPRECATED] Use current_organization instead"
    )

    def __str__(self):
        return self.username

    def get_role_in_organization(self, organization):
        """Get user's role in a specific organization."""
        try:
            membership = self.organization_memberships.get(organization=organization)
            return membership.role
        except UserOrganizationMembership.DoesNotExist:
            return None

    def is_admin_in_organization(self, organization):
        """Check if user is admin or owner in a specific organization."""
        role = self.get_role_in_organization(organization)
        return role in ['admin', 'owner']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'