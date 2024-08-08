from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'confirm_password', 'full_name', 'is_active', 'trial_end_date')
        read_only_fields = ('is_active', 'trial_end_date')

    def validate(self, data):
        """
        Check that the two password entries match.
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
   
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    is_forgotten_password = serializers.BooleanField(default=False)

class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(validators=[validate_password])
    token = serializers.CharField()
    uid = serializers.CharField()
    is_forgotten_password = serializers.BooleanField(default=False)
    
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()