from django import forms
from .models import Project, Sprint


class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""

    class Meta:
        model = Project
        fields = ['workspace', 'name', 'description']
        widgets = {
            'workspace': forms.Select(attrs={
                'class': 'form-select'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project description (optional)',
                'rows': 4
            }),
        }


class SprintForm(forms.ModelForm):
    """Form for creating and editing sprints."""

    class Meta:
        model = Sprint
        fields = ['name', 'start_date', 'end_date', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter sprint name (e.g., Sprint 1)'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('End date must be after start date.')

        return cleaned_data
