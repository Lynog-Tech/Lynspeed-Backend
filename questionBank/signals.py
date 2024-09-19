from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Subject, Option, Result

@receiver([post_save, post_delete], sender=Subject)
def invalidate_subject_cache(sender, **kwargs):
    cache.delete('all_subjects')

@receiver([post_save, post_delete], sender=Option)
def invalidate_option_cache(sender, instance, **kwargs):
    cache.delete(f'options_for_question_{instance.question_id}')

@receiver(post_save, sender=Result)
def invalidate_test_result_cache(sender, instance, **kwargs):
    cache.delete(f'test_results_user_{instance.user_id}_session_{instance.test_session_id}')



# from django.urls import reverse
# from rest_framework.authtoken.models import Token
# from rest_framework import status
# from rest_framework.test import APITestCase, APIClient
# from django.contrib.auth import get_user_model
# from .models import Subject, Worksheet, Question

# import logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# class TestViews(APITestCase):

#     def setUp(self):
#         User = get_user_model()
#         self.user = User.objects.create_user(
#             email='testuser@example.com',
#             password='testpass',
#             is_active=True  # Ensure the user is active
#         )
        
#         self.token = Token.objects.create(user=self.user)

#         self.subject_english = Subject.objects.create(name="English")
#         self.subject_math = Subject.objects.create(name="Mathematics")
#         self.subject_science = Subject.objects.create(name="Science")
#         self.subject_history = Subject.objects.create(name="History")

#         self.worksheet_english = Worksheet.objects.create(subject=self.subject_english, name="English Worksheet")
#         self.worksheet_math = Worksheet.objects.create(subject=self.subject_math, name="Math Worksheet")
#         self.question1 = Question.objects.create(worksheet=self.worksheet_english, text="Question 1")
#         self.question2 = Question.objects.create(worksheet=self.worksheet_math, text="Question 2")

#         self.client = APIClient()
#         self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
#     def log_response(self, response, description=""):
#         logger.info(f"{description} Response status code: {response.status_code}")
#         logger.info(f"{description} Response content: {response.content}")

#     def test_subject_list_view(self):
#         url = reverse('subject-list')
#         response = self.client.get(url)
#         self.log_response(response, "Subject List View")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("English", [subject['name'] for subject in response.data])

#     def test_start_test_session(self):
#         url = reverse('start-test-session')
#         data = {"subjects": ["English", "Mathematics", "Science", "History"]}
#         response = self.client.post(url, data, format='json')
#         self.log_response(response, "Start Test Session")
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertIn('assigned_question_ids', response.data)
#         self.assertGreater(len(response.data['assigned_question_ids']), 0)

#     def test_start_test_session_without_english(self):
#         url = reverse('start-test-session')
#         data = {"subjects": ["Mathematics", "Science", "History"]}
#         response = self.client.post(url, data, format='json')
#         self.log_response(response, "Start Test Session without English")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_submit_test_session(self):
#         start_url = reverse('start-test-session')
#         data = {"subjects": ["English", "Mathematics", "Science", "History"]}
#         start_response = self.client.post(start_url, data, format='json')
#         self.log_response(start_response, "Submit Test Session - Start")
#         test_session_id = start_response.data['test_session_id']

#         submit_url = reverse('submit-test-session')
#         submit_data = {
#             "test_session_id": test_session_id,
#             "responses": [
#                 {"question_id": self.question1.id, "selected_option": "A"},
#                 {"question_id": self.question2.id, "selected_option": "B"}
#             ]
#         }
#         response = self.client.post(submit_url, submit_data, format='json')
#         self.log_response(response, "Submit Test Session - Finalize")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     def test_view_test_session_results(self):
#         start_url = reverse('start-test-session')
#         data = {"subjects": ["English", "Mathematics", "Science", "History"]}
#         start_response = self.client.post(start_url, data, format='json')
#         self.log_response(start_response, "View Test Session Results - Start")
#         test_session_id = start_response.data['test_session_id']

#         submit_url = reverse('submit-test-session')
#         submit_data = {
#             "test_session_id": test_session_id,
#             "responses": [
#                 {"question_id": self.question1.id, "selected_option": "A"},
#                 {"question_id": self.question2.id, "selected_option": "B"}
#             ]
#         }
#         self.client.post(submit_url, submit_data, format='json')

#         result_url = reverse('test-session-results')
#         response = self.client.get(f"{result_url}?test_session_id={test_session_id}")
#         self.log_response(response, "View Test Session Results - Result")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # Add assertions based on your actual response structure