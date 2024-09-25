from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import CustomUser
from ..serializers import UserSerializer
from .base_views import BaseUserView, logger

class UserProfileView(BaseUserView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Retrieve and update the user's profile.",
        responses={
            200: openapi.Response("Profile retrieved successfully."),
            400: openapi.Response("Invalid data."),
            404: openapi.Response("User not found.")
        }
    )
    def get(self, request, *args, **kwargs):
        """Retrieve the authenticated user's profile."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """Update the authenticated user's profile."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User profile updated: {user.email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.warning("Validation errors during profile update.")
        return Response({
            "error": "Invalid data",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserSubscriptionStatusView(BaseUserView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve the user's subscription status.",
        responses={
            200: openapi.Response("Subscription status retrieved successfully."),
            404: openapi.Response("User not found.")
        }
    )
    def get(self, request, *args, **kwargs):
        """Retrieve the subscription status of the authenticated user."""
        user = request.user
        subscription_data = {
            'trial_count': user.trial_count,
            'subscribed': user.subscribed,
            'subscription_end_date': user.subscription_end_date,
        }
        logger.info(f"Retrieved subscription status for user: {user.email}")
        return Response(subscription_data, status=status.HTTP_200_OK)
