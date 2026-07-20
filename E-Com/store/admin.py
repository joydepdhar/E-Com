import logging

from django.contrib import admin
from .audit import create_audit_log
from .models import (
    AuditLog, Category, Product, Cart, CartItem, Order, OrderItem,
    ShippingAddress, Payment, Review,
)


store_logger = logging.getLogger('store')
order_logger = logging.getLogger('store.orders')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = 'product_updated' if change else 'product_created'
        store_logger.info(
            'admin_product_%s actor_id=%s product_id=%s',
            'updated' if change else 'created',
            request.user.id,
            obj.id,
        )
        create_audit_log(
            request,
            action=action,
            object_type='Product',
            object_id=obj.id,
        )

    def delete_model(self, request, obj):
        product_id = obj.id
        super().delete_model(request, obj)
        store_logger.info(
            'admin_product_deleted actor_id=%s product_id=%s',
            request.user.id,
            product_id,
        )
        create_audit_log(
            request,
            action='product_deleted',
            object_type='Product',
            object_id=product_id,
        )

    def delete_queryset(self, request, queryset):
        product_ids = list(queryset.values_list('id', flat=True))
        super().delete_queryset(request, queryset)
        for product_id in product_ids:
            store_logger.info(
                'admin_product_deleted actor_id=%s product_id=%s',
                request.user.id,
                product_id,
            )
            create_audit_log(
                request,
                action='product_deleted',
                object_type='Product',
                object_id=product_id,
            )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_status = Order.objects.filter(pk=obj.pk).values_list(
                'status',
                flat=True,
            ).first()

        super().save_model(request, obj, form, change)

        if change and old_status != obj.status:
            order_logger.info(
                'admin_order_status_updated actor_id=%s order_id=%s old_status=%s new_status=%s',
                request.user.id,
                obj.id,
                old_status,
                obj.status,
            )
            create_audit_log(
                request,
                action='order_status_updated',
                object_type='Order',
                object_id=obj.id,
            )
            if obj.status.lower() == 'cancelled':
                order_logger.info(
                    'order_cancelled actor_id=%s order_id=%s',
                    request.user.id,
                    obj.id,
                )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'object_type', 'object_id', 'ip_address')
    list_filter = ('action', 'object_type')
    search_fields = ('action', 'object_type', 'object_id', 'user__username')
    readonly_fields = ('user', 'action', 'object_type', 'object_id', 'timestamp', 'ip_address')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Payment)
admin.site.register(Review)
