from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

# -------------------- CATEGORY --------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


# -------------------- PRODUCT --------------------
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image', blank=True, null=True)  # Use CloudinaryField here
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name='product_price_gt_zero',
            ),
        ]
        indexes = [
            models.Index(
                fields=['category', 'is_active', 'price'],
                name='prod_cat_active_price_idx',
            ),
            models.Index(fields=['created_at'], name='prod_created_at_idx'),
        ]

    def __str__(self):
        return self.name


# -------------------- CART --------------------
class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='unique_cart_per_user',
            ),
        ]

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_cart_item_per_product',
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name='cartitem_quantity_gt_zero',
            ),
        ]

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name}"
        return f"{self.quantity} x [Deleted Product]"


# -------------------- ORDER --------------------
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, default='Pending')  # e.g., Shipped, Delivered, Cancelled

    class Meta:
        indexes = [
            models.Index(
                fields=['status', 'is_paid', 'created_at'],
                name='order_status_paid_created_idx',
            ),
            models.Index(fields=['total_price'], name='order_total_price_idx'),
        ]

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name='orderitem_quantity_gt_zero',
            ),
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='orderitem_price_gte_zero',
            ),
        ]

    def __str__(self):
        if self.product:
            return f"{self.quantity} x {self.product.name}"
        return f"{self.quantity} x [Deleted Product]"


# -------------------- SHIPPING ADDRESS --------------------
class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Shipping for Order #{self.order.pk}"


# -------------------- PAYMENT --------------------
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        SUCCESSFUL = 'Successful', 'Successful'
        FAILED = 'Failed', 'Failed'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50)  # e.g., Stripe, PayPal
    payment_id = models.CharField(max_length=100, blank=True)     # Transaction ID or COD reference
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_successful = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name='payment_amount_gte_zero',
            ),
        ]

    def __str__(self):
        return f"Payment for Order #{self.order.pk}"


# -------------------- REVIEW --------------------
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=5)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_review_per_user_product',
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name='review_rating_between_1_and_5',
            ),
        ]

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"


# -------------------- AUDIT LOG --------------------
class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
    )
    action = models.CharField(max_length=100)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action', 'timestamp'], name='audit_action_time_idx'),
            models.Index(fields=['object_type', 'object_id'], name='audit_object_idx'),
            models.Index(fields=['user', 'timestamp'], name='audit_user_time_idx'),
        ]

    def __str__(self):
        return f"{self.action} {self.object_type}#{self.object_id}"
