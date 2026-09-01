from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import NotificationStudent, NotificationStaffs

class NotificationAPITests(BaseAPITestCase):

    def test_admin_broadcast_to_all_students(self):
        self.authenticate_as_admin()
        url = reverse('broadcast_students')
        payload = {
            'message': 'Midterm exams will begin on October 15th.',
            'target_type': 'all'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreaterEqual(response.data['recipient_count'], 1)
        self.assertTrue(NotificationStudent.objects.filter(message='Midterm exams will begin on October 15th.').exists())

    def test_admin_broadcast_to_course_students(self):
        self.authenticate_as_admin()
        url = reverse('broadcast_students')
        payload = {
            'message': 'CS department laboratory workshop this Friday.',
            'target_type': 'course',
            'course_id': self.course.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreaterEqual(response.data['recipient_count'], 1)

    def test_admin_broadcast_to_staff(self):
        self.authenticate_as_admin()
        url = reverse('broadcast_staff')
        payload = {
            'message': 'Faculty meeting tomorrow at 10 AM.'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreaterEqual(response.data['recipient_count'], 1)
        self.assertTrue(NotificationStaffs.objects.filter(message='Faculty meeting tomorrow at 10 AM.').exists())

    def test_student_retrieves_notifications(self):
        # 1. Admin sends broadcast
        NotificationStudent.objects.create(student_id=self.student_profile, message='Welcome to the new academic term!')

        # 2. Student views notifications
        self.authenticate_as_student()
        url = reverse('notifications_student')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Welcome to the new academic term!')

    def test_staff_retrieves_notifications(self):
        # 1. Admin sends broadcast
        NotificationStaffs.objects.create(staff_id=self.staff_profile, message='Grade submissions deadline is Friday.')

        # 2. Staff views notifications
        self.authenticate_as_staff()
        url = reverse('notifications_staff')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Grade submissions deadline is Friday.')

    def test_admin_views_history(self):
        self.authenticate_as_admin()
        url = reverse('notifications_admin_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('student_notifications', response.data)
        self.assertIn('staff_notifications', response.data)

    def test_delete_notification(self):
        notif = NotificationStudent.objects.create(student_id=self.student_profile, message='Temporary alert')
        self.authenticate_as_student()
        delete_url = reverse('delete_student_notification', kwargs={'pk': notif.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(NotificationStudent.objects.filter(id=notif.id).exists())
