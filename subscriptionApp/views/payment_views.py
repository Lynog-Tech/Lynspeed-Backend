from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..models import Plan, Subscription, Payment
from ..serializers import PaymentSerializer
from .utils import initialize_paystack_payment, verify_paystack_payment  

class InitializePaymentView(generics.GenericAPIView):
    """
    Initialize a payment for a subscription plan using Paystack.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Initialize a payment session with Paystack")
    def post(self, request, *args, **kwargs):
        plan_id = request.data.get('plan_id')
        plan = get_object_or_404(Plan, id=plan_id)

        # Initialize Paystack payment
        payment_url, reference = initialize_paystack_payment(request.user, plan)
        if not payment_url:
            return Response({"detail": "Error initializing payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"payment_url": payment_url, "reference": reference}, status=status.HTTP_200_OK)


class VerifyPaymentView(generics.GenericAPIView):
    """
    Verify Paystack payment and activate the user's subscription.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(operation_description="Verify the Paystack payment for subscription")
    def post(self, request, *args, **kwargs):
        reference = request.data.get('reference')
        if not reference:
            return Response({"detail": "Payment reference is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify payment via Paystack
        is_valid, payment_info = verify_paystack_payment(reference)
        if not is_valid:
            return Response({"detail": "Invalid payment"}, status=status.HTTP_400_BAD_REQUEST)

        # If valid, activate the subscription
        plan_id = payment_info['plan_id']
        plan = get_object_or_404(Plan, id=plan_id)
        subscription = Subscription.objects.get(user=request.user)

        # Activate the subscription and record payment
        subscription.plan = plan
        subscription.activate()

        # Record payment
        Payment.objects.create(
            user=request.user,
            amount=payment_info['amount'],
            transaction_id=payment_info['transaction_id']
        )

        return Response({"message": "Payment successful, subscription activated"}, status=status.HTTP_200_OK)


class PaymentListView(generics.ListAPIView):
    """
    List payment history for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        """
        Retrieve the payment records for the authenticated user.
        """
        return Payment.objects.filter(user=self.request.user)

    @swagger_auto_schema(operation_description="List payment history for the user")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
