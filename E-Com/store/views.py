from django.db import transaction
from django.db.models import Count, Sum
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from user_app.permissions import IsAdminRole, IsCustomerRole, IsStaffOrAdminRole
from .models import (
    Category, Product, Cart, CartItem,
    Order, OrderItem, ShippingAddress,
    Payment, Review
)
from .serializers import (
    CategorySerializer, ProductSerializer, CartSerializer,
    CartItemSerializer, OrderSerializer, ShippingAddressSerializer,
    PaymentSerializer, ReviewSerializer, AdminOrderSerializer,
    AdminUserSerializer
)

# -------------------- CATEGORY --------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# -------------------- PRODUCT --------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def product_list_create(request):
    if request.method == 'GET':
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        if not getattr(request.user, 'is_staff_role', False):
            return Response({'error': 'Only admin or staff can add products'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not getattr(request.user, 'is_staff_role', False):
            return Response({'error': 'Only admin or staff can update products'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not getattr(request.user, 'is_staff_role', False):
            return Response({'error': 'Only admin or staff can delete products'}, status=status.HTTP_403_FORBIDDEN)
        product.delete()
        return Response({'message': 'Product deleted'}, status=status.HTTP_204_NO_CONTENT)


# -------------------- CART --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    if request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity = quantity
        item.save()
        return Response({'message': 'Item added to cart'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        return Response({'message': 'Item removed'})
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


# -------------------- ORDER --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            order = Order.objects.create(user=request.user)
            total_price = 0

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
                total_price += item.product.price * item.quantity

            order.total_price = total_price
            order.save()

            # Clear cart items after order placement
            cart.items.all().delete()

        return Response({'message': 'Order placed', 'order_id': order.id}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': 'Failed to create order', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# -------------------- SHIPPING ADDRESS --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_shipping_address(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ShippingAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(order=order)
        return Response({'message': 'Shipping address added'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- PAYMENT --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(order=order, is_successful=True)
        order.is_paid = True
        order.save()
        return Response({'message': 'Payment successful'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- REVIEW --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def review_list_create(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------- ADMIN DASHBOARD --------------------
@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_dashboard(request):
    paid_revenue = Order.objects.filter(is_paid=True).aggregate(
        total=Sum('total_price')
    )['total'] or 0

    order_status_counts = {
        item['status']: item['count']
        for item in Order.objects.values('status').annotate(count=Count('id'))
    }

    recent_orders = Order.objects.select_related('user').prefetch_related(
        'order_items__product'
    ).order_by('-created_at')[:5]
    low_stock_products = Product.objects.select_related('category').filter(
        stock__lte=5,
        is_active=True
    ).order_by('stock', 'name')[:10]

    return Response({
        'totals': {
            'revenue': paid_revenue,
            'orders': Order.objects.count(),
            'paid_orders': Order.objects.filter(is_paid=True).count(),
            'pending_orders': Order.objects.filter(status__iexact='Pending').count(),
            'products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'customers': get_user_model().objects.filter(role='customer').count(),
            'reviews': Review.objects.count(),
        },
        'orders_by_status': order_status_counts,
        'recent_orders': AdminOrderSerializer(
            recent_orders,
            many=True,
            context={'request': request}
        ).data,
        'low_stock_products': ProductSerializer(
            low_stock_products,
            many=True,
            context={'request': request}
        ).data,
    })


@api_view(['GET'])
@permission_classes([IsStaffOrAdminRole])
def staff_dashboard(request):
    recent_orders = Order.objects.select_related('user').prefetch_related(
        'order_items__product'
    ).order_by('-created_at')[:10]
    low_stock_products = Product.objects.select_related('category').filter(
        stock__lte=5,
        is_active=True
    ).order_by('stock', 'name')[:10]

    return Response({
        'totals': {
            'orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status__iexact='Pending').count(),
            'paid_orders': Order.objects.filter(is_paid=True).count(),
            'products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'low_stock_products': Product.objects.filter(stock__lte=5, is_active=True).count(),
        },
        'recent_orders': AdminOrderSerializer(
            recent_orders,
            many=True,
            context={'request': request}
        ).data,
        'low_stock_products': ProductSerializer(
            low_stock_products,
            many=True,
            context={'request': request}
        ).data,
    })


@api_view(['GET'])
@permission_classes([IsCustomerRole])
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user)
    recent_orders = orders.prefetch_related(
        'order_items__product'
    ).order_by('-created_at')[:5]
    cart, _ = Cart.objects.get_or_create(user=request.user)

    return Response({
        'totals': {
            'orders': orders.count(),
            'pending_orders': orders.filter(status__iexact='Pending').count(),
            'paid_orders': orders.filter(is_paid=True).count(),
            'cart_items': cart.items.count(),
            'reviews': Review.objects.filter(user=request.user).count(),
        },
        'cart': CartSerializer(cart, context={'request': request}).data,
        'recent_orders': OrderSerializer(
            recent_orders,
            many=True,
            context={'request': request}
        ).data,
    })


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_order_list(request):
    orders = Order.objects.select_related('user').prefetch_related(
        'order_items__product'
    ).order_by('-created_at')
    serializer = AdminOrderSerializer(orders, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdminRole])
def admin_update_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AdminOrderSerializer(
        order,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_customer_list(request):
    users = get_user_model().objects.filter(role='customer').annotate(
        orders_count=Count('order')
    ).order_by('-date_joined')
    serializer = AdminUserSerializer(users, many=True)
    return Response(serializer.data)


# -------------------- ADMIN USERS MANAGEMENT --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminRole])
def admin_users(request):
    """List all users or create a new user"""
    if request.method == 'GET':
        users = get_user_model().objects.annotate(orders_count=Count('order')).order_by('-date_joined')
        serializer = AdminUserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create new user
        UserModel = get_user_model()
        data = request.data
        
        if UserModel.objects.filter(username=data.get('username')).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if UserModel.objects.filter(email=data.get('email')).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        role = data.get('role', UserModel.Role.CUSTOMER)
        if role not in UserModel.Role.values:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

        user = UserModel.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password', 'temppassword123'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            role=role,
            is_staff=role == UserModel.Role.ADMIN,
            is_active=data.get('is_active', True)
        )
        
        serializer = AdminUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminRole])
def admin_user_detail(request, user_id):
    """Retrieve, update or delete a specific user"""
    try:
        user = get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = request.data
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        role = data.get('role', user.role)
        if role not in user.Role.values:
            return Response({'error': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        user.role = role
        user.is_staff = role == user.Role.ADMIN
        user.is_active = data.get('is_active', user.is_active)
        user.phone = data.get('phone', user.phone)
        user.address = data.get('address', user.address)
        user.save()
        
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        if user.id == request.user.id:
            return Response({'error': 'Cannot delete your own account'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)


# -------------------- ADMIN PRODUCTS MANAGEMENT --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsStaffOrAdminRole])
def admin_products(request):
    """List all products or create a new product"""
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrAdminRole])
def admin_product_detail(request, product_id):
    """Retrieve, update or delete a specific product"""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product.delete()
        return Response({'message': 'Product deleted'}, status=status.HTTP_204_NO_CONTENT)


# -------------------- ADMIN SETTINGS --------------------
from django.core.cache import cache

@api_view(['GET', 'PUT'])
@permission_classes([IsAdminRole])
def admin_settings(request):
    """Manage admin settings"""
    if request.method == 'GET':
        # Get settings from cache or database
        settings_data = cache.get('admin_settings', {})
        
        if not settings_data:
            settings_data = {
                'store_name': 'E-Commerce Store',
                'store_description': 'Your awesome e-commerce platform',
                'store_email': 'support@ecommerce.com',
                'store_phone': '+1-800-123-4567',
                'currency': 'USD',
                'tax_rate': '10',
                'shipping_cost': '10',
                'min_order_amount': '0',
                'maintenance_mode': False,
                'allow_registration': True,
                'require_email_verification': False,
            }
        
        return Response(settings_data)
    
    elif request.method == 'PUT':
        # Update settings
        settings_data = request.data
        cache.set('admin_settings', settings_data, timeout=None)
        return Response({
            'message': 'Settings updated successfully',
            'data': settings_data
        })
