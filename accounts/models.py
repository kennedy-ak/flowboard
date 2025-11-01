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


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds phone number for SMS notifications and organization membership.
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number for SMS notifications")
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='members', help_text="User's organization")

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'