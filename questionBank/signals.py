from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Subject,Worksheet, Question, Result


@receiver(post_save, sender=Result)
def invalidate_test_result_cache(sender, instance, **kwargs):
    cache.delete(f'test_results_user_{instance.user_id}_session_{instance.test_session_id}')



@receiver(post_save, sender=Subject)
@receiver(post_save, sender=Worksheet)
@receiver(post_save, sender=Question)
@receiver(post_delete, sender=Subject)
@receiver(post_delete, sender=Worksheet)
@receiver(post_delete, sender=Question)
def invalidate_cache(sender, **kwargs):
    """
    Clear the cache when a Subject, Worksheet, or Question is saved or deleted.
    """
    cache.clear()
