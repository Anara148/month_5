from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "first_name", "last_name", "phone_number", "username", "registration_source", "last_login_google", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "registration_source")
    search_fields = ("email", "phone_number", "username", "first_name", "last_name")
    ordering = ("email",)
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone_number", "username", "birthdate")}),
        ("Google OAuth", {"fields": ("registration_source", "last_login_google")}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Important dates", {"fields": ("last_login",)}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "phone_number", "username", "password1", "password2"),
            },
        ),
    )