from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase

class AuthAPITests(BaseAPITestCase):

    def test_login_with_username_success(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'test_admin',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'test_admin')
        self.assertEqual(response.data['user']['user_type'], '1')

    def test_login_with_email_success(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'admin@test.com',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_with_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'test_admin',
            'password': 'wrongpassword'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        refresh_token = self.client.post(reverse('token_obtain_pair'), {
            'username': 'test_admin',
            'password': 'password123'
        }, format='json').data['refresh']

        url = reverse('token_refresh')
        response = self.client.post(url, {'refresh': refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_get_current_user_authenticated(self):
        self.authenticate_as_admin()
        url = reverse('current_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test_admin')
        self.assertEqual(response.data['email'], 'admin@test.com')

    def test_get_current_user_unauthenticated(self):
        url = reverse('current_user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile(self):
        self.authenticate_as_staff()
        url = reverse('current_user')
        payload = {
            'first_name': 'UpdatedStaff',
            'last_name': 'Teacher',
            'address': 'New Campus Tower 4'
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.staff_user.refresh_from_db()
        self.staff_profile.refresh_from_db()
        self.assertEqual(self.staff_user.first_name, 'UpdatedStaff')
        self.assertEqual(self.staff_profile.address, 'New Campus Tower 4')
