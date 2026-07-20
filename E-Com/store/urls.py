from django.urls import path
from . import views

urlpatterns = [
    # Category
    path('categories/', views.category_list, name='category-list'),

    # Product
    path('products/', views.product_list_create, name='product-list-create'),
    path('products/<int:pk>/', views.product_detail, name='product-detail'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove-cart-item'),

    # Orders
    path('orders/', views.order_list, name='order-list'),
    path('orders/create/', views.create_order, name='create-order'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),

    # Shipping Address
    path('orders/<int:order_id>/shipping/', views.add_shipping_address, name='add-shipping-address'),

    # Payment
    path('orders/<int:order_id>/payment/', views.make_payment, name='make-payment'),

    # Reviews
    path('products/<int:product_id>/reviews/', views.review_list_create, name='product-review'),

    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff-dashboard'),
    path('customer/dashboard/', views.customer_dashboard, name='customer-dashboard'),
    path('admin/orders/', views.admin_order_list, name='admin-order-list'),
    path('admin/orders/<int:order_id>/', views.admin_update_order, name='admin-update-order'),
    path('admin/customers/', views.admin_customer_list, name='admin-customer-list'),
    
    # Admin Users Management
    path('admin/users/', views.admin_users, name='admin-users'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin-user-detail'),
    
    # Admin Products Management
    path('admin/products/', views.admin_products, name='admin-products'),
    path('admin/products/<int:product_id>/', views.admin_product_detail, name='admin-product-detail'),
    
    # Admin Settings
    path('admin/settings/', views.admin_settings, name='admin-settings'),
]
