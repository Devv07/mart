from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)

# Unregister CustomUser if already registered
if admin.site.is_registered(CustomUser):
    admin.site.unregister(CustomUser)
admin.site.register(CustomUser, CustomUserAdmin)