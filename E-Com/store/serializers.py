from rest_framework import serializers
from .models import (
    Category, Product, Cart, CartItem,
    Order, OrderItem, ShippingAddress,
    Payment, Review
)

# -------------------- CATEGORY --------------------
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']


# -------------------- PRODUCT --------------------
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'image',
            'stock', 'is_active', 'created_at',
            'category', 'category_id'
        ]
        read_only_fields = ['id', 'created_at']

    def get_image(self, obj):
        request = self.context.get('request', None)
        if request and obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None


# -------------------- CART ITEM --------------------
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        read_only_fields = ['id']


# -------------------- CART --------------------
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_price']
        read_only_fields = ['id', 'user', 'created_at']

    def get_total_price(self, obj):
        return sum([item.quantity * item.product.price for item in obj.items.all()])


# -------------------- ORDER ITEM --------------------
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['id']


# -------------------- SHIPPING --------------------
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'address', 'city', 'postal_code', 'country']
        read_only_fields = ['id']


# -------------------- PAYMENT --------------------
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_method', 'payment_id', 'amount', 'is_successful', 'paid_at']
        read_only_fields = ['id', 'is_successful', 'paid_at']


# -------------------- ORDER --------------------
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'is_paid', 'total_price', 'status', 'order_items', 'shipping_address', 'payment']
        read_only_fields = ['id', 'user', 'created_at', 'is_paid', 'total_price']


# -------------------- REVIEW --------------------
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product = serializers.StringRelatedField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'product_id', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
