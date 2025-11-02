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
            user = form.save(commit=False)

            # Handle organization
            if org_type == 'create':
                # Create new organization
                organization = org_create_form.save(commit=False)
                organization.created_by = user
                organization.save()
                user.organization = organization
            elif org_type == 'join':
                # Join existing organization
                user.organization = organization

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
