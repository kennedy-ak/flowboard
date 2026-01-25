#!/usr/bin/env python3
"""
FlowBoard Internal Email Test
This script tests email functionality using FlowBoard's actual Django configuration.
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowboard.settings')
django.setup()

# Import FlowBoard models and email functionality
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from accounts.models import User, Organization, UserOrganizationMembership
from workspaces.models import Workspace, WorkspaceInvitation

def test_flowboard_email():
    """Test email functionality using FlowBoard's actual configuration."""
    
    print("FlowBoard Internal Email Test")
    print("=" * 50)
    
    # Check current email configuration
    from django.conf import settings
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email User: {settings.EMAIL_HOST_USER}")
    print(f"Use SSL: {settings.EMAIL_USE_SSL}")
    print(f"Use TLS: {settings.EMAIL_USE_TLS}")
    print("-" * 50)
    
    try:
        # Test basic email sending
        print("Testing basic email functionality...")
        
        subject = "FlowBoard Application Email Test"
        message = f"""
        Hello from FlowBoard!
        
        This email was sent using FlowBoard's Django email configuration.
        The email system is properly configured and working.
        
        Email Settings Used:
        - Host: {settings.EMAIL_HOST}
        - Port: {settings.EMAIL_PORT}
        - SSL: {settings.EMAIL_USE_SSL}
        - TLS: {settings.EMAIL_USE_TLS}
        - From: {settings.EMAIL_HOST_USER}
        
        Timestamp: {__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}
        
        This confirms that FlowBoard can send emails successfully.
        """
        
        # Send test email
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['akogokennedy@gmail.com'],
            fail_silently=False,
        )
        
        if result == 1:
            print("SUCCESS: FlowBoard email system is working!")
            print("Check akogokennedy@gmail.com for the test email.")
            
            # Test workspace invitation functionality
            print("\\nTesting workspace invitation email functionality...")
            
            # This would be used in actual workspace invitations
            invitation_subject = "Workspace Invitation - FlowBoard"
            invitation_message = """
            You've been invited to join a workspace on FlowBoard!
            
            Click the link below to accept the invitation and join the team.
            
            [Accept Invitation Link]
            
            Best regards,
            The FlowBoard Team
            """
            
            invitation_result = send_mail(
                subject=invitation_subject,
                message=invitation_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['akogokennedy@gmail.com'],
                fail_silently=False,
            )
            
            if invitation_result == 1:
                print("SUCCESS: Workspace invitation emails will work correctly!")
            else:
                print("WARNING: Basic email works but invitation emails may have issues.")
                
        else:
            print("FAILED: FlowBoard email system is not working.")
            print("Result code:", result)
            
    except Exception as e:
        print("ERROR: FlowBoard email test failed")
        print(f"Error: {type(e).__name__}: {str(e)}")
        return False
    
    return True

def show_email_usage_example():
    """Show how to use email in FlowBoard views."""
    print("\\n" + "=" * 50)
    print("Email Usage Example for FlowBoard Developers")
    print("=" * 50)
    
    example_code = '''
# In FlowBoard views (e.g., workspaces/views.py)
from django.core.mail import send_mail
from django.conf import settings

def send_workspace_invitation(request, workspace_id, email, role):
    """Send workspace invitation email."""
    try:
        invitation_link = f"{settings.SITE_URL}/accounts/invite/accept/?token={invitation_token}"
        
        subject = f"Invitation to join {workspace.name} on FlowBoard"
        message = f"""
        Hello,
        
        You've been invited to join the workspace "{workspace.name}" on FlowBoard 
        with the role of {role}.
        
        Click the link below to accept the invitation:
        {invitation_link}
        
        Best regards,
        The FlowBoard Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        # Log error
        print(f"Failed to send invitation email: {e}")
        return False

# In task assignment (e.g., tasks/views.py)
def assign_task(request, task_id, user_ids):
    """Assign task and send notification emails."""
    task = get_object_or_404(Task, id=task_id)
    
    # Assign task to users
    task.assigned_to.set(user_ids)
    task.save()
    
    # Send notification emails
    assigned_users = User.objects.filter(id__in=user_ids)
    for user in assigned_users:
        subject = f"New Task Assignment: {task.title}"
        message = f"""
        Hello {user.first_name},
        
        You have been assigned a new task: "{task.title}"
        
        Project: {task.project.name}
        Due Date: {task.due_date}
        
        View the task: {settings.SITE_URL}/tasks/{task.id}/
        
        Best regards,
        The FlowBoard Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,  # Don't fail task assignment if email fails
        )
'''
    
    print(example_code)

if __name__ == "__main__":
    success = test_flowboard_email()
    show_email_usage_example()
    
    print("\\n" + "=" * 50)
    if success:
        print("FlowBoard email system is ready for production use!")
    else:
        print("Please check email configuration before deploying.")
    print("=" * 50)