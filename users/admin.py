from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The default "add user" form has no email field, but our email is required.
    add_fieldsets = (
        (None, {"fields": ("username", "email", "usable_password", "password1", "password2")}),
    )
