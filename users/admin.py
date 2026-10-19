from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "base_currency", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (("Finance", {"fields": ("base_currency",)}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "base_currency",
                    "usable_password",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
