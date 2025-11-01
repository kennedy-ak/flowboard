from django import forms
from .models import Workspace, WorkspaceMember, WorkspaceInvitation


class WorkspaceForm(forms.ModelForm):
    """Form for creating and editing workspaces."""

    class Meta:
        model = Workspace
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter workspace name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter workspace description (optional)',
                'rows': 4
            }),
        }


class WorkspaceMemberForm(forms.ModelForm):
    """Form for adding members to workspaces."""

    class Meta:
        model = WorkspaceMember
        fields = ['user', 'role']
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class WorkspaceInvitationForm(forms.ModelForm):
    """Form for inviting users to workspaces via email and SMS."""

    class Meta:
        model = WorkspaceInvitation
        fields = ['recipient_name', 'email', 'recipient_phone', 'role']
        widgets = {
            'recipient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'user@example.com'
            }),
            'recipient_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890 (optional)'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'recipient_name': 'Full Name',
            'email': 'Email Address',
            'recipient_phone': 'Phone Number (Optional)',
            'role': 'Role in Workspace'
        }
        help_texts = {
            'recipient_name': 'Enter the full name of the person you want to invite',
            'email': 'Enter the email address for the invitation',
            'recipient_phone': 'Enter phone number to also send SMS notification (optional)',
            'role': 'Select the role they will have in this workspace'
        }
