from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Subject
from .utilis import BaseTestCase

User = get_user_model()

class SubjectListViewTests(BaseTestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser@mail.com', password='password123')
        cls.subjects = [
            Subject.objects.create(name="English"),
            Subject.objects.create(name="Math"),
            Subject.objects.create(name="Science"),
            Subject.objects.create(name="History")
        ]
        cls.client.force_authenticate(user=cls.user)

    def test_get_subject_list(self):
        url = reverse('subject-list')
        response = self.client.get(url)
        self.log_request_response('GET', url, None, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), len(self.subjects))
            self.assert_passed("test_get_subject_list")
        except AssertionError as e:
            self.assert_failed("test_get_subject_list", e)

class UserSubjectPreferenceViewTests(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser@mail.com', password='password123')
        cls.subjects = [
            Subject.objects.create(name="English"),
            Subject.objects.create(name="Math"),
            Subject.objects.create(name="Science"),
            Subject.objects.create(name="History"),
            Subject.objects.create(name="Geography")
        ]
        cls.client.force_authenticate(user=cls.user)

    def test_set_subject_preferences(self):
        url = reverse('user-subject-preferences')
        data = {'subjects': [sub.name for sub in self.subjects]}
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Subjects selected successfully.')
            self.assert_passed("test_set_subject_preferences")
        except AssertionError as e:
            self.assert_failed("test_set_subject_preferences", e)

    def test_set_invalid_subject_preferences(self):
        url = reverse('user-subject-preferences')
        data = {'subjects': ['Math', 'Science']}  # Invalid preference
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], "You must select exactly 5 subjects, including English.")
            self.assert_passed("test_set_invalid_subject_preferences")
        except AssertionError as e:
            self.assert_failed("test_set_invalid_subject_preferences", e)