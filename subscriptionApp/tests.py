from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Plan, Subscription

User = get_user_model()

class SubscriptionTestCase(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate user for tests

        # Create some plans for testing
        self.plan1 = Plan.objects.create(name="Basic Plan", price=1000, duration_in_days=30)
        self.plan2 = Plan.objects.create(name="Premium Plan", price=3000, duration_in_days=90)

        # Create a subscription for the user
        self.subscription = Subscription.objects.create(user=self.user, plan=self.plan1)

    def test_list_plans(self):
        """
        Ensure we can list all available subscription plans.
        """
        url = reverse('plan-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # We created two plans in setUp()

    def test_get_subscription(self):
        """
        Ensure the user can retrieve their current subscription.
        """
        url = reverse('subscription')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['plan']['name'], self.plan1.name)  # Should match the current plan

    def test_update_subscription(self):
        """
        Ensure the user can update (change) their subscription plan.
        """
        url = reverse('subscription')
        response = self.client.put(url, data={'plan': self.plan2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh the subscription object and check the plan was updated
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.plan.id, self.plan2.id)

    def test_activate_subscription(self):
        """
        Ensure the user can activate a new subscription plan.
        """
        url = reverse('subscription-activate')
        data = {'plan_id': self.plan2.id}
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Subscription activated successfully")

        # Check if the user's subscription was updated to the new plan
        self.subscription.refresh_from_db()
        self.assertEqual(self.subscription.plan.id, self.plan2.id)

    def test_unauthenticated_user_cannot_access(self):
        """
        Ensure an unauthenticated user cannot access the subscription endpoints.
        """
        self.client.force_authenticate(user=None)  # Unauthenticate the user
        url = reverse('subscription')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

