from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from .models import Workspace, WorkspaceMember, WorkspaceInvitation, WorkspaceFile
from .forms import WorkspaceForm, WorkspaceMemberForm, WorkspaceInvitationForm, WorkspaceFileUploadForm, WorkspaceLinkForm
from .decorators import workspace_member_required, workspace_admin_required
from accounts.models import User


@login_required
def workspace_list(request):
    """
    List all workspaces where the user is a member.
    """
    workspaces = Workspace.objects.filter(
        members__user=request.user
    ).annotate(
        project_count=Count('projects', distinct=True),
        member_count=Count('members', distinct=True)
    ).distinct().order_by('-created_at')

    context = {
        'workspaces': workspaces
    }
    return render(request, 'workspaces/workspace_list.html', context)


@login_required
def workspace_create(request):
    """
    Create a new workspace. Creator becomes admin automatically.
    """
    if request.method == 'POST':
        form = WorkspaceForm(request.POST)
        if form.is_valid():
            workspace = form.save(commit=False)
            workspace.created_by = request.user
            workspace.save()

            # Add creator as admin
            WorkspaceMember.objects.create(
                workspace=workspace,
                user=request.user,
                role='admin'
            )

            messages.success(request, f'Workspace "{workspace.name}" created successfully!')
            return redirect('workspaces:detail', pk=workspace.pk)
    else:
        form = WorkspaceForm()

    context = {'form': form}
    return render(request, 'workspaces/workspace_form.html', context)


@login_required
@workspace_member_required()
def workspace_detail(request, pk):
    """
    View workspace details with projects and recent activity.
    """
    workspace = request.workspace
    membership = request.workspace_membership

    # Get workspace statistics
    projects = workspace.projects.all()[:5]
    members = workspace.members.select_related('user').all()

    context = {
        'workspace': workspace,
        'membership': membership,
        'projects': projects,
        'members': members,
        'is_admin': membership.role == 'admin',
        'is_pm': membership.role in ['admin', 'pm'],
    }
    return render(request, 'workspaces/workspace_detail.html', context)


@login_required
@workspace_admin_required
def workspace_edit(request, pk):
    """
    Edit workspace details. Only admins can edit.
    """
    workspace = request.workspace

    if request.method == 'POST':
        form = WorkspaceForm(request.POST, instance=workspace)
        if form.is_valid():
            form.save()
            messages.success(request, f'Workspace "{workspace.name}" updated successfully!')
            return redirect('workspaces:detail', pk=pk)
    else:
        form = WorkspaceForm(instance=workspace)

    context = {
        'form': form,
        'workspace': workspace,
        'is_edit': True
    }
    return render(request, 'workspaces/workspace_form.html', context)


@login_required
@workspace_admin_required
def workspace_delete(request, pk):
    """
    Delete workspace. Only workspace admins AND organization admins/owners can delete.
    """
    workspace = request.workspace

    # Additional check: Only organization admins or owners can delete workspaces
    if request.user.current_organization:
        if not request.user.is_admin_in_organization(request.user.current_organization):
            messages.error(request, 'Only organization admins and owners can delete workspaces.')
            return redirect('workspaces:detail', pk=pk)
    else:
        messages.error(request, 'You must be part of an organization to delete workspaces.')
        return redirect('workspaces:detail', pk=pk)

    if request.method == 'POST':
        workspace_name = workspace.name
        workspace.delete()
        messages.success(request, f'Workspace "{workspace_name}" deleted successfully!')
        return redirect('workspaces:list')

    context = {'workspace': workspace}
    return render(request, 'workspaces/workspace_confirm_delete.html', context)


@login_required
@workspace_member_required()
def workspace_members(request, pk):
    """
    View all workspace members.
    """
    workspace = request.workspace
    membership = request.workspace_membership

    members = workspace.members.select_related('user').all().order_by('role', 'joined_at')

    context = {
        'workspace': workspace,
        'membership': membership,
        'members': members,
        'is_admin': membership.role == 'admin',
    }
    return render(request, 'workspaces/workspace_members.html', context)


@login_required
@workspace_admin_required
def workspace_add_member(request, pk):
    """
    Add a new member to the workspace. Only admins can add members.
    """
    workspace = request.workspace

    if request.method == 'POST':
        form = WorkspaceMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.workspace = workspace

            # Check if user is already a member
            if WorkspaceMember.objects.filter(workspace=workspace, user=member.user).exists():
                messages.error(request, f'{member.user.username} is already a member of this workspace.')
            else:
                member.save()
                messages.success(request, f'{member.user.username} added to workspace successfully!')
                return redirect('workspaces:members', pk=pk)
    else:
        form = WorkspaceMemberForm()

    # Get users who are not already members AND from the same organization
    existing_member_ids = workspace.members.values_list('user_id', flat=True)

    # Filter users: must be from same organization as the requesting user's current organization
    if request.user.current_organization:
        # Show only users from the same organization (using the new many-to-many relationship)
        available_users = User.objects.filter(
            organizations=request.user.current_organization
        ).exclude(id__in=existing_member_ids)
    else:
        # If user has no current organization, they can't add anyone
        available_users = User.objects.none()

    form.fields['user'].queryset = available_users

    # Add warning message if no users are available
    if not available_users.exists():
        if not request.user.current_organization:
            messages.info(request, 'You must join an organization and set it as your current organization before you can add members to workspaces.')
        else:
            messages.info(request, f'No users from your current organization ({request.user.current_organization.name}) are available to add. Share your organization code to invite more members.')

    context = {
        'form': form,
        'workspace': workspace
    }
    return render(request, 'workspaces/workspace_add_member.html', context)


@login_required
@workspace_admin_required
def workspace_remove_member(request, pk, member_id):
    """
    Remove a member from the workspace. Only workspace admins AND organization admins/owners can remove members.
    Cannot remove yourself if you're the last admin.
    """
    workspace = request.workspace
    member = get_object_or_404(WorkspaceMember, pk=member_id, workspace=workspace)

    # Additional check: Only organization admins or owners can remove members
    if request.user.current_organization:
        if not request.user.is_admin_in_organization(request.user.current_organization):
            messages.error(request, 'Only organization admins and owners can remove workspace members.')
            return redirect('workspaces:members', pk=pk)

    # Prevent removing the last admin
    if member.role == 'admin':
        admin_count = WorkspaceMember.objects.filter(workspace=workspace, role='admin').count()
        if admin_count == 1:
            messages.error(request, 'Cannot remove the last admin from the workspace.')
            return redirect('workspaces:members', pk=pk)

    if request.method == 'POST':
        username = member.user.username
        member.delete()
        messages.success(request, f'{username} removed from workspace successfully!')
        return redirect('workspaces:members', pk=pk)

    context = {
        'workspace': workspace,
        'member': member
    }
    return render(request, 'workspaces/workspace_remove_member.html', context)


@login_required
@workspace_admin_required
def workspace_change_role(request, pk, member_id):
    """
    Change a member's role. Only admins can change roles.
    Cannot demote the last admin.
    """
    workspace = request.workspace
    member = get_object_or_404(WorkspaceMember, pk=member_id, workspace=workspace)

    if request.method == 'POST':
        new_role = request.POST.get('role')

        # Prevent demoting the last admin
        if member.role == 'admin' and new_role != 'admin':
            admin_count = WorkspaceMember.objects.filter(workspace=workspace, role='admin').count()
            if admin_count == 1:
                messages.error(request, 'Cannot demote the last admin.')
                return redirect('workspaces:members', pk=pk)

        member.role = new_role
        member.save()
        messages.success(request, f'{member.user.username} role updated to {member.get_role_display()}!')
        return redirect('workspaces:members', pk=pk)

    context = {
        'workspace': workspace,
        'member': member
    }
    return render(request, 'workspaces/workspace_change_role.html', context)


# Invitation Views

@login_required
@workspace_admin_required
def workspace_invite_user(request, pk):
    """
    Send an invitation to join the workspace.
    Only admins can send invitations.
    """
    workspace = request.workspace

    if request.method == 'POST':
        form = WorkspaceInvitationForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.workspace = workspace
            invitation.created_by = request.user

            # Check if user with this email already exists in workspace
            existing_member = WorkspaceMember.objects.filter(
                workspace=workspace,
                user__email=invitation.email
            ).first()

            if existing_member:
                messages.error(request, f'A user with email {invitation.email} is already a member of this workspace.')
                return redirect('workspaces:invitations', pk=pk)

            # Check if there's already a pending invitation for this email
            existing_invitation = WorkspaceInvitation.objects.filter(
                workspace=workspace,
                email=invitation.email,
                is_used=False
            ).first()

            if existing_invitation and existing_invitation.is_valid():
                messages.warning(request, f'There is already a pending invitation for {invitation.email}.')
                return redirect('workspaces:invitations', pk=pk)

            invitation.save()

            # Queue background tasks for invitation email and SMS
            from .tasks import send_invitation_email_async, send_invitation_sms_async
            send_invitation_email_async(invitation.id)
            send_invitation_sms_async(invitation.id)

            # Success message based on whether phone was provided
            if invitation.recipient_phone:
                messages.success(request, f'Invitation sent to {invitation.recipient_name} via email ({invitation.email}) and SMS ({invitation.recipient_phone})!')
            else:
                messages.success(request, f'Invitation sent to {invitation.recipient_name} via email ({invitation.email})!')
            return redirect('workspaces:invitations', pk=pk)
    else:
        form = WorkspaceInvitationForm()

    context = {
        'form': form,
        'workspace': workspace
    }
    return render(request, 'workspaces/workspace_invite.html', context)


@login_required
@workspace_admin_required
def workspace_invitations_list(request, pk):
    """
    List all invitations for the workspace.
    Only admins can view invitations.
    """
    workspace = request.workspace

    # Get all invitations for this workspace
    invitations = workspace.invitations.all().order_by('-created_at')

    # Separate pending and used invitations
    pending_invitations = [inv for inv in invitations if inv.is_valid()]
    expired_invitations = [inv for inv in invitations if not inv.is_used and not inv.is_valid()]
    used_invitations = [inv for inv in invitations if inv.is_used]

    context = {
        'workspace': workspace,
        'pending_invitations': pending_invitations,
        'expired_invitations': expired_invitations,
        'used_invitations': used_invitations,
    }
    return render(request, 'workspaces/workspace_invitations.html', context)


@login_required
@workspace_admin_required
def workspace_revoke_invitation(request, pk, invitation_id):
    """
    Revoke/delete an invitation.
    Only admins can revoke invitations.
    """
    workspace = request.workspace
    invitation = get_object_or_404(WorkspaceInvitation, pk=invitation_id, workspace=workspace)

    if request.method == 'POST':
        email = invitation.email
        invitation.delete()
        messages.success(request, f'Invitation to {email} has been revoked.')
        return redirect('workspaces:invitations', pk=pk)

    context = {
        'workspace': workspace,
        'invitation': invitation
    }
    return render(request, 'workspaces/workspace_revoke_invitation.html', context)


def accept_invitation(request, token):
    """
    Accept a workspace invitation.
    Can be accessed by both authenticated and unauthenticated users.
    """
    invitation = get_object_or_404(WorkspaceInvitation, token=token)

    # Check if invitation is valid
    if not invitation.is_valid():
        if invitation.is_used:
            messages.error(request, 'This invitation has already been used.')
        else:
            messages.error(request, 'This invitation has expired.')
        return redirect('accounts:login')

    # If user is authenticated
    if request.user.is_authenticated:
        # Accept the invitation
        invitation.accept(request.user)
        messages.success(request, f'Welcome to {invitation.workspace.name}!')
        return redirect('workspaces:detail', pk=invitation.workspace.pk)
    else:
        # Store invitation token in session and redirect to registration
        request.session['invitation_token'] = token
        messages.info(request, f'Please register or login to accept the invitation to {invitation.workspace.name}.')
        return redirect('accounts:register')


# File Management Views

@login_required
@workspace_member_required()
def workspace_files_list(request, pk):
    """
    List all files and links in a workspace.
    All members can view files.
    """
    workspace = request.workspace
    membership = request.workspace_membership

    files = WorkspaceFile.objects.filter(workspace=workspace).select_related('uploaded_by')

    context = {
        'workspace': workspace,
        'membership': membership,
        'files': files,
        'is_admin': membership.role == 'admin',
    }
    return render(request, 'workspaces/workspace_files.html', context)


@login_required
@workspace_admin_required
def workspace_file_upload(request, pk):
    """
    Upload a file to the workspace.
    Only admins can upload files.
    """
    workspace = request.workspace

    if request.method == 'POST':
        form = WorkspaceFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            workspace_file = form.save(commit=False)
            workspace_file.workspace = workspace
            workspace_file.uploaded_by = request.user
            workspace_file.file_type = 'upload'
            workspace_file.save()
            messages.success(request, f'File "{workspace_file.name}" uploaded successfully!')
            return redirect('workspaces:files', pk=pk)
    else:
        form = WorkspaceFileUploadForm()

    context = {
        'form': form,
        'workspace': workspace,
        'action': 'Upload File'
    }
    return render(request, 'workspaces/workspace_file_form.html', context)


@login_required
@workspace_admin_required
def workspace_link_add(request, pk):
    """
    Add an external link to the workspace.
    Only admins can add links.
    """
    workspace = request.workspace

    if request.method == 'POST':
        form = WorkspaceLinkForm(request.POST)
        if form.is_valid():
            workspace_link = form.save(commit=False)
            workspace_link.workspace = workspace
            workspace_link.uploaded_by = request.user
            workspace_link.file_type = 'link'
            workspace_link.save()
            messages.success(request, f'Link "{workspace_link.name}" added successfully!')
            return redirect('workspaces:files', pk=pk)
    else:
        form = WorkspaceLinkForm()

    context = {
        'form': form,
        'workspace': workspace,
        'action': 'Add External Link'
    }
    return render(request, 'workspaces/workspace_link_form.html', context)


@login_required
@workspace_admin_required
def workspace_file_delete(request, pk, file_id):
    """
    Delete a file or link from the workspace.
    Only admins can delete files.
    """
    workspace = request.workspace
    workspace_file = get_object_or_404(WorkspaceFile, pk=file_id, workspace=workspace)

    if request.method == 'POST':
        file_name = workspace_file.name
        # Delete the actual file if it's an upload
        if workspace_file.file_type == 'upload' and workspace_file.file:
            workspace_file.file.delete()
        workspace_file.delete()
        messages.success(request, f'"{file_name}" deleted successfully!')
        return redirect('workspaces:files', pk=pk)

    context = {
        'workspace': workspace,
        'file': workspace_file
    }
    return render(request, 'workspaces/workspace_file_confirm_delete.html', context)
