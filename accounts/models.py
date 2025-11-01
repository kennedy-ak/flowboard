from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds phone number for SMS notifications.
    """
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Phone number for SMS notifications")
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'