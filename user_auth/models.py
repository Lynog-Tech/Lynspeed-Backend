from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from datetime import timedelta
from django.core.cache import cache
from django.utils import timezone

def default_trial_end_date():
    return timezone.now() + timedelta(days=1)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Free trial logic
    trial_count = models.IntegerField(default=2)
    trial_end_date = models.DateTimeField(default=default_trial_end_date)  

    # Subscription logic
    subscribed = models.BooleanField(default=False)
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @classmethod
    def get_user_by_email(cls, email):
        """Retrieve user from cache or database by email."""
        cache_key = f"user_email_{email}"
        user = cache.get(cache_key)
        if not user:
            user = cls.objects.filter(email=email).first()
            if user:
                cache.set(cache_key, user, timeout=300)
        return user

    @classmethod
    def get_user_by_id(cls, user_id):
        """Retrieve user from cache or database by ID."""
        cache_key = f"user_id_{user_id}"
        user = cache.get(cache_key)
        if not user:
            user = cls.objects.filter(id=user_id).first()
            if user:
                cache.set(cache_key, user, timeout=300)
        return user

    def save(self, *args, **kwargs):
        """Override save method to clear cache when user is updated."""
        super().save(*args, **kwargs)
        cache.delete(f"user_email_{self.email}")
        cache.delete(f"user_id_{self.id}")

    def delete(self, *args, **kwargs):
        """Override delete method to clear cache when user is deleted."""
        cache.delete(f"user_email_{self.email}")
        cache.delete(f"user_id_{self.id}")
        super().delete(*args, **kwargs)
