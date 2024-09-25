from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..models import Plan, Subscription
from ..serializers import PlanSerializer, SubscriptionSerializer

class PlanListView(generics.ListAPIView):
    """
    List all available subscription plans.
    """
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

    @swagger_auto_schema(operation_description="Get a list of subscription plans")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SubscriptionView(generics.RetrieveUpdateAPIView):
    """
    Get the current user's subscription and manage subscription status.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    def get_object(self):
        """
        Return the user's subscription or raise 404 if none exists.
        """
        return get_object_or_404(Subscription, user=self.request.user)

    @swagger_auto_schema(operation_description="Get user's current subscription status")
    def get(self, request, *args, **kwargs):
        """
        Get the subscription details for the authenticated user.
        """
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_description="Update subscription, typically used when activating a plan.")
    def put(self, request, *args, **kwargs):
        """
        Activate or update a user's subscription.
        """
        return super().put(request, *args, **kwargs)


class SubscriptionActivateView(generics.GenericAPIView):
    """
    Activate or switch to a new subscription plan after payment.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer

    @swagger_auto_schema(operation_description="Activate a subscription plan after payment.")
    def post(self, request, *args, **kwargs):
        """
        Handle the subscription activation after payment has been made and verified.
        """
        plan_id = request.data.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)
        subscription = Subscription.objects.get(user=request.user)

        # Call the activate method from Subscription model
        subscription.plan = plan
        subscription.activate()
        return Response({"message": "Subscription activated successfully"}, status=status.HTTP_200_OK)



