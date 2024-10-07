from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth import get_user_model
from .models import Subject, PerformanceRecord, PerformanceAnalysis, PerformanceChart

User = get_user_model()

class PerformanceRecordTestCase(APITestCase):
    def setUp(self):
        # Set up a test user and subject
        self.user = User.objects.create_user(email='testuser@mail.com', password='password123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a subject
        self.subject = Subject.objects.create(name='Mathematics')

        # Create performance records
        self.performance_record = PerformanceRecord.objects.create(
            user=self.user,
            subject=self.subject,
            score=85.0,
            speed=120.0,
        )

        self.performance_analysis = PerformanceAnalysis.objects.create(
            user=self.user,
            subject=self.subject,
            average_score=85.0,
            average_speed=120.0,
        )

        self.performance_chart = PerformanceChart.objects.create(
            user=self.user,
            subject=self.subject,
            chart_data={"scores": [85], "dates": ["2024-10-06"], "speeds": [120]}
        )

   # Test creating a performance record
    def test_create_performance_record(self):
        url = reverse('performance-records')
        data = {
            'subject': {'name': 'Physics'},
            'score': 90.0,
            'speed': 100.0,
            'user': self.user.id
        }
        response = self.client.post(url, data, format='json')

        # Print debugging information if the test fails
        if response.status_code != status.HTTP_201_CREATED:
            print("Test Failed:")
            print("Response Status Code:", response.status_code)
            print("Response Content:", response.content.decode('utf-8'))  # Decode the response content for easier readability

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PerformanceRecord.objects.count(), 2)


    # Test listing performance records for the authenticated user
    def test_list_performance_records(self):
        url = reverse('performance-records')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['score'], 85.0)

    # Test retrieving a single performance record
    def test_retrieve_performance_record(self):
        url = reverse('performance-record-detail', args=[self.performance_record.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['score'], 85.0)

    # Test updating a performance record
    def test_update_performance_record(self):
        url = reverse('performance-record-detail', args=[self.performance_record.id])
        data = {'score': 88.0}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.performance_record.refresh_from_db()
        self.assertEqual(self.performance_record.score, 88.0)

    # Test deleting a performance record
    def test_delete_performance_record(self):
        url = reverse('performance-record-detail', args=[self.performance_record.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PerformanceRecord.objects.count(), 0)

    # Test listing performance analysis
    def test_list_performance_analysis(self):
        url = reverse('performance-analysis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['average_score'], 85.0)

    # Test retrieving performance chart data
    def test_retrieve_performance_chart(self):
        url = reverse('performance-chart', args=[self.performance_chart.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('scores', response.data['chart_data'])
        self.assertIn('dates', response.data['chart_data'])
