from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext as _

from . import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    list_display = (
        'id', 'email', 'username', 'mobile', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_verified'
    )
    search_fields = ('email', 'mobile', 'username',)
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions',)
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
         'fields': ('first_name', 'last_name', 'mobile', 'username')}),
        (
            _('Permissions'),
            {'fields': (
                'is_active', 'is_staff', 'is_admin', 'is_verified', 'is_superuser', 'groups', 'user_permissions'
            )}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','is_active', 'created_at']
    list_display_links = ['id', 'user']
    list_filter = ['created_at', 'updated_at', 'is_active', 'date_of_joining']
    autocomplete_fields = ['user']
    search_fields = ['user__email', ]


@admin.register(models.GenerateToken)
class ResetPasswordTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'ip_address', 'user_agent')