from django.core.cache import cache
import json
from .models import Subject, TestSession, Result, Worksheet

CACHE_TTL = 60 * 15  # 15 minutes

def get_cached_subjects():
    cache_key = 'all_subjects'
    subjects = cache.get(cache_key)
    if not subjects:
        subjects = Subject.objects.all()
        cache.set(cache_key, subjects, timeout=CACHE_TTL)
    return subjects

def get_cached_worksheets(subject_id):
    cache_key = f'worksheets_{subject_id}'
    worksheets = cache.get(cache_key)
    if not worksheets:
        worksheets = list(Worksheet.objects.filter(subject_id=subject_id))
        cache.set(cache_key, worksheets, CACHE_TTL)
    return worksheets

def get_cached_test_questions(test_session_id):
    cache_key = f'test_questions_{test_session_id}'
    questions = cache.get(cache_key)
    if not questions:
        test_session = TestSession.objects.get(id=test_session_id)
        questions = test_session.generate_questions()
        cache.set(cache_key, questions, timeout=CACHE_TTL)
    return questions

def get_cached_test_results(user_id, test_session_id):
    # Retrieve cached data as JSON string and parse it
    cache_key = f"test_results_user_{user_id}_session_{test_session_id}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return json.loads(cached_data)
    return None

def cache_test_results(user_id, test_session_id, result_data):
    # Cache serialized data as a JSON string
    cache_key = f"test_results_user_{user_id}_session_{test_session_id}"
    cache.set(cache_key, json.dumps(result_data))
