import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import Students, Subjects

class MediaUploadAPITests(BaseAPITestCase):

    def generate_test_image(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0, 0))
        image.save(file, 'png')
        file.name = 'test_avatar.png'
        file.seek(0)
        return SimpleUploadedFile(file.name, file.read(), content_type='image/png')

    def test_student_avatar_upload(self):
        self.authenticate_as_student()
        url = reverse('current_user')
        avatar = self.generate_test_image()

        res = self.client.put(url, {
            'profile_pic': avatar,
            'address': 'New Dorm 4B'
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Verify student model updated
        self.student_profile.refresh_from_db()
        self.assertTrue(bool(self.student_profile.profile_pic))
        self.assertEqual(self.student_profile.address, 'New Dorm 4B')

    def test_subject_syllabus_upload(self):
        self.authenticate_as_admin()
        url = reverse('subjects-list')
        pdf_file = SimpleUploadedFile("syllabus.pdf", b"%PDF-1.4 test syllabus content", content_type="application/pdf")

        res = self.client.post(url, {
            'subject_name': 'Advanced Quantum Mechanics',
            'course_id': self.course.id,
            'staff_id': self.staff_user.id,
            'syllabus_file': pdf_file
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('syllabus_file', res.data)
        self.assertIsNotNone(res.data['syllabus_file'])
