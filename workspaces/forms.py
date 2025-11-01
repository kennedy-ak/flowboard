from django import forms
from .models import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceFile


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


class WorkspaceFileUploadForm(forms.ModelForm):
    """Form for uploading files to workspace."""

    class Meta:
        model = WorkspaceFile
        fields = ['name', 'description', 'file']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter file name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter file description (optional)',
                'rows': 3
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'File Name',
            'description': 'Description (Optional)',
            'file': 'Choose File'
        }
        help_texts = {
            'name': 'Give your file a descriptive name',
            'file': 'Maximum file size: 100MB'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True


class WorkspaceLinkForm(forms.ModelForm):
    """Form for adding external links to workspace."""

    class Meta:
        model = WorkspaceFile
        fields = ['name', 'description', 'external_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter link name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter link description (optional)',
                'rows': 3
            }),
            'external_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://drive.google.com/...'
            }),
        }
        labels = {
            'name': 'Link Name',
            'description': 'Description (Optional)',
            'external_url': 'External Link URL'
        }
        help_texts = {
            'name': 'Give your link a descriptive name',
            'external_url': 'URL to external file (Google Drive, Dropbox, OneDrive, etc.)'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['external_url'].required = True
