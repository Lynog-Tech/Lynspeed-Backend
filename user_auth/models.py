from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    '''
    Custom user model extanding the default Abstractuser
    '''
    full_name = models.CharField(max_length=255)
    is_trial = models.BooleanField(default=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    
    def set_trial_end_date(self):
        ''' Sets the trial end day to one day from the current time'''
        self.trial_end_date = timezone.now() + timezone.timedelta(days=1)
        self.save()