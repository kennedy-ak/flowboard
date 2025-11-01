from django import forms
from .models import Task, Subtask, Comment


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks."""

    class Meta:
        model = Task
        fields = ['project', 'sprint', 'title', 'description', 'status', 'due_date', 'assigned_to']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'sprint': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter task description', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        }


class SubtaskForm(forms.ModelForm):
    """Form for creating and editing subtasks."""

    class Meta:
        model = Subtask
        fields = ['title', 'description', 'status', 'due_date', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subtask title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter subtask description', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '3'}),
        }


class CommentForm(forms.ModelForm):
    """Form for adding comments."""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write a comment...',
                'rows': 3
            }),
        }
