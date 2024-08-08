from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Plan(models.Model):
    """
    Model to define different subscription plans.
    """
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(default=30)  # Duration in days

    def __str__(self):
        return self.name

class Subscription(models.Model):
    """
    Model to manage user subscriptions, including trial periods and active subscriptions.
    """
    STATUS_CHOICES = [
        ('Trial', 'Trial'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Trial')
    
    def __str__(self):
        return f"{self.user.email} - {self.status}"

    def activate(self):
        self.status = 'Active'
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.plan.duration)
        self.save()

    def deactivate(self):
        self.status = 'Inactive'
        self.save()

class Payment(models.Model):
    """
    Model to manage payment records for user subscriptions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.amount}"
