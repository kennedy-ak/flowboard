from django.urls import path
from . import views

app_name = 'workspaces'

urlpatterns = [
    path('', views.workspace_list, name='list'),
    path('create/', views.workspace_create, name='create'),
    path('<int:pk>/', views.workspace_detail, name='detail'),
    path('<int:pk>/edit/', views.workspace_edit, name='edit'),
    path('<int:pk>/delete/', views.workspace_delete, name='delete'),
    path('<int:pk>/members/', views.workspace_members, name='members'),
    path('<int:pk>/members/add/', views.workspace_add_member, name='add_member'),
    path('<int:pk>/members/<int:member_id>/remove/', views.workspace_remove_member, name='remove_member'),
    path('<int:pk>/members/<int:member_id>/change-role/', views.workspace_change_role, name='change_role'),

    # Invitation URLs
    path('<int:pk>/invitations/', views.workspace_invitations_list, name='invitations'),
    path('<int:pk>/invitations/send/', views.workspace_invite_user, name='invite_user'),
    path('<int:pk>/invitations/<int:invitation_id>/revoke/', views.workspace_revoke_invitation, name='revoke_invitation'),
    path('invite/<str:token>/', views.accept_invitation, name='accept_invitation'),

    # File Management URLs
    path('<int:pk>/files/', views.workspace_files_list, name='files'),
    path('<int:pk>/files/upload/', views.workspace_file_upload, name='file_upload'),
    path('<int:pk>/files/add-link/', views.workspace_link_add, name='link_add'),
    path('<int:pk>/files/<int:file_id>/delete/', views.workspace_file_delete, name='file_delete'),
]
