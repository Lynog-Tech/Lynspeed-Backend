import logging

from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.hashers import make_password

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .utils import send_email, generate_token


logger = logging.getLogger(__name__)

class BaseUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def create_token_and_send_email(self, serializer_data, request):
        token_data = {
            'full_name': serializer_data['full_name'],
            'email': serializer_data['email'],
            'password': make_password(serializer_data['password']),
        }
        token = generate_token(token_data, settings.SECRET_KEY, 'email-confirmation')

        current_site = get_current_site(request).domain
        verification_link = f'http://{current_site}/api/v1/verify-email/{token}/'

        email_body = render_to_string('email/activate.html', {'verification_link': verification_link})
        send_email('Activate Your Account', email_body, serializer_data['email'])
