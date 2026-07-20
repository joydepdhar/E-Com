from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .serializers import RegisterSerializer, UserSerializer


class AuthAPITests(APITestCase):
    def v1(self, name):
        return reverse(f'api_v1:{name}')

    def test_register_login_and_refresh_tokens(self):
        register_response = self.client.post(
            self.v1('register'),
            {
                'username': 'new-customer',
                'email': 'new-customer@example.com',
                'password': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            format='json',
        )

        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(get_user_model().objects.filter(username='new-customer').exists())

        login_response = self.client.post(
            self.v1('token_obtain_pair'),
            {'username': 'new-customer', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        self.assertEqual(login_response.data['role'], get_user_model().Role.CUSTOMER)

        refresh_response = self.client.post(
            self.v1('token_refresh'),
            {'refresh': login_response.data['refresh']},
            format='json',
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_invalid_login_and_unauthorized_profile_access(self):
        get_user_model().objects.create_user(
            username='login-user',
            email='login-user@example.com',
            password='StrongPass123!',
        )

        login_response = self.client.post(
            self.v1('token_obtain_pair'),
            {'username': 'login-user', 'password': 'wrong-password'},
            format='json',
        )
        profile_response = self.client.get(self.v1('profile'))

        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(profile_response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserSerializerTests(APITestCase):
    def test_register_serializer_validates_password_confirmation(self):
        serializer = RegisterSerializer(data={
            'username': 'serializer-user',
            'email': 'serializer-user@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_user_serializer_keeps_role_read_only(self):
        user = get_user_model().objects.create_user(
            username='readonly-user',
            email='readonly-user@example.com',
            password='StrongPass123!',
        )
        serializer = UserSerializer(user, data={'role': get_user_model().Role.ADMIN}, partial=True)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.role, get_user_model().Role.CUSTOMER)
