from django.urls import path
from subscriptionApp.views.views import PlanListView, SubscriptionView, SubscriptionActivateView 
from subscriptionApp.views.payment_views import InitializePaymentView, PaymentListView, VerifyPaymentView

urlpatterns = [
    # Plan URLs
    path('plans/', PlanListView.as_view(), name='plan-list'),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
    path('subscription/activate/', SubscriptionActivateView.as_view(), name='subscription-activate'),
    

    # Payment URLs
    path('payment/initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('payment/history/', PaymentListView.as_view(), name='payment-history'),

]
