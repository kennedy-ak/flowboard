from django.contrib import admin
from .models import Workspace, WorkspaceMember, WorkspaceInvitation


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'workspace', 'role', 'joined_at']
    search_fields = ['user__username', 'workspace__name']
    list_filter = ['role', 'joined_at']


@admin.register(WorkspaceInvitation)
class WorkspaceInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'workspace', 'role', 'created_by', 'is_used', 'created_at', 'expires_at']
    search_fields = ['email', 'workspace__name']
    list_filter = ['role', 'is_used', 'created_at']
    readonly_fields = ['token', 'created_at', 'used_by', 'used_at']
