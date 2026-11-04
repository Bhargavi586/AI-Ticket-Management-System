from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthorizationTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='StrongPass!234',
            role=User.Role.CUSTOMER,
        )
        self.admin = User.objects.create_user(
            username='admin1',
            email='admin@example.com',
            password='StrongPass!234',
            role=User.Role.ADMIN,
        )

    def test_registration_creates_customer(self):
        response = self.client.post(reverse('register'), {
            'username': 'newcustomer',
            'email': 'new@example.com',
            'password': 'AnotherStrong!234',
            'confirm_password': 'AnotherStrong!234',
            'role': 'ADMIN',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['role'], User.Role.CUSTOMER)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password': '123',
            'confirm_password': '123',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_role_and_token_claim(self):
        response = self.client.post(reverse('login'), {
            'username': 'customer1',
            'password': 'StrongPass!234',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], User.Role.CUSTOMER)

    def test_profile_requires_authentication(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_access_admin_dashboard(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_admin_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.customer)
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            reverse('logout'),
            {'refresh': str(refresh)},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('accounts.serializers.id_token.verify_oauth2_token')
    def test_google_login_creates_customer(self, verify_token):
        verify_token.return_value = {
            'sub': 'google-sub-123',
            'email': 'google@example.com',
            'email_verified': True,
        }
        response = self.client.post(
            reverse('google-login'),
            {'token': 'mock-google-token'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(
            email='google@example.com',
            google_sub='google-sub-123',
        ).exists())

    @patch('accounts.serializers.id_token.verify_oauth2_token')
    def test_google_login_does_not_auto_link_existing_email(self, verify_token):
        verify_token.return_value = {
            'sub': 'google-sub-456',
            'email': self.customer.email,
            'email_verified': True,
        }
        response = self.client.post(
            reverse('google-login'),
            {'token': 'mock-google-token'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertIsNone(self.customer.google_sub)

    @patch('accounts.serializers.id_token.verify_oauth2_token')
    def test_authenticated_user_can_link_matching_google_account(self, verify_token):
        verify_token.return_value = {
            'sub': 'google-sub-789',
            'email': self.customer.email,
            'email_verified': True,
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.post(
            reverse('google-link'),
            {'token': 'mock-google-token'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.google_sub, 'google-sub-789')
