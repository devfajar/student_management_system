from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase

class DashboardAPITests(BaseAPITestCase):

    def test_admin_dashboard_stats(self):
        self.authenticate_as_admin()
        url = reverse('dashboard_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_type'], '1')
        self.assertIn('student_count', response.data)
        self.assertIn('staff_count', response.data)
        self.assertIn('course_count', response.data)
        self.assertIn('subject_count', response.data)

    def test_staff_dashboard_stats(self):
        self.authenticate_as_staff()
        url = reverse('dashboard_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_type'], '2')
        self.assertIn('subject_count', response.data)
        self.assertIn('attendance_count', response.data)
        self.assertIn('total_leave', response.data)

    def test_student_dashboard_stats(self):
        self.authenticate_as_student()
        url = reverse('dashboard_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_type'], '3')
        self.assertIn('total_attendance', response.data)
        self.assertIn('attendance_present', response.data)
        self.assertIn('attendance_absent', response.data)

    def test_unauthenticated_dashboard_stats(self):
        url = reverse('dashboard_stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
