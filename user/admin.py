from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _


User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password',
            ),
        }),
        (_('Personal info'), {
            'classes': ('collapse',),
            'fields': (
                'first_name',
                'last_name',
                'email',
            ),
        }),
        (_('Permissions'), {
            'classes': ('collapse',),
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important datas'), {
            'classes': ('collapse',),
            'fields': (
                'last_login',
                'date_joined',
            ),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
            ),
        }),
    )
    