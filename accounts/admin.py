from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, UserOrganizationMembership


class UserOrganizationMembershipInline(admin.TabularInline):
    """Inline admin for user organization memberships."""
    model = UserOrganizationMembership
    extra = 0
    fields = ['organization', 'role', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin configuration for Organization model."""
    list_display = ['name', 'code', 'created_by', 'member_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['code', 'created_at', 'updated_at']
    inlines = [UserOrganizationMembershipInline]

    fieldsets = (
        ('Organization Info', {
            'fields': ('name', 'code', 'description')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

    def member_count(self, obj):
        """Display number of members in organization."""
        return obj.user_memberships.count()
    member_count.short_description = 'Members'


@admin.register(UserOrganizationMembership)
class UserOrganizationMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for UserOrganizationMembership model."""
    list_display = ['user', 'organization', 'role', 'joined_at']
    list_filter = ['role', 'joined_at', 'organization']
    search_fields = ['user__username', 'user__email', 'organization__name']
    readonly_fields = ['joined_at']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom User model."""
    list_display = ['username', 'email', 'current_organization', 'org_count', 'phone_number', 'is_staff', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'current_organization']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    inlines = [UserOrganizationMembershipInline]

    fieldsets = UserAdmin.fieldsets + (
        ('Organization Info', {
            'fields': ('current_organization', 'organization')
        }),
        ('Additional Info', {
            'fields': ('phone_number',)
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Organization Info', {
            'fields': ('current_organization', 'organization')
        }),
        ('Additional Info', {
            'fields': ('email', 'phone_number')
        }),
    )

    def org_count(self, obj):
        """Display number of organizations user belongs to."""
        return obj.organization_memberships.count()
    org_count.short_description = 'Orgs'
