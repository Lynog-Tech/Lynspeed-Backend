from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core import mail
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.verify_otp_url = reverse('user-verify-otp')

    def test_user_registration_with_otp(self):
        # Create a new user
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "password": "testpassword",
            "confirm_password": "testpassword"
        }
        response = self.client.post(self.register_url, data, format='json')

        # Check that the response is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the user is created
        user = User.objects.get(username=data['username'])
        self.assertIsNotNone(user)

        # Check that an OTP email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Your Otp code is', mail.outbox[0].body)

        # Verify the OTP
        otp_data = {
            "email": data['email'],
            "otp": user.otp
        }
        otp_response = self.client.post(self.verify_otp_url, otp_data, format='json')

        # Check that the response is 200 OK
        self.assertEqual(otp_response.status_code, status.HTTP_200_OK)

        # Check that the user is verified
        user.refresh_from_db()
        self.assertTrue(user.is_verified)
