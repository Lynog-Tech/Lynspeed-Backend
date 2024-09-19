from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Subject, TestSession, Question, Worksheet, TestSessionQuestion, UserResponse, Result, UserSubjectPreference
from .utilis import BaseTestCase

User = get_user_model()

class StartTestSessionViewTests(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser@mail.com', password='password123')
        cls.english = Subject.objects.create(name="English")
        cls.math = Subject.objects.create(name="Math")
        cls.science = Subject.objects.create(name="Science")
        cls.history = Subject.objects.create(name="History")
        cls.geography = Subject.objects.create(name="Geography")
        UserSubjectPreference.objects.create(user=cls.user, selected_subjects=[cls.english, cls.math, cls.science, cls.history, cls.geography])
        cls.client.force_authenticate(user=cls.user)

    def test_start_test_session(self):
        url = reverse('start-test-session')
        data = {'subjects': ['English', 'Math', 'Science', 'History']}
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(len(response.data['subjects']), 4)
            self.assertIn('assigned_question_ids', response.data)
            self.assert_passed("test_start_test_session")
        except AssertionError as e:
            self.assert_failed("test_start_test_session", e)

    def test_start_test_session_invalid_subjects(self):
        url = reverse('start-test-session')
        data = {'subjects': ['Math', 'Science']}  # Missing English
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], "You must select exactly 4 subjects, including English.")
            self.assert_passed("test_start_test_session_invalid_subjects")
        except AssertionError as e:
            self.assert_failed("test_start_test_session_invalid_subjects", e)

class SubmitTestSessionViewTests(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser@mail.com', password='password123')
        cls.english = Subject.objects.create(name="English")
        cls.math = Subject.objects.create(name="Math")
        cls.science = Subject.objects.create(name="Science")
        cls.test_session = TestSession.objects.create(user=cls.user)
        cls.test_session.subjects.add(cls.english, cls.math, cls.science)
        cls.worksheet = Worksheet.objects.create(subject=cls.english, name="Worksheet 1")
        cls.question = Question.objects.create(worksheet=cls.worksheet, text="What is 2+2?", correct_option='A')
        TestSessionQuestion.objects.create(test_session=cls.test_session, question=cls.question)
        cls.client.force_authenticate(user=cls.user)

    def test_submit_test_session(self):
        url = reverse('submit-test-session')
        data = {
            'test_session_id': self.test_session.id,
            'responses': [{'question_id': self.question.id, 'selected_option': 'A'}]
        }
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(UserResponse.objects.filter(test_session=self.test_session, question=self.question).exists())
            self.assert_passed("test_submit_test_session")
        except AssertionError as e:
            self.assert_failed("test_submit_test_session", e)

    def test_submit_test_session_invalid_id(self):
        url = reverse('submit-test-session')
        data = {
            'test_session_id': 999,  # Invalid session ID
            'responses': [{'question_id': self.question.id, 'selected_option': 'A'}]
        }
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], 'No TestSession matches the given query.')
            self.assert_passed("test_submit_test_session_invalid_id")
        except AssertionError as e:
            self.assert_failed("test_submit_test_session_invalid_id", e)

    def test_submit_test_session_missing_responses(self):
        url = reverse('submit-test-session')
        data = {
            'test_session_id': self.test_session.id,
            'responses': []  # No responses
        }
        response = self.client.post(url, data, format='json')
        self.log_request_response('POST', url, data, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assert_passed("test_submit_test_session_missing_responses")
        except AssertionError as e:
            self.assert_failed("test_submit_test_session_missing_responses", e)

class ViewTestSessionResultsViewTests(BaseTestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email='testuser@mail.com', password='password123')
        cls.english = Subject.objects.create(name="English")
        cls.test_session = TestSession.objects.create(user=cls.user, completed=True)
        cls.result = Result.objects.create(
            user=cls.user,
            subject=cls.english,
            worksheet=Worksheet.objects.create(subject=cls.english, name="Worksheet 1"),
            score=80,
            speed=30,
            test_session=cls.test_session
        )
        cls.client.force_authenticate(user=cls.user)

    def test_view_test_session_results(self):
        url = reverse('view-test-session-results', kwargs={'session_id': self.test_session.id})
        response = self.client.get(url)
        self.log_request_response('GET', url, None, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), 1)
            self.assert_passed("test_view_test_session_results")
        except AssertionError as e:
            self.assert_failed("test_view_test_session_results", e)

    def test_view_test_session_results_incomplete_session(self):
        incomplete_session = TestSession.objects.create(user=self.user, completed=False)
        url = reverse('view-test-session-results', kwargs={'session_id': incomplete_session.id})
        response = self.client.get(url)
        self.log_request_response('GET', url, None, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], "Test session is not yet completed.")
            self.assert_passed("test_view_test_session_results_incomplete_session")
        except AssertionError as e:
            self.assert_failed("test_view_test_session_results_incomplete_session", e)

    def test_view_test_session_results_invalid_id(self):
        url = reverse('view-test-session-results', kwargs={'session_id': 999})  # Invalid ID
        response = self.client.get(url)
        self.log_request_response('GET', url, None, response)

        try:
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assert_passed("test_view_test_session_results_invalid_id")
        except AssertionError as e:
            self.assert_failed("test_view_test_session_results_invalid_id", e)
