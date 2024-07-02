from rest_framework import generics,viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, logout
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    Viewsets for User Registration and OTP verification
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=RegisterSerializer,
        responses={201: UserSerializer()}
    )
    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        """Handle User registration"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"detail": "User registered successfully. Please verify your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Verify OTP",
        request_body=VerifyOTPSerializer,
        responses={200: openapi.Response("OTP verified and trial activated")}
    )
    @action(detail=False, methods=['post'], url_path='verify-otp')
    def verify_otp(self, request):
        """Handle OTP verification"""
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "OTP verified and trial activated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CustomTokenObtainPairView(TokenObtainPairView):
    """View for user login"""
    serializer_class = CustomTokenObtainPairSerializer
    @swagger_auto_schema(
        operation_description="Login a user",
        request_body= CustomTokenObtainPairSerializer,
        responses={201: UserSerializer()}
    )
    @action(detail=False, methods=['post'], url_path='register')
    def post(self, request, *args, **kwargs):
        """Handle user Login"""
        return super().post(request, *args, **kwargs)
class ProfileView(generics.RetrieveUpdateAPIView):
    """
    View to retrieve and update user profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Return the authenticated user.
        """
        return self.request.user

class PasswordResetRequestView(generics.GenericAPIView):
    """
    View to handle password reset request.
    """
    serializer_class = PasswordResetRequestSerializer

    @swagger_auto_schema(
        operation_description="Request password reset.",
        request_body=PasswordResetRequestSerializer,
        responses={200: openapi.Response('Password reset link sent.')}
    )
    def post(self, request, *args, **kwargs):
        """
        Handle password reset request.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password reset link sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(generics.GenericAPIView):
    """
    View to handle password reset.
    """
    serializer_class = PasswordResetSerializer

    @swagger_auto_schema(
        operation_description="Reset password.",
        request_body=PasswordResetSerializer,
        responses={200: openapi.Response('Password has been reset.')}
    )
    def post(self, request, *args, **kwargs):
        """
        Handle password reset.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(generics.GenericAPIView):
    """
    View to handle user logout.
    """
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Logout user by blacklisting their refresh token.",
        responses={200: openapi.Response('Logout successful.')}
    )
    def post(self, request, *args, **kwargs):
        """
        Handle user logout.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)