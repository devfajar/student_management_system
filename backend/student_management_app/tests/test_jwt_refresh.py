from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase

class JWTRefreshAPITests(BaseAPITestCase):

    def test_login_returns_access_and_refresh_tokens(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {
            'username': 'test_admin',
            'password': 'password123'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(len(response.data['access']) > 20)
        self.assertTrue(len(response.data['refresh']) > 20)

    def test_token_refresh_produces_valid_new_access_token(self):
        login_res = self.client.post(reverse('token_obtain_pair'), {
            'username': 'test_student',
            'password': 'password123'
        }, format='json')
        refresh_token = login_res.data['refresh']

        url = reverse('token_refresh')
        refresh_res = self.client.post(url, {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_res.data)

        # Verify new access token can access protected endpoint
        new_access = refresh_res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access}')
        me_res = self.client.get(reverse('current_user'))
        self.assertEqual(me_res.status_code, status.HTTP_200_OK)
        self.assertEqual(me_res.data['username'], 'test_student')

    def test_token_refresh_with_invalid_token_rejected(self):
        url = reverse('token_refresh')
        response = self.client.post(url, {'refresh': 'invalid.malformed.jwttoken'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_with_missing_payload_rejected(self):
        url = reverse('token_refresh')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_or_tampered_token_cannot_access_api(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered')
        response = self.client.get(reverse('current_user'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
