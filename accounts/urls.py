from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Organization Management
    path('organization/', views.organization_settings, name='organization_settings'),
    path('organization/join/', views.join_organization, name='join_organization'),
    path('organization/leave/', views.leave_organization, name='leave_organization'),
    path('organization/members/', views.organization_members, name='organization_members'),
    path('organization/members/remove/<int:user_id>/', views.remove_organization_member, name='remove_organization_member'),

    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
