import logging
from django.db import transaction
from django.db.models import Count, Prefetch, Q, Sum
from django.contrib.auth import get_user_model
from types import SimpleNamespace
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
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
from .filters import AliasOrderingFilter, OrderFilter, ProductFilter, UserFilter
from .pagination import StandardResultsSetPagination
from .audit import create_audit_log


store_logger = logging.getLogger('store')
payment_logger = logging.getLogger('store.payments')
order_logger = logging.getLogger('store.orders')


def product_queryset():
    return Product.objects.select_related('category')


def cart_queryset():
    return Cart.objects.select_related('user').prefetch_related(
        Prefetch(
            'items',
            queryset=CartItem.objects.select_related('product__category'),
        )
    )


def order_queryset():
    return Order.objects.select_related(
        'user',
        'shipping_address',
        'payment',
    ).prefetch_related(
        Prefetch(
            'order_items',
            queryset=OrderItem.objects.select_related('product__category'),
        )
    )


def apply_collection_query_options(
    request,
    queryset,
    *,
    filterset_class=None,
    search_fields=(),
    ordering_fields=(),
    ordering=None,
    ordering_field_aliases=None,
):
    """Apply declarative filters plus DRF search and ordering to a queryset."""
    if filterset_class:
        queryset = filterset_class(request.query_params, queryset=queryset).qs

    view = SimpleNamespace(
        search_fields=search_fields,
        ordering_fields=ordering_fields,
        ordering=ordering,
        ordering_field_aliases=ordering_field_aliases or {},
    )
    queryset = SearchFilter().filter_queryset(request, queryset, view)
    return AliasOrderingFilter().filter_queryset(request, queryset, view)


def paginated_response(request, queryset, serializer_class, *, context=None):
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True, context=context or {})
    return paginator.get_paginated_response(serializer.data)

# -------------------- CATEGORY --------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.order_by('id')
    return paginated_response(request, categories, CategorySerializer)


# -------------------- PRODUCT --------------------
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def product_list_create(request):
    if request.method == 'GET':
        products = product_queryset().filter(is_active=True).order_by('id')
        products = apply_collection_query_options(
            request,
            products,
            filterset_class=ProductFilter,
            search_fields=('name', 'description'),
            ordering_fields=('name', 'price', 'created_at'),
        )
        return paginated_response(
            request,
            products,
            ProductSerializer,
            context={'request': request},
        )

    if request.method == 'POST':
        if not getattr(request.user, 'is_staff_role', False):
            raise PermissionDenied('Only admin or staff can add products')
        serializer = ProductSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        store_logger.info(
            'admin_product_created actor_id=%s product_id=%s',
            request.user.id,
            product.id,
        )
        create_audit_log(
            request,
            action='product_created',
            object_type='Product',
            object_id=product.id,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def product_detail(request, pk):
    try:
        product = product_queryset().get(pk=pk)
    except Product.DoesNotExist:
        raise NotFound('Product not found')

    if request.method == 'GET':
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not getattr(request.user, 'is_staff_role', False):
            raise PermissionDenied('Only admin or staff can update products')
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        store_logger.info(
            'admin_product_updated actor_id=%s product_id=%s',
            request.user.id,
            product.id,
        )
        create_audit_log(
            request,
            action='product_updated',
            object_type='Product',
            object_id=product.id,
        )
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if not getattr(request.user, 'is_staff_role', False):
            raise PermissionDenied('Only admin or staff can delete products')
        product_id = product.id
        product.delete()
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
        return Response({'message': 'Product deleted'}, status=status.HTTP_204_NO_CONTENT)


# -------------------- CART --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        cart = cart_queryset().get(pk=cart.pk)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    if request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise NotFound('Product not found')

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
        raise NotFound('Item not found')


# -------------------- ORDER --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        with transaction.atomic():
            cart = Cart.objects.select_for_update().filter(user=request.user).first()
            if not cart:
                raise ValidationError({'error': 'Cart is empty'})

            cart_items = list(CartItem.objects.select_for_update().filter(cart=cart))
            if not cart_items:
                raise ValidationError({'error': 'Cart is empty'})

            product_ids = {item.product_id for item in cart_items if item.product_id is not None}
            # Lock inventory in a stable order so concurrent checkouts serialize safely.
            locked_products = {
                product.id: product
                for product in Product.objects.select_for_update().filter(
                    id__in=product_ids
                ).order_by('id')
            }

            requested_quantities = {}
            for item in cart_items:
                if item.product_id is None or item.product_id not in locked_products:
                    raise ValidationError({'error': 'A product in the cart no longer exists'})
                if item.quantity <= 0:
                    raise ValidationError({
                        'error': f'Quantity for product {item.product_id} must be greater than zero'
                    })

                product = locked_products[item.product_id]
                if not product.is_active:
                    raise ValidationError({'error': f'Product {product.id} is inactive'})
                requested_quantities[product.id] = (
                    requested_quantities.get(product.id, 0) + item.quantity
                )

            # Validate every locked product before creating the order or changing stock.
            for product_id, requested_quantity in requested_quantities.items():
                product = locked_products[product_id]
                if product.stock < requested_quantity:
                    raise ValidationError({
                        'error': f'Insufficient stock for product {product.id}'
                    })

            order = Order.objects.create(user=request.user)
            total_price = 0

            for item in cart_items:
                product = locked_products[item.product_id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )
                total_price += product.price * item.quantity

            # Stock changes occur while product rows remain locked by this transaction.
            for product_id, requested_quantity in requested_quantities.items():
                product = locked_products[product_id]
                product.stock -= requested_quantity
                product.save(update_fields=['stock'])

            order.total_price = total_price
            order.save(update_fields=['total_price'])

            # Clear the cart only after the order and inventory updates have succeeded.
            CartItem.objects.filter(id__in=[item.id for item in cart_items]).delete()

        order_logger.info(
            'order_created user_id=%s order_id=%s item_count=%s',
            request.user.id,
            order.id,
            len(cart_items),
        )
        return Response({'message': 'Order placed', 'order_id': order.id}, status=status.HTTP_201_CREATED)

    except ValidationError:
        raise
    except Exception:
        order_logger.exception(
            'order_creation_failed user_id=%s',
            getattr(request.user, 'id', None),
        )
        raise


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_list(request):
    orders = order_queryset().filter(user=request.user).order_by('id')
    orders = apply_collection_query_options(
        request,
        orders,
        filterset_class=OrderFilter,
        search_fields=('id', 'user__username'),
        ordering_fields=('created_at', 'total_price'),
        ordering_field_aliases={'total': 'total_price'},
    )
    return paginated_response(request, orders, OrderSerializer)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = order_queryset().get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        raise NotFound('Order not found')

    serializer = OrderSerializer(order, context={'request': request})
    return Response(serializer.data)


# -------------------- SHIPPING ADDRESS --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_shipping_address(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        raise NotFound('Order not found')

    serializer = ShippingAddressSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(order=order)
    return Response({'message': 'Shipping address added'})


# -------------------- PAYMENT --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, order_id):
    payment_logger.info(
        'payment_attempt user_id=%s order_id=%s',
        request.user.id,
        order_id,
    )
    data = request.data.copy()
    if not data.get('payment_method'):
        data['payment_method'] = 'Cash on Delivery'

    serializer = PaymentSerializer(data=data)
    if not serializer.is_valid():
        payment_logger.warning(
            'payment_attempt_failed reason=validation user_id=%s order_id=%s',
            request.user.id,
            order_id,
        )
        raise ValidationError(serializer.errors)

    try:
        with transaction.atomic():
            # Lock the order so concurrent retries cannot create competing payments.
            order = Order.objects.select_for_update().get(id=order_id, user=request.user)
            existing_payment = Payment.objects.filter(order=order).first()
            if existing_payment:
                payment_logger.info(
                    'payment_attempt_reused user_id=%s order_id=%s payment_id=%s status=%s',
                    request.user.id,
                    order.id,
                    existing_payment.id,
                    existing_payment.status,
                )
                return Response({
                    'message': 'Payment pending verification',
                    'payment_id': existing_payment.payment_id,
                    'status': existing_payment.status,
                }, status=status.HTTP_200_OK)

            payment_method = serializer.validated_data.get('payment_method', 'Cash on Delivery')
            payment_id = serializer.validated_data.get('payment_id')
            if payment_method.lower() in ['cash on delivery', 'cod'] and not payment_id:
                payment_id = f'COD-{order.id}'
            elif payment_method.lower() in ['sandbox', 'test', 'testgateway'] and not payment_id:
                payment_id = f'SANDBOX-{order.id}'

            # The payable amount is authoritative order data, never client input.
            payment = serializer.save(
                order=order,
                amount=order.total_price,
                status=Payment.Status.PENDING,
                is_successful=False,
                payment_id=payment_id,
            )
    except Order.DoesNotExist:
        payment_logger.warning(
            'payment_attempt_failed reason=order_not_found user_id=%s order_id=%s',
            request.user.id,
            order_id,
        )
        raise NotFound('Order not found')

    payment_logger.info(
        'payment_attempt_created user_id=%s order_id=%s payment_id=%s status=%s',
        request.user.id,
        order.id,
        payment.payment_id,
        payment.status,
    )
    return Response({
        'message': 'Payment pending verification',
        'payment_id': payment.payment_id,
        'status': payment.status,
    }, status=status.HTTP_201_CREATED)


# -------------------- REVIEW --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def review_list_create(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise NotFound('Product not found')

    if request.method == 'GET':
        reviews = Review.objects.select_related('user', 'product').filter(
            product=product
        ).order_by('id')
        return paginated_response(request, reviews, ReviewSerializer)

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -------------------- ADMIN DASHBOARD --------------------
@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_dashboard(request):
    order_totals = Order.objects.aggregate(
        revenue=Sum('total_price', filter=Q(is_paid=True)),
        orders=Count('id'),
        paid_orders=Count('id', filter=Q(is_paid=True)),
        pending_orders=Count('id', filter=Q(status__iexact='Pending')),
    )
    product_totals = Product.objects.aggregate(
        products=Count('id'),
        active_products=Count('id', filter=Q(is_active=True)),
    )

    order_status_counts = {
        item['status']: item['count']
        for item in Order.objects.values('status').annotate(count=Count('id'))
    }

    recent_orders = order_queryset().order_by('-created_at')[:5]
    low_stock_products = product_queryset().filter(
        stock__lte=5,
        is_active=True
    ).order_by('stock', 'name')[:10]

    return Response({
        'totals': {
            'revenue': order_totals['revenue'] or 0,
            'orders': order_totals['orders'],
            'paid_orders': order_totals['paid_orders'],
            'pending_orders': order_totals['pending_orders'],
            'products': product_totals['products'],
            'active_products': product_totals['active_products'],
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
    order_totals = Order.objects.aggregate(
        orders=Count('id'),
        pending_orders=Count('id', filter=Q(status__iexact='Pending')),
        paid_orders=Count('id', filter=Q(is_paid=True)),
    )
    product_totals = Product.objects.aggregate(
        products=Count('id'),
        active_products=Count('id', filter=Q(is_active=True)),
        low_stock_products=Count('id', filter=Q(stock__lte=5, is_active=True)),
    )
    recent_orders = order_queryset().order_by('-created_at')[:10]
    low_stock_products = product_queryset().filter(
        stock__lte=5,
        is_active=True
    ).order_by('stock', 'name')[:10]

    return Response({
        'totals': {
            'orders': order_totals['orders'],
            'pending_orders': order_totals['pending_orders'],
            'paid_orders': order_totals['paid_orders'],
            'products': product_totals['products'],
            'active_products': product_totals['active_products'],
            'low_stock_products': product_totals['low_stock_products'],
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
    order_totals = orders.aggregate(
        orders=Count('id'),
        pending_orders=Count('id', filter=Q(status__iexact='Pending')),
        paid_orders=Count('id', filter=Q(is_paid=True)),
    )
    recent_orders = order_queryset().filter(user=request.user).order_by('-created_at')[:5]
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart = cart_queryset().get(pk=cart.pk)

    return Response({
        'totals': {
            'orders': order_totals['orders'],
            'pending_orders': order_totals['pending_orders'],
            'paid_orders': order_totals['paid_orders'],
            'cart_items': len(cart.items.all()),
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
    orders = order_queryset().order_by('-created_at')
    orders = apply_collection_query_options(
        request,
        orders,
        filterset_class=OrderFilter,
        search_fields=('id', 'user__username'),
        ordering_fields=('created_at', 'total_price'),
        ordering=('-created_at',),
        ordering_field_aliases={'total': 'total_price'},
    )
    return paginated_response(
        request,
        orders,
        AdminOrderSerializer,
        context={'request': request},
    )


@api_view(['GET', 'PATCH'])
@permission_classes([IsAdminRole])
def admin_update_order(request, order_id):
    try:
        order = order_queryset().get(id=order_id)
    except Order.DoesNotExist:
        raise NotFound('Order not found')

    if request.method == 'GET':
        serializer = AdminOrderSerializer(order, context={'request': request})
        return Response(serializer.data)

    serializer = AdminOrderSerializer(
        order,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    old_status = order.status
    order = serializer.save()
    if old_status != order.status:
        order_logger.info(
            'admin_order_status_updated actor_id=%s order_id=%s old_status=%s new_status=%s',
            request.user.id,
            order.id,
            old_status,
            order.status,
        )
        create_audit_log(
            request,
            action='order_status_updated',
            object_type='Order',
            object_id=order.id,
        )
        if order.status.lower() == 'cancelled':
            order_logger.info(
                'order_cancelled actor_id=%s order_id=%s',
                request.user.id,
                order.id,
            )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_customer_list(request):
    users = get_user_model().objects.filter(role='customer').annotate(
        orders_count=Count('order')
    ).order_by('-date_joined')
    users = apply_collection_query_options(
        request,
        users,
        filterset_class=UserFilter,
        search_fields=('username', 'email', 'first_name', 'last_name'),
        ordering_fields=('username', 'date_joined'),
        ordering=('-date_joined',),
    )
    return paginated_response(request, users, AdminUserSerializer)


# -------------------- ADMIN USERS MANAGEMENT --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAdminRole])
def admin_users(request):
    """List all users or create a new user"""
    if request.method == 'GET':
        users = get_user_model().objects.annotate(orders_count=Count('order')).order_by('-date_joined')
        users = apply_collection_query_options(
            request,
            users,
            filterset_class=UserFilter,
            search_fields=('username', 'email', 'first_name', 'last_name'),
            ordering_fields=('username', 'date_joined'),
            ordering=('-date_joined',),
        )
        return paginated_response(request, users, AdminUserSerializer)
    
    elif request.method == 'POST':
        # Create new user
        UserModel = get_user_model()
        data = request.data
        
        if UserModel.objects.filter(username=data.get('username')).exists():
            raise ValidationError({'username': ['Username already exists']})
        
        if UserModel.objects.filter(email=data.get('email')).exists():
            raise ValidationError({'email': ['Email already exists']})
        
        role = data.get('role', UserModel.Role.CUSTOMER)
        if role not in UserModel.Role.values:
            raise ValidationError({'role': ['Invalid role']})

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

        store_logger.info(
            'admin_user_created actor_id=%s user_id=%s role=%s',
            request.user.id,
            user.id,
            user.role,
        )
        create_audit_log(
            request,
            action='user_created',
            object_type='User',
            object_id=user.id,
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
        raise NotFound('User not found')
    
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
            raise ValidationError({'role': ['Invalid role']})
        user.role = role
        user.is_staff = role == user.Role.ADMIN
        user.is_active = data.get('is_active', user.is_active)
        user.phone = data.get('phone', user.phone)
        user.address = data.get('address', user.address)
        user.save()

        store_logger.info(
            'admin_user_updated actor_id=%s user_id=%s role=%s is_active=%s',
            request.user.id,
            user.id,
            user.role,
            user.is_active,
        )
        create_audit_log(
            request,
            action='user_updated',
            object_type='User',
            object_id=user.id,
        )
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        if user.id == request.user.id:
            raise ValidationError({'user': ['Cannot delete your own account']})
        deleted_user_id = user.id
        user.delete()
        store_logger.info(
            'admin_user_deleted actor_id=%s user_id=%s',
            request.user.id,
            deleted_user_id,
        )
        create_audit_log(
            request,
            action='user_deleted',
            object_type='User',
            object_id=deleted_user_id,
        )
        return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)


# -------------------- ADMIN PRODUCTS MANAGEMENT --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsStaffOrAdminRole])
def admin_products(request):
    """List all products or create a new product"""
    if request.method == 'GET':
        products = product_queryset().order_by('id')
        products = apply_collection_query_options(
            request,
            products,
            filterset_class=ProductFilter,
            search_fields=('name', 'description'),
            ordering_fields=('name', 'price', 'created_at'),
        )
        return paginated_response(
            request,
            products,
            ProductSerializer,
            context={'request': request},
        )
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        store_logger.info(
            'admin_product_created actor_id=%s product_id=%s',
            request.user.id,
            product.id,
        )
        create_audit_log(
            request,
            action='product_created',
            object_type='Product',
            object_id=product.id,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsStaffOrAdminRole])
def admin_product_detail(request, product_id):
    """Retrieve, update or delete a specific product"""
    try:
        product = product_queryset().get(id=product_id)
    except Product.DoesNotExist:
        raise NotFound('Product not found')
    
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
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        store_logger.info(
            'admin_product_updated actor_id=%s product_id=%s',
            request.user.id,
            product.id,
        )
        create_audit_log(
            request,
            action='product_updated',
            object_type='Product',
            object_id=product.id,
        )
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        product_id = product.id
        product.delete()
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
        store_logger.info(
            'admin_settings_updated actor_id=%s',
            request.user.id,
        )
        create_audit_log(
            request,
            action='settings_updated',
            object_type='AdminSettings',
            object_id='admin_settings',
        )
        return Response({
            'message': 'Settings updated successfully',
            'data': settings_data
        })
