from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    AuditLog, Cart, CartItem, Category, Order, OrderItem, Payment, Product, Review,
    ShippingAddress,
)
from .exceptions import custom_exception_handler
from .serializers import CartItemSerializer, ProductSerializer, ShippingAddressSerializer


class ApiRootTests(SimpleTestCase):
    def test_api_root_supports_json_clients(self):
        response = self.client.get('/', HTTP_ACCEPT='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['store'], '/api/store/')

    def test_api_root_supports_browser_html_requests(self):
        response = self.client.get('/', HTTP_ACCEPT='text/html')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/api/store/')


class APIVersioningTests(APITestCase):
    def test_v1_routes_are_available_and_legacy_routes_still_work(self):
        v1_url = reverse('api_v1:product-list-create')

        v1_response = self.client.get(v1_url)
        legacy_response = self.client.get(reverse('product-list-create'))

        self.assertEqual(v1_url, '/api/v1/products/')
        self.assertEqual(v1_response.status_code, status.HTTP_200_OK)
        self.assertEqual(legacy_response.status_code, status.HTTP_200_OK)

    def test_unsupported_api_version_is_rejected(self):
        response = self.client.get('/api/v2/products/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaymentEndpointTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='payment-owner', email='owner@example.com', password='StrongPass123!'
        )
        self.other_user = User.objects.create_user(
            username='other-user', email='other@example.com', password='StrongPass123!'
        )
        self.order = Order.objects.create(user=self.user, total_price=Decimal('125.50'))
        self.url = f'/api/store/orders/{self.order.id}/payment/'
        self.payload = {
            'payment_method': 'TestGateway',
            'payment_id': 'provider-reference-1',
            'amount': '0.01',
        }

    def test_payment_uses_order_total_and_stays_pending(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.amount, Decimal('125.50'))
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertFalse(payment.is_successful)
        self.order.refresh_from_db()
        self.assertFalse(self.order.is_paid)

    def test_repeated_request_returns_existing_payment(self):
        self.client.force_authenticate(self.user)
        first_response = self.client.post(self.url, self.payload, format='json')

        second_response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)
        self.assertEqual(first_response.data['payment_id'], second_response.data['payment_id'])

    def test_other_user_cannot_create_payment_for_order(self):
        self.client.force_authenticate(self.other_user)

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(Payment.objects.filter(order=self.order).exists())

    def test_invalid_payment_details_return_validation_errors_for_non_cod_methods(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {'payment_method': 'Stripe'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Validation error.')
        self.assertEqual(response.data['status_code'], status.HTTP_400_BAD_REQUEST)
        self.assertIn('payment_id', response.data['errors'])

    def test_default_payment_method_is_cash_on_delivery(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.payment_method, 'Cash on Delivery')
        self.assertTrue(payment.payment_id.startswith('COD-'))
        self.assertEqual(payment.amount, Decimal('125.50'))

    def test_cod_can_be_explicitly_specified_without_payment_id(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {'payment_method': 'COD'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.payment_method, 'COD')
        self.assertTrue(payment.payment_id.startswith('COD-'))

    def test_sandbox_payment_defaults_to_sandbox_id(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.url, {'payment_method': 'Sandbox'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.payment_method, 'Sandbox')
        self.assertTrue(payment.payment_id.startswith('SANDBOX-'))

    def test_reused_payment_returns_payment_id_not_pk(self):
        self.client.force_authenticate(self.user)
        first_response = self.client.post(self.url, self.payload, format='json')
        second_response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.data['payment_id'], second_response.data['payment_id'])
        self.assertEqual(first_response.data['payment_id'], Payment.objects.get(order=self.order).payment_id)


class OrderInventoryTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='checkout-user', email='checkout@example.com', password='StrongPass123!'
        )
        self.category = Category.objects.create(name='Checkout', slug='checkout')
        self.product = Product.objects.create(
            category=self.category,
            name='Inventory product',
            description='Product used by checkout tests',
            price=Decimal('25.00'),
            stock=5,
        )
        self.cart = Cart.objects.create(user=self.user)
        self.client.force_authenticate(self.user)
        self.url = '/api/store/orders/create/'

    def test_checkout_deducts_stock_and_clears_cart(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())
        order = Order.objects.get(id=response.data['order_id'])
        self.assertEqual(order.total_price, Decimal('50.00'))
        self.assertEqual(OrderItem.objects.get(order=order).quantity, 2)

    def test_insufficient_stock_rolls_back_checkout(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=6)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('Insufficient stock', str(response.data['errors']))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)
        self.assertFalse(Order.objects.filter(user=self.user).exists())
        self.assertTrue(CartItem.objects.filter(cart=self.cart).exists())

    def test_inactive_product_rolls_back_checkout(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('inactive', str(response.data['errors']))
        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_database_rejects_non_positive_cart_item_quantity(self):
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, product=self.product, quantity=0)

    def test_missing_product_rolls_back_checkout(self):
        CartItem.objects.create(cart=self.cart, product=None, quantity=1)

        response = self.client.post(self.url, {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['success'], False)
        self.assertIn('no longer exists', str(response.data['errors']))
        self.assertFalse(Order.objects.filter(user=self.user).exists())


class CollectionEndpointTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(
            username='collection-customer',
            email='collection-customer@example.com',
            password='StrongPass123!',
        )
        self.admin = User.objects.create_user(
            username='collection-admin',
            email='collection-admin@example.com',
            password='StrongPass123!',
            role=User.Role.ADMIN,
        )
        self.category = Category.objects.create(name='Collections', slug='collections')
        self.active_product = Product.objects.create(
            category=self.category,
            name='Wireless keyboard',
            description='Compact wireless keyboard',
            price=Decimal('49.99'),
            stock=10,
        )
        self.inactive_product = Product.objects.create(
            category=self.category,
            name='Archived keyboard',
            description='Inactive product',
            price=Decimal('29.99'),
            stock=10,
            is_active=False,
        )

    def test_product_collection_paginates_filters_searches_and_orders(self):
        response = self.client.get(
            '/api/store/products/',
            {
                'category': self.category.id,
                'min_price': '40',
                'max_price': '50',
                'search': 'wireless',
                'ordering': '-price',
                'page_size': 1,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.active_product.id)

    def test_category_and_review_collections_paginate(self):
        self.client.force_authenticate(self.customer)
        Review.objects.create(user=self.customer, product=self.active_product, rating=5)

        category_response = self.client.get('/api/store/categories/?page_size=1')
        review_response = self.client.get(
            f'/api/store/products/{self.active_product.id}/reviews/?page_size=1'
        )

        self.assertEqual(category_response.status_code, status.HTTP_200_OK)
        self.assertIn('results', category_response.data)
        self.assertEqual(review_response.status_code, status.HTTP_200_OK)
        self.assertEqual(review_response.data['count'], 1)

    def test_order_collection_filters_searches_and_orders_by_total_alias(self):
        Order.objects.create(
            user=self.customer,
            status='Shipped',
            is_paid=True,
            total_price=Decimal('75.00'),
        )
        Order.objects.create(
            user=self.customer,
            status='Pending',
            is_paid=False,
            total_price=Decimal('25.00'),
        )
        self.client.force_authenticate(self.customer)

        response = self.client.get(
            '/api/store/orders/',
            {
                'status': 'shipped',
                'is_paid': 'true',
                'customer': self.customer.id,
                'search': 'collection-customer',
                'ordering': '-total',
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['total_price'], '75.00')

    def test_admin_collections_preserve_permissions_and_query_options(self):
        Order.objects.create(
            user=self.customer,
            status='Shipped',
            is_paid=True,
            total_price=Decimal('75.00'),
        )
        self.client.force_authenticate(self.admin)

        product_response = self.client.get(
            '/api/store/admin/products/?is_active=false&search=archived&ordering=price'
        )
        order_response = self.client.get(
            f'/api/store/admin/orders/?customer={self.customer.id}&ordering=-total'
        )
        user_response = self.client.get(
            '/api/store/admin/users/?is_staff=true&search=collection-admin&ordering=username'
        )
        customer_response = self.client.get(
            '/api/store/admin/customers/?is_active=true&search=collection-customer&ordering=username'
        )

        self.assertEqual(product_response.status_code, status.HTTP_200_OK)
        self.assertEqual(product_response.data['count'], 1)
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.data['count'], 1)
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_response.data['count'], 1)
        self.assertEqual(customer_response.status_code, status.HTTP_200_OK)
        self.assertEqual(customer_response.data['count'], 1)


class QueryOptimizationTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(
            username='query-customer',
            email='query-customer@example.com',
            password='StrongPass123!',
        )
        self.admin = User.objects.create_user(
            username='query-admin',
            email='query-admin@example.com',
            password='StrongPass123!',
            role=User.Role.ADMIN,
        )
        category = Category.objects.create(name='Query category', slug='query-category')
        self.product = Product.objects.create(
            category=category,
            name='Query product',
            description='Product for query count tests',
            price=Decimal('25.00'),
            stock=10,
        )
        cart = Cart.objects.create(user=self.customer)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.order = Order.objects.create(
            user=self.customer,
            total_price=Decimal('50.00'),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('25.00'),
        )
        ShippingAddress.objects.create(
            order=self.order,
            address='1 Query Street',
            city='Test City',
            postal_code='1000',
            country='Test Country',
        )
        Payment.objects.create(
            order=self.order,
            payment_method='TestGateway',
            payment_id='query-payment',
            amount=Decimal('50.00'),
        )
        Review.objects.create(user=self.customer, product=self.product, rating=5)

    def test_product_cart_order_and_review_queries_are_constant(self):
        with self.assertNumQueries(2):
            product_response = self.client.get('/api/store/products/')
        self.assertEqual(product_response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.customer)
        with self.assertNumQueries(3):
            cart_response = self.client.get('/api/store/cart/')
        with self.assertNumQueries(3):
            order_response = self.client.get('/api/store/orders/')
        with self.assertNumQueries(3):
            review_response = self.client.get(
                f'/api/store/products/{self.product.id}/reviews/'
            )

        self.assertEqual(cart_response.status_code, status.HTTP_200_OK)
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.assertEqual(review_response.status_code, status.HTTP_200_OK)

    def test_dashboard_queries_use_aggregates_and_prefetches(self):
        self.client.force_authenticate(self.admin)

        with self.assertNumQueries(8):
            admin_response = self.client.get('/api/store/admin/dashboard/')
        with self.assertNumQueries(5):
            staff_response = self.client.get('/api/store/staff/dashboard/')

        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        self.assertEqual(staff_response.status_code, status.HTTP_200_OK)


class ObservabilityTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='audit-admin',
            email='audit-admin@example.com',
            password='StrongPass123!',
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.customer = User.objects.create_user(
            username='audit-customer',
            email='audit-customer@example.com',
            password='StrongPass123!',
        )
        self.category = Category.objects.create(name='Audit category', slug='audit-category')
        self.product = Product.objects.create(
            category=self.category,
            name='Audited product',
            description='Product for audit tests',
            price=Decimal('25.00'),
            stock=10,
        )

    def test_request_id_header_is_added(self):
        response = self.client.get('/api/store/products/', HTTP_X_REQUEST_ID='test-request-id')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['X-Request-ID'], 'test-request-id')

    def test_admin_product_create_writes_audit_log(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            '/api/store/admin/products/',
            {
                'category_id': self.category.id,
                'name': 'New audited product',
                'description': 'Created through admin API',
                'price': '30.00',
                'stock': 5,
            },
            format='json',
            REMOTE_ADDR='127.0.0.1',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        audit_log = AuditLog.objects.get(
            action='product_created',
            object_type='Product',
            object_id=str(response.data['id']),
        )
        self.assertEqual(audit_log.user, self.admin)
        self.assertEqual(audit_log.ip_address, '127.0.0.1')

    def test_admin_order_status_update_writes_audit_log_and_logs_event(self):
        self.client.force_authenticate(self.admin)
        order = Order.objects.create(user=self.customer, total_price=Decimal('25.00'))

        with self.assertLogs('store.orders', level='INFO') as captured_logs:
            response = self.client.patch(
                f'/api/store/admin/orders/{order.id}/',
                {'status': 'Cancelled'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            AuditLog.objects.filter(
                action='order_status_updated',
                object_type='Order',
                object_id=str(order.id),
                user=self.admin,
            ).exists()
        )
        self.assertTrue(
            any('order_cancelled' in message for message in captured_logs.output)
        )

    def test_admin_settings_update_writes_audit_log(self):
        self.client.force_authenticate(self.admin)

        response = self.client.put(
            '/api/store/admin/settings/',
            {'maintenance_mode': False},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            AuditLog.objects.filter(
                action='settings_updated',
                object_type='AdminSettings',
                object_id='admin_settings',
                user=self.admin,
            ).exists()
        )

    def test_registration_and_login_are_logged_without_sensitive_payloads(self):
        with self.assertLogs('authentication', level='INFO') as registration_logs:
            register_response = self.client.post(
                '/api/user_app/register/',
                {
                    'username': 'logged-registration',
                    'email': 'logged-registration@example.com',
                    'password': 'StrongPass123!',
                    'password2': 'StrongPass123!',
                },
                format='json',
            )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        registered_user = get_user_model().objects.get(username='logged-registration')
        self.assertTrue(
            AuditLog.objects.filter(
                action='user_registered',
                object_type='User',
                object_id=str(registered_user.id),
            ).exists()
        )
        self.assertIn('user_registered', registration_logs.output[0])
        self.assertNotIn('StrongPass123', registration_logs.output[0])

        with self.assertLogs('authentication', level='INFO') as login_logs:
            login_response = self.client.post(
                '/api/user_app/login/',
                {
                    'username': 'logged-registration',
                    'password': 'StrongPass123!',
                },
                format='json',
            )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('user_login_success', login_logs.output[0])
        self.assertNotIn('StrongPass123', login_logs.output[0])


class CentralizedExceptionHandlingTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.customer = User.objects.create_user(
            username='exception-customer',
            email='exception-customer@example.com',
            password='StrongPass123!',
        )
        self.admin = User.objects.create_user(
            username='exception-admin',
            email='exception-admin@example.com',
            password='StrongPass123!',
            role=User.Role.ADMIN,
            is_staff=True,
        )
        self.category = Category.objects.create(name='Exceptions', slug='exceptions')

    def assert_error_envelope(self, response, expected_status):
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.data['success'], False)
        self.assertIn('message', response.data)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data['status_code'], expected_status)

    def test_unauthenticated_response_uses_standard_error_envelope(self):
        response = self.client.get('/api/store/cart/')

        self.assert_error_envelope(response, status.HTTP_401_UNAUTHORIZED)

    def test_permission_denied_response_uses_standard_error_envelope(self):
        self.client.force_authenticate(self.customer)

        response = self.client.get('/api/store/admin/products/')

        self.assert_error_envelope(response, status.HTTP_403_FORBIDDEN)

    def test_not_found_response_uses_standard_error_envelope(self):
        response = self.client.get('/api/store/products/999999/')

        self.assert_error_envelope(response, status.HTTP_404_NOT_FOUND)

    def test_validation_response_uses_standard_error_envelope(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            '/api/store/admin/products/',
            {
                'category_id': self.category.id,
                'name': '',
                'description': 'Invalid product',
                'price': '10.00',
                'stock': 1,
            },
            format='json',
        )

        self.assert_error_envelope(response, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data['errors'])

    def test_generic_exception_returns_safe_500_error_envelope(self):
        with self.assertLogs('store', level='ERROR'):
            response = custom_exception_handler(
                RuntimeError('internal secret details'),
                {'request': None, 'view': None},
            )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data,
            {
                'success': False,
                'message': 'An unexpected error occurred.',
                'errors': {},
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
            },
        )
        self.assertNotIn('internal secret details', str(response.data))


class StoreAPITestMixin:
    password = 'StrongPass123!'

    def v1(self, name, **kwargs):
        return reverse(f'api_v1:{name}', kwargs=kwargs)

    def create_user(self, username='customer', role=None, is_superuser=False):
        User = get_user_model()
        role = role or User.Role.CUSTOMER
        return User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=self.password,
            role=role,
            is_superuser=is_superuser,
        )

    def create_product(self, name='Test product', stock=10, is_active=True, price='10.00'):
        category, _ = Category.objects.get_or_create(
            slug='test-category',
            defaults={'name': 'Test category'},
        )
        return Product.objects.create(
            category=category,
            name=name,
            description=f'{name} description',
            price=Decimal(price),
            stock=stock,
            is_active=is_active,
        )


class PermissionAndSecurityTests(StoreAPITestMixin, APITestCase):
    def setUp(self):
        self.user = self.create_user('plain-user')
        self.other_user = self.create_user('other-owner')
        self.admin = self.create_user('admin-user', role=get_user_model().Role.ADMIN)
        self.product = self.create_product()

    def test_normal_user_cannot_access_admin_endpoints_and_admin_can(self):
        self.client.force_authenticate(self.user)
        denied_response = self.client.get(self.v1('admin-dashboard'))

        self.client.force_authenticate(self.admin)
        allowed_response = self.client.get(self.v1('admin-dashboard'))

        self.assertEqual(denied_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(allowed_response.status_code, status.HTTP_200_OK)

    def test_user_cannot_access_another_users_cart_item(self):
        cart = Cart.objects.create(user=self.other_user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        self.client.force_authenticate(self.user)

        response = self.client.delete(self.v1('remove-cart-item', item_id=item.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(CartItem.objects.filter(id=item.id).exists())

    def test_user_cannot_access_another_users_orders_or_payments(self):
        order = Order.objects.create(user=self.other_user, total_price=Decimal('10.00'))
        self.client.force_authenticate(self.user)

        list_response = self.client.get(self.v1('order-list'))
        payment_response = self.client.post(
            self.v1('make-payment', order_id=order.id),
            {'payment_method': 'TestGateway', 'payment_id': 'unauthorized'},
            format='json',
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 0)
        self.assertEqual(payment_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_protected_endpoints_require_authentication(self):
        cart_response = self.client.get(self.v1('cart'))
        checkout_response = self.client.post(self.v1('create-order'), {}, format='json')
        admin_response = self.client.get(self.v1('admin-users'))

        self.assertEqual(cart_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(checkout_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(admin_response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProductAndCartAPITests(StoreAPITestMixin, APITestCase):
    def setUp(self):
        self.user = self.create_user('cart-user')
        self.category = Category.objects.create(name='Accessories', slug='accessories')
        self.keyboard = Product.objects.create(
            category=self.category,
            name='Wireless keyboard',
            description='Compact keyboard',
            price=Decimal('49.99'),
            stock=10,
        )
        self.mouse = Product.objects.create(
            category=self.category,
            name='Bluetooth mouse',
            description='Compact mouse',
            price=Decimal('24.99'),
            stock=10,
        )

    def test_product_list_detail_filter_search_and_pagination(self):
        list_response = self.client.get(self.v1('product-list-create'), {
            'category': self.category.id,
            'search': 'keyboard',
            'page_size': 1,
        })
        detail_response = self.client.get(self.v1('product-detail', pk=self.keyboard.id))

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)
        self.assertEqual(list_response.data['results'][0]['id'], self.keyboard.id)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['name'], 'Wireless keyboard')

    def test_cart_add_update_remove_invalid_quantity_and_duplicate_prevention(self):
        self.client.force_authenticate(self.user)
        cart_url = self.v1('cart')

        add_response = self.client.post(
            cart_url,
            {'product_id': self.keyboard.id, 'quantity': 2},
            format='json',
        )
        duplicate_response = self.client.post(
            cart_url,
            {'product_id': self.keyboard.id, 'quantity': 4},
            format='json',
        )
        item = CartItem.objects.get(cart__user=self.user, product=self.keyboard)
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)
        self.assertEqual(duplicate_response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.filter(cart__user=self.user, product=self.keyboard).count(), 1)
        self.assertEqual(item.quantity, 4)

        remove_response = self.client.delete(self.v1('remove-cart-item', item_id=item.id))
        self.assertEqual(remove_response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())

        invalid_response = self.client.post(
            cart_url,
            {'product_id': self.mouse.id, 'quantity': 0},
            format='json',
        )
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)


class CheckoutOrderAndPaymentAPITests(StoreAPITestMixin, APITestCase):
    def setUp(self):
        self.user = self.create_user('checkout-api-user')
        self.admin = self.create_user('checkout-api-admin', role=get_user_model().Role.ADMIN)
        self.product = self.create_product(name='Checkout widget', stock=3, price='15.00')
        self.cart = Cart.objects.create(user=self.user)

    def test_successful_checkout_creates_order_lists_order_and_accepts_payment_idempotently(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.client.force_authenticate(self.user)

        checkout_response = self.client.post(self.v1('create-order'), {}, format='json')
        order_id = checkout_response.data['order_id']
        list_response = self.client.get(self.v1('order-list'))
        payment_url = self.v1('make-payment', order_id=order_id)
        first_payment = self.client.post(
            payment_url,
            {'payment_method': 'TestGateway', 'payment_id': 'pay-1'},
            format='json',
        )
        duplicate_payment = self.client.post(
            payment_url,
            {'payment_method': 'TestGateway', 'payment_id': 'pay-1'},
            format='json',
        )

        self.assertEqual(checkout_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.get(id=order_id).total_price, Decimal('30.00'))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data['count'], 1)
        self.assertEqual(first_payment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(duplicate_payment.status_code, status.HTTP_200_OK)
        self.assertEqual(Payment.objects.filter(order_id=order_id).count(), 1)

    def test_customer_can_retrieve_order_detail(self):
        order = Order.objects.create(user=self.user, total_price=Decimal('20.00'), status='Pending')
        self.client.force_authenticate(self.user)

        response = self.client.get(self.v1('order-detail', order_id=order.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['total_price'], str(order.total_price))
        self.assertEqual(response.data['status'], 'Pending')

    def test_checkout_empty_cart_out_of_stock_inactive_and_insufficient_stock(self):
        self.client.force_authenticate(self.user)
        empty_response = self.client.post(self.v1('create-order'), {}, format='json')

        CartItem.objects.create(cart=self.cart, product=self.product, quantity=4)
        insufficient_response = self.client.post(self.v1('create-order'), {}, format='json')

        self.cart.items.all().delete()
        self.product.stock = 0
        self.product.save(update_fields=['stock'])
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        out_of_stock_response = self.client.post(self.v1('create-order'), {}, format='json')

        self.cart.items.all().delete()
        self.product.stock = 2
        self.product.is_active = False
        self.product.save(update_fields=['stock', 'is_active'])
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        inactive_response = self.client.post(self.v1('create-order'), {}, format='json')

        self.assertEqual(empty_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(insufficient_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(out_of_stock_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(inactive_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_retrieves_and_updates_order_status_and_invalid_transition_is_not_enforced(self):
        order = Order.objects.create(user=self.user, total_price=Decimal('15.00'))
        self.client.force_authenticate(self.admin)
        url = self.v1('admin-update-order', order_id=order.id)

        retrieve_response = self.client.get(url)
        update_response = self.client.patch(url, {'status': 'Shipped'}, format='json')
        current_behavior_response = self.client.patch(url, {'status': 'Pending'}, format='json')

        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['id'], order.id)
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(current_behavior_response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'Pending')

    def test_invalid_and_unauthorized_payment_requests(self):
        order = Order.objects.create(user=self.user, total_price=Decimal('15.00'))

        unauthorized_response = self.client.post(
            self.v1('make-payment', order_id=order.id),
            {'payment_method': 'TestGateway', 'payment_id': 'pay-no-auth'},
            format='json',
        )
        self.client.force_authenticate(self.user)
        invalid_response = self.client.post(
            self.v1('make-payment', order_id=order.id),
            {},
            format='json',
        )

        self.assertEqual(unauthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_checkout_request_after_success_does_not_double_decrement_stock(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.client.force_authenticate(self.user)

        first_response = self.client.post(self.v1('create-order'), {}, format='json')
        second_response = self.client.post(self.v1('create-order'), {}, format='json')

        self.product.refresh_from_db()
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)


class AdminAPITests(StoreAPITestMixin, APITestCase):
    def setUp(self):
        self.admin = self.create_user('full-admin', role=get_user_model().Role.ADMIN)
        self.customer = self.create_user('managed-customer')
        self.category = Category.objects.create(name='Admin category', slug='admin-category')
        self.product = Product.objects.create(
            category=self.category,
            name='Admin product',
            description='Managed product',
            price=Decimal('20.00'),
            stock=5,
        )
        self.order = Order.objects.create(user=self.customer, total_price=Decimal('20.00'))
        self.client.force_authenticate(self.admin)

    def test_admin_product_crud_user_crud_order_dashboard_and_settings(self):
        product_create = self.client.post(
            self.v1('admin-products'),
            {
                'category_id': self.category.id,
                'name': 'Created product',
                'description': 'Created through tests',
                'price': '12.00',
                'stock': 3,
            },
            format='json',
        )
        product_id = product_create.data['id']
        product_update = self.client.put(
            self.v1('admin-product-detail', product_id=product_id),
            {'name': 'Updated product'},
            format='json',
        )
        product_delete = self.client.delete(self.v1('admin-product-detail', product_id=product_id))

        user_create = self.client.post(
            self.v1('admin-users'),
            {
                'username': 'created-user',
                'email': 'created-user@example.com',
                'password': 'StrongPass123!',
                'role': get_user_model().Role.CUSTOMER,
            },
            format='json',
        )
        user_id = user_create.data['id']
        user_update = self.client.put(
            self.v1('admin-user-detail', user_id=user_id),
            {'first_name': 'Updated', 'role': get_user_model().Role.CUSTOMER},
            format='json',
        )
        user_delete = self.client.delete(self.v1('admin-user-detail', user_id=user_id))

        order_update = self.client.patch(
            self.v1('admin-update-order', order_id=self.order.id),
            {'status': 'Shipped'},
            format='json',
        )
        dashboard = self.client.get(self.v1('admin-dashboard'))
        settings_response = self.client.put(
            self.v1('admin-settings'),
            {'store_name': 'Test Store', 'maintenance_mode': False},
            format='json',
        )

        self.assertEqual(product_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(product_update.status_code, status.HTTP_200_OK)
        self.assertEqual(product_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user_update.status_code, status.HTTP_200_OK)
        self.assertEqual(user_delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(order_update.status_code, status.HTTP_200_OK)
        self.assertEqual(dashboard.status_code, status.HTTP_200_OK)
        self.assertIn('totals', dashboard.data)
        self.assertEqual(settings_response.status_code, status.HTTP_200_OK)


class StoreSerializerAndModelTests(StoreAPITestMixin, APITestCase):
    def setUp(self):
        self.product = self.create_product()

    def test_serializers_validate_required_fields_and_invalid_data(self):
        product_serializer = ProductSerializer(data={
            'category_id': self.product.category_id,
            'name': '',
            'description': 'Invalid',
            'price': '-1.00',
            'stock': 1,
        })
        cart_item_serializer = CartItemSerializer(data={'product_id': self.product.id, 'quantity': 1})
        shipping_serializer = ShippingAddressSerializer(data={'address': '1 Main Street'})

        self.assertFalse(product_serializer.is_valid())
        self.assertIn('name', product_serializer.errors)
        self.assertTrue(cart_item_serializer.is_valid(), cart_item_serializer.errors)
        self.assertFalse(shipping_serializer.is_valid())
        self.assertIn('city', shipping_serializer.errors)

    def test_model_constraints_unique_constraints_and_methods(self):
        user = self.create_user('model-user')
        cart = Cart.objects.create(user=user)

        self.assertEqual(str(self.product), 'Test product')
        self.assertIn("model-user", str(cart))
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Category.objects.create(name='Test category', slug='test-category')
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Cart.objects.create(user=user)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Product.objects.create(
                    category=self.product.category,
                    name='Invalid price',
                    description='Invalid',
                    price=Decimal('0.00'),
                    stock=1,
                )

    def test_related_model_methods_and_constraints(self):
        user = self.create_user('related-model-user')
        order = Order.objects.create(user=user, total_price=Decimal('10.00'))
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal('10.00'),
        )
        payment = Payment.objects.create(
            order=order,
            payment_method='TestGateway',
            payment_id='model-payment',
            amount=Decimal('10.00'),
        )
        review = Review.objects.create(user=user, product=self.product, rating=5)

        self.assertIn('Order #', str(order))
        self.assertIn('Test product', str(order_item))
        self.assertIn('Payment for Order', str(payment))
        self.assertIn('Review by related-model-user', str(review))
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Review.objects.create(user=user, product=self.product, rating=5)
