"""
Main project views.
"""
from django.shortcuts import render, redirect


def home(request):
    """
    Home page view - landing page for unauthenticated users.
    Redirects to dashboard if user is already logged in.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'home.html')
