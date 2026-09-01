from django.core.cache import cache
from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import Courses, Subjects, SessionYearModel

class RedisCachingAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        cache.clear()

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_dashboard_stats_cached_and_invalidated(self):
        self.authenticate_as_admin()
        url = reverse('dashboard_stats')

        # 1. First fetch -> cache miss & populated
        res1 = self.client.get(url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        total_students_initial = res1.data['total_students']

        # 2. Check cache exists in Redis
        cache_key = f"dashboard_stats_admin_{self.admin_user.id}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['total_students'], total_students_initial)

        # 3. Create a student via API -> should invalidate cache
        create_res = self.client.post(reverse('students-list'), {
            'username': 'cachestudent',
            'email': 'cache@test.com',
            'password': 'password123',
            'first_name': 'Cache',
            'last_name': 'Tester',
            'gender': 'Male',
            'address': 'Campus',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id
        }, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)

        # 4. Next fetch returns fresh stats
        res2 = self.client.get(url)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.data['total_students'], total_students_initial + 1)

    def test_courses_catalog_caching_and_invalidation(self):
        self.authenticate_as_admin()
        url = reverse('courses-list')

        # 1. Fetch courses list -> caches
        res1 = self.client.get(url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        initial_count = len(res1.data)

        # Cache key should exist
        cached_courses = cache.get("courses_list")
        self.assertIsNotNone(cached_courses)
        self.assertEqual(len(cached_courses), initial_count)

        # 2. Add course -> invalidates cache
        create_res = self.client.post(url, {'course_name': 'Data Science & AI'}, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)

        # Cache should be cleared or updated
        self.assertIsNone(cache.get("courses_list"))

        # 3. Next list fetch returns new course
        res2 = self.client.get(url)
        self.assertEqual(len(res2.data), initial_count + 1)

    def test_sessions_catalog_caching_and_invalidation(self):
        self.authenticate_as_admin()
        url = reverse('sessions-list')

        res1 = self.client.get(url)
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(cache.get("sessions_list"))

        # Create session
        create_res = self.client.post(url, {
            'session_start_year': '2027-01-01',
            'session_end_year': '2027-12-31'
        }, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(cache.get("sessions_list"))
