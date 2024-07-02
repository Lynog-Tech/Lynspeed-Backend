from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
import random

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    '''Serializer for CustomUser model'''
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'is_trial', 'trial_end_date', 'is_verified')

class RegisterSerializer(serializers.ModelSerializer):
    ''''
    Serializer for user registration
    Validates password and handles OTP generation
    '''
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'password', 'confirm_password')
        
    def validate(self, data):
        '''Ensure password match'''
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        '''Create user and generate OTP'''
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
        )
        user.otp = str(random.randint(100000, 999999))
        user.save()
        # Send Otp to user email
        send_mail(
            'Email Verfication',
            f'Your Otp code is {user.otp}',
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        return user
    
class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification"""
    email = serializers.EmailField()
    otp =serializers.CharField(max_length=6)
    
    def validate(self, data):
        """Validate email and otp"""
        try:
            user = User.objects.get(email=data['email'], otp=data['otp'])
        except User.DoesNotExist:
            raise serializers.ValidationError("invalid otp or email")
        return data
    
    def save(self, validated_data):
        """Activate user and set trial end date"""
        user = User.objects.get(email=validated_data['email'])
        user.is_verified = True
        user.set_trial_end_date()
        user.save()
        return user
    
class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate if the user with the given email exist"""
        try:
            user= User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
    def save(self):
        """ Generate  password reset token and send email"""
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            settings.EMAIL_HOST_USER,
            [email]
        )
        
class PasswordResetSerializer(serializers.Serializer):
    """ Serrializer for password reset"""
    uid =serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """validate password reset token and password match"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link")
        if not PasswordResetTokenGenerator().check_token(self.user, data['token']):
            raise serializers.ValidationError("Invalid or expired token")
        return data
    
    def save(self):
        """ Set new password for user"""
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer for obtaining JWT tokens with additional user data.
    """
    def validate(self, attrs):
        """
        Validate user credentials and add custom data to the token response.
        """
        data = super().validate(attrs)

        # Add custom data to the token response
        data.update({
            'user_id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
        })

        return data
