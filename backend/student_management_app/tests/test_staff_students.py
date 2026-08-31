from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import CustomUser, Staffs, Students

class StaffStudentAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.authenticate_as_admin()

    def test_list_staff(self):
        url = reverse('staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_staff(self):
        url = reverse('staff-list')
        payload = {
            'username': 'new_staff_member',
            'email': 'newstaff@school.edu',
            'password': 'password123',
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'address': 'Faculty Block A'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username='new_staff_member').exists())

    def test_update_staff(self):
        url = reverse('staff-detail', kwargs={'pk': self.staff_profile.id})
        payload = {
            'first_name': 'UpdatedFirst',
            'address': 'New Residence 502'
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.staff_profile.refresh_from_db()
        self.assertEqual(self.staff_profile.address, 'New Residence 502')

    def test_list_students(self):
        url = reverse('students-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_student(self):
        url = reverse('students-list')
        payload = {
            'username': 'alice_student',
            'email': 'alice@school.edu',
            'password': 'password123',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'gender': 'Female',
            'address': 'Dormitory C, Room 12',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(username='alice_student').exists())

    def test_update_student(self):
        url = reverse('students-detail', kwargs={'pk': self.student_profile.id})
        payload = {
            'first_name': 'Johnny',
            'address': 'Campus Villa 9'
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.address, 'Campus Villa 9')
