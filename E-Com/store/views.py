from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

# -------------------- CATEGORY --------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# -------------------- PRODUCT --------------------
@api_view(['GET', 'POST'])
def product_list_create(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({'error': 'Only admin can add products'}, status=403)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.is_staff:
            return Response({'error': 'Only admin can update products'}, status=403)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({'error': 'Only admin can delete products'}, status=403)
        product.delete()
        return Response({'message': 'Product deleted'}, status=204)

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
            item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            item.quantity = quantity
            item.save()
            return Response({'message': 'Item added to cart'})
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, item_id):
    try:
        item = CartItem.objects.get(id=item_id, cart__user=request.user)
        item.delete()
        return Response({'message': 'Item removed'})
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

# -------------------- ORDER --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return Response({'error': 'Cart is empty'}, status=400)

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
    cart.items.all().delete()

    return Response({'message': 'Order placed', 'order_id': order.id})

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
        return Response({'error': 'Order not found'}, status=404)

    serializer = ShippingAddressSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(order=order)
        return Response({'message': 'Shipping address added'})
    return Response(serializer.errors, status=400)

# -------------------- PAYMENT --------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)

    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save(order=order, is_successful=True)
        order.is_paid = True
        order.save()
        return Response({'message': 'Payment successful'})
    return Response(serializer.errors, status=400)

# -------------------- REVIEW --------------------
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def review_list_create(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)

    if request.method == 'GET':
        reviews = Review.objects.filter(product=product)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
