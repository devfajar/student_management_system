from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import Courses, Subjects, SessionYearModel

class CourseSubjectSessionAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.authenticate_as_admin()

    def test_list_courses(self):
        url = reverse('courses-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_course(self):
        url = reverse('courses-list')
        response = self.client.post(url, {'course_name': 'Mechanical Engineering'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Courses.objects.filter(course_name='Mechanical Engineering').exists())

    def test_update_course(self):
        url = reverse('courses-detail', kwargs={'pk': self.course.id})
        response = self.client.put(url, {'course_name': 'CS & AI'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.course_name, 'CS & AI')

    def test_delete_course(self):
        course = Courses.objects.create(course_name='Temporary Course')
        url = reverse('courses-detail', kwargs={'pk': course.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Courses.objects.filter(id=course.id).exists())

    def test_list_subjects(self):
        url = reverse('subjects-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_subject(self):
        url = reverse('subjects-list')
        payload = {
            'subject_name': 'Algorithms & Complexity',
            'course_id': self.course.id,
            'staff_id': self.staff_user.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Subjects.objects.filter(subject_name='Algorithms & Complexity').exists())

    def test_list_sessions(self):
        url = reverse('sessions-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_session(self):
        url = reverse('sessions-list')
        payload = {
            'session_start_year': '2027-01-01',
            'session_end_year': '2027-12-31'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SessionYearModel.objects.filter(session_start_year='2027-01-01').exists())
