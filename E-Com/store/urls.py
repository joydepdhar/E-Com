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

    # Order
    path('orders/', views.order_list, name='order-list'),
    path('orders/create/', views.create_order, name='create-order'),

    # Shipping Address
    path('orders/<int:order_id>/shipping/', views.add_shipping_address, name='add-shipping-address'),

    # Payment
    path('orders/<int:order_id>/payment/', views.make_payment, name='make-payment'),

    # Reviews
    path('products/<int:product_id>/reviews/', views.review_list_create, name='product-review'),
]
