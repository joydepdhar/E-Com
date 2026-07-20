import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from store.audit import create_audit_log
from .models import CustomUser


store_logger = logging.getLogger('store')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role and profile', {'fields': ('role', 'address', 'phone', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = UserAdmin.list_filter + ('role',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = 'user_updated' if change else 'user_created'
        store_logger.info(
            'admin_user_%s actor_id=%s user_id=%s role=%s is_active=%s',
            'updated' if change else 'created',
            request.user.id,
            obj.id,
            obj.role,
            obj.is_active,
        )
        create_audit_log(
            request,
            action=action,
            object_type='User',
            object_id=obj.id,
        )

    def delete_model(self, request, obj):
        user_id = obj.id
        super().delete_model(request, obj)
        store_logger.info(
            'admin_user_deleted actor_id=%s user_id=%s',
            request.user.id,
            user_id,
        )
        create_audit_log(
            request,
            action='user_deleted',
            object_type='User',
            object_id=user_id,
        )

    def delete_queryset(self, request, queryset):
        user_ids = list(queryset.values_list('id', flat=True))
        super().delete_queryset(request, queryset)
        for user_id in user_ids:
            store_logger.info(
                'admin_user_deleted actor_id=%s user_id=%s',
                request.user.id,
                user_id,
            )
            create_audit_log(
                request,
                action='user_deleted',
                object_type='User',
                object_id=user_id,
            )
