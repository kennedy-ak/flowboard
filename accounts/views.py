from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .forms import UserRegistrationForm, UserLoginForm, CustomPasswordResetForm


def register_view(request):
    """
    User registration view.
    Handles invitation tokens and organization creation/joining.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Check if there's an invitation token in the session
    invitation_token = request.session.get('invitation_token')
    invitation = None

    if invitation_token:
        from workspaces.models import WorkspaceInvitation
        try:
            invitation = WorkspaceInvitation.objects.get(token=invitation_token)
            if not invitation.is_valid():
                messages.warning(request, 'The invitation link has expired.')
                del request.session['invitation_token']
                invitation = None
        except WorkspaceInvitation.DoesNotExist:
            del request.session['invitation_token']

    if request.method == 'POST':
        from .forms import OrganizationCreateForm, OrganizationJoinForm
        from .models import Organization

        form = UserRegistrationForm(request.POST)
        org_type = request.POST.get('organization_type')
        org_create_form = OrganizationCreateForm(request.POST) if org_type == 'create' else OrganizationCreateForm()
        org_join_form = OrganizationJoinForm(request.POST) if org_type == 'join' else OrganizationJoinForm()

        # Validate based on organization type
        org_valid = True
        organization = None

        if org_type == 'create':
            org_valid = org_create_form.is_valid()
        elif org_type == 'join':
            org_valid = org_join_form.is_valid()
            if org_valid:
                organization = org_join_form.cleaned_data.get('organization')

        if form.is_valid() and org_valid:
            from .models import UserOrganizationMembership

            user = form.save(commit=False)
            user.save()  # Save user first before creating organization

            # Handle organization
            if org_type == 'create':
                # Create new organization
                organization = org_create_form.save(commit=False)
                organization.created_by = user  # Now user is saved and has a primary key
                organization.save()

                # Create membership with 'owner' role
                UserOrganizationMembership.objects.create(
                    user=user,
                    organization=organization,
                    role='owner'
                )

                # Set as current organization
                user.current_organization = organization
                user.organization = organization  # Keep for backward compatibility
                user.save()
            elif org_type == 'join':
                # Join existing organization
                UserOrganizationMembership.objects.create(
                    user=user,
                    organization=organization,
                    role='member'
                )

                # Set as current organization
                user.current_organization = organization
                user.organization = organization  # Keep for backward compatibility
                user.save()

            login(request, user)

            # If there's a valid invitation, accept it
            if invitation:
                invitation.accept(user)
                del request.session['invitation_token']
                messages.success(request, f'Registration successful! You have been added to {invitation.workspace.name}.')
                return redirect('workspaces:detail', pk=invitation.workspace.pk)
            else:
                if org_type == 'create':
                    messages.success(request, f'Registration successful! Your organization code is: {organization.code}. Share this code with your team members.')
                elif org_type == 'join':
                    messages.success(request, f'Registration successful! You have joined {organization.name}.')
                else:
                    messages.success(request, 'Registration successful! Welcome to FlowBoard.')
                return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        from .forms import OrganizationCreateForm, OrganizationJoinForm
        form = UserRegistrationForm()
        org_create_form = OrganizationCreateForm()
        org_join_form = OrganizationJoinForm()

    context = {
        'form': form,
        'org_create_form': org_create_form,
        'org_join_form': org_join_form,
        'invitation': invitation
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """
    User login view.
    Handles invitation tokens if present.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Check for invitation token in session
    invitation_token = request.session.get('invitation_token')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # If there's an invitation token, accept it
                if invitation_token:
                    from workspaces.models import WorkspaceInvitation
                    try:
                        invitation = WorkspaceInvitation.objects.get(token=invitation_token)
                        if invitation.is_valid():
                            invitation.accept(user)
                            del request.session['invitation_token']
                            messages.success(request, f'Welcome back, {username}! You have been added to {invitation.workspace.name}.')
                            return redirect('workspaces:detail', pk=invitation.workspace.pk)
                        else:
                            del request.session['invitation_token']
                    except WorkspaceInvitation.DoesNotExist:
                        del request.session['invitation_token']

                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    User logout view.
    """
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')
    return redirect('home')


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view.
    """
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Password reset done view.
    """
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Password reset confirm view.
    """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Password reset complete view.
    """
    template_name = 'accounts/password_reset_complete.html'


@login_required
def organization_settings(request):
    """
    Organization settings view.
    Shows all organizations the user belongs to and their current active organization.
    """
    # Get all organizations the user belongs to with their roles
    user_memberships = request.user.organization_memberships.select_related('organization').all()

    # Check if user has any organizations
    if not user_memberships.exists():
        messages.warning(request, 'You are not part of any organization.')
        return redirect('dashboard')

    # Get current organization
    current_organization = request.user.current_organization

    # Build organization data with roles
    organizations_data = []
    for membership in user_memberships:
        org = membership.organization
        organizations_data.append({
            'organization': org,
            'role': membership.role,
            'is_current': org == current_organization,
            'members_count': org.user_memberships.count(),
            'is_owner': membership.role == 'owner',
        })

    context = {
        'organizations_data': organizations_data,
        'current_organization': current_organization,
    }

    return render(request, 'accounts/organization_settings.html', context)


@login_required
def join_organization(request):
    """
    View for existing users to join an organization using a code.
    Users can join multiple organizations.
    """
    from .forms import OrganizationJoinForm
    from .models import UserOrganizationMembership

    if request.method == 'POST':
        form = OrganizationJoinForm(request.POST)
        if form.is_valid():
            organization = form.cleaned_data.get('organization')

            # Check if user is already a member
            if request.user.organization_memberships.filter(organization=organization).exists():
                messages.warning(request, f'You are already a member of {organization.name}.')
                return redirect('accounts:organization_settings')

            # Add user to organization with 'member' role
            UserOrganizationMembership.objects.create(
                user=request.user,
                organization=organization,
                role='member'
            )

            # Set as current organization if user has no current org
            if not request.user.current_organization:
                request.user.current_organization = organization
                request.user.save()

            messages.success(request, f'Successfully joined {organization.name}!')
            return redirect('accounts:organization_settings')
    else:
        form = OrganizationJoinForm()

    context = {
        'form': form,
    }

    return render(request, 'accounts/join_organization.html', context)


@login_required
def leave_organization(request, org_id):
    """
    View for users to leave an organization.
    Owners cannot leave their own organization.
    """
    from .models import Organization, UserOrganizationMembership

    if request.method == 'POST':
        try:
            organization = Organization.objects.get(id=org_id)
            membership = UserOrganizationMembership.objects.get(
                user=request.user,
                organization=organization
            )

            # Prevent owner from leaving
            if membership.role == 'owner':
                messages.error(request, 'You cannot leave an organization you own. You can delete it or transfer ownership instead.')
                return redirect('accounts:organization_settings')

            org_name = organization.name

            # Remove membership
            membership.delete()

            # If this was the current organization, switch to another or clear
            if request.user.current_organization == organization:
                # Get another organization the user belongs to
                other_membership = request.user.organization_memberships.first()
                request.user.current_organization = other_membership.organization if other_membership else None
                request.user.save()

            messages.success(request, f'You have left {org_name}.')

        except (Organization.DoesNotExist, UserOrganizationMembership.DoesNotExist):
            messages.error(request, 'Organization not found or you are not a member.')

        return redirect('accounts:organization_settings')

    return redirect('accounts:organization_settings')


@login_required
def organization_members(request, org_id=None):
    """
    View to list all members of an organization.
    Only accessible by organization owners/admins.
    """
    from .models import Organization

    # Get organization (use provided org_id or current organization)
    if org_id:
        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            messages.error(request, 'Organization not found.')
            return redirect('accounts:organization_settings')
    else:
        organization = request.user.current_organization

    # Check if user has an organization
    if not organization:
        messages.warning(request, 'You are not part of any organization.')
        return redirect('dashboard')

    # Check if user is admin or owner in this organization
    if not request.user.is_admin_in_organization(organization):
        messages.error(request, 'Only organization owners and admins can view the members list.')
        return redirect('accounts:organization_settings')

    # Get all members with their roles
    memberships = organization.user_memberships.select_related('user').all().order_by('-joined_at')

    context = {
        'organization': organization,
        'memberships': memberships,
        'total_members': memberships.count(),
    }

    return render(request, 'accounts/organization_members.html', context)


@login_required
def remove_organization_member(request, org_id, user_id):
    """
    View to remove a member from the organization.
    Only accessible by organization owners/admins.
    """
    from .models import Organization, User, UserOrganizationMembership

    try:
        organization = Organization.objects.get(id=org_id)
    except Organization.DoesNotExist:
        messages.error(request, 'Organization not found.')
        return redirect('accounts:organization_settings')

    # Check if user is admin or owner in this organization
    if not request.user.is_admin_in_organization(organization):
        messages.error(request, 'Only organization owners and admins can remove members.')
        return redirect('accounts:organization_settings')

    if request.method == 'POST':
        try:
            member = User.objects.get(id=user_id)
            membership = UserOrganizationMembership.objects.get(
                user=member,
                organization=organization
            )

            # Prevent removing yourself
            if member == request.user:
                messages.error(request, 'You cannot remove yourself from the organization.')
                return redirect('accounts:organization_members', org_id=org_id)

            # Prevent non-owners from removing owners
            if membership.role == 'owner' and request.user.get_role_in_organization(organization) != 'owner':
                messages.error(request, 'You cannot remove an owner from the organization.')
                return redirect('accounts:organization_members', org_id=org_id)

            member_username = member.username
            membership.delete()

            # If the removed member had this as current org, switch them to another
            if member.current_organization == organization:
                other_membership = member.organization_memberships.first()
                member.current_organization = other_membership.organization if other_membership else None
                member.save()

            messages.success(request, f'{member_username} has been removed from the organization.')
        except (User.DoesNotExist, UserOrganizationMembership.DoesNotExist):
            messages.error(request, 'Member not found.')

        return redirect('accounts:organization_members', org_id=org_id)

    return redirect('accounts:organization_members', org_id=org_id)


@login_required
def switch_organization(request, org_id):
    """
    View to switch the user's current active organization.
    """
    from .models import Organization

    if request.method == 'POST':
        try:
            organization = Organization.objects.get(id=org_id)

            # Check if user is a member of this organization
            if not request.user.organization_memberships.filter(organization=organization).exists():
                messages.error(request, 'You are not a member of this organization.')
                return redirect('accounts:organization_settings')

            # Switch current organization
            request.user.current_organization = organization
            request.user.save()

            messages.success(request, f'Switched to {organization.name}.')

        except Organization.DoesNotExist:
            messages.error(request, 'Organization not found.')

        return redirect('accounts:organization_settings')

    return redirect('accounts:organization_settings')
