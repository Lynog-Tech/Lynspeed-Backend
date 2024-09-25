from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from user_auth.views.user_views import RegisterView, LoginView, VerifyEmailView, LogoutView
from user_auth.views.password_views import PasswordResetView, PasswordResetConfirmView
from user_auth.views.profile_subscription_view import UserProfileView, UserSubscriptionStatusView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('subscription-status/', UserSubscriptionStatusView.as_view(), name='subscription_status'),


    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

]