from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['username', 'email', 'name', 'date_joined']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Information'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('date_joined', 'last_login')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Application)
admin.site.register(models.Software)
admin.site.register(models.Project)
