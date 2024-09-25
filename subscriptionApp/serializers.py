from rest_framework import serializers
from .models import Plan, Subscription, Payment

class PlanSerializer(serializers.ModelSerializer):
    """
    Serializer for the Plan model, which handles the representation
    of different subscription plans.
    """
    class Meta:
        model = Plan
        fields = ['id', 'name', 'price', 'duration']  


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Subscription model, which manages user subscriptions
    and handles plan assignment, status updates, and active/inactive state.
    """
    plan = PlanSerializer(read_only=True)  # Nested serializer to include plan details

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'start_date', 'end_date', 'status']  
        read_only_fields = ['start_date', 'end_date', 'status']  
        
    def activate_subscription(self, subscription):
        """
        Activate the subscription by setting the status to 'Active' and
        calculating the end date based on the plan duration.
        """
        subscription.activate()  # Call the activate method on the subscription instance
        return subscription

    def deactivate_subscription(self, subscription):
        """
        Deactivate the subscription by setting the status to 'Inactive'.
        """
        subscription.deactivate()  # Call the deactivate method on the subscription instance
        return subscription


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model, which handles payment records and
    tracks payments related to user subscriptions.
    """
    class Meta:
        model = Payment
        fields = ['id', 'user', 'amount', 'payment_date', 'transaction_id']  
        read_only_fields = ['payment_date']  

    def create(self, validated_data):
        """
        Custom create method to handle payment creation and any additional logic,
        such as updating the subscription status after payment.
        """
        payment = Payment.objects.create(**validated_data)
        # You could include logic here to activate the user's subscription if needed
        # e.g., Activate subscription after a successful payment
        return payment
