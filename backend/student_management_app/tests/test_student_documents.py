import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import Students, CustomUser

class StudentDocumentsAndProfilePicAPITests(BaseAPITestCase):

    def generate_test_image(self, name="avatar.png"):
        file = io.BytesIO()
        image = Image.new('RGB', size=(60, 60), color=(10, 100, 200))
        image.save(file, 'png')
        file.name = name
        file.seek(0)
        return SimpleUploadedFile(file.name, file.read(), content_type='image/png')

    def generate_test_pdf(self, name="doc.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 mock pdf content", content_type="application/pdf")

    def test_student_can_upload_document(self):
        self.authenticate_as_student()
        url = reverse('student-documents-list')
        pdf = self.generate_test_pdf("highschool_transcript.pdf")

        res = self.client.post(url, {
            'document_name': 'High School Transcript',
            'document_type': 'transcript',
            'document_file': pdf
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['document_name'], 'High School Transcript')
        self.assertEqual(res.data['document_type'], 'transcript')
        self.assertEqual(res.data['verification_status'], 0) # 0 = Pending
        self.assertIsNotNone(res.data['document_file'])

    def test_student_can_only_view_own_documents(self):
        # Create doc for current student
        self.authenticate_as_student()
        url = reverse('student-documents-list')
        pdf1 = self.generate_test_pdf("student1_id.pdf")
        self.client.post(url, {
            'document_name': 'National ID Card',
            'document_type': 'id_card',
            'document_file': pdf1
        }, format='multipart')

        # Create student 2 and their doc
        student2_user = CustomUser.objects.create_user(
            username='student2', email='s2@test.com', password='password123',
            user_type=3, first_name='Other', last_name='Student'
        )
        student2 = student2_user.students
        student2.course_id = self.course
        student2.session_year_id = self.session_year
        student2.save()


        # Authenticate as student 2
        token_res = self.client.post(reverse('token_obtain_pair'), {'username': 'student2', 'password': 'password123'}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_res.data['access']}")


        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0) # Student 2 has no documents yet

    def test_student_can_delete_own_pending_document(self):
        self.authenticate_as_student()
        url = reverse('student-documents-list')
        pdf = self.generate_test_pdf("cert.pdf")
        create_res = self.client.post(url, {
            'document_name': 'Birth Certificate',
            'document_type': 'certificate',
            'document_file': pdf
        }, format='multipart')
        doc_id = create_res.data['id']

        del_res = self.client.delete(reverse('student-documents-detail', kwargs={'pk': doc_id}))
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_list_and_verify_documents(self):
        # Student uploads doc
        self.authenticate_as_student()
        pdf = self.generate_test_pdf("diploma.pdf")
        create_res = self.client.post(reverse('student-documents-list'), {
            'document_name': 'Diploma',
            'document_type': 'certificate',
            'document_file': pdf
        }, format='multipart')
        doc_id = create_res.data['id']

        # Admin logs in and approves
        self.authenticate_as_admin()
        list_res = self.client.get(reverse('student-documents-list'))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data), 1)

        # Approve document
        verify_url = reverse('student-documents-verify', kwargs={'pk': doc_id})
        approve_res = self.client.post(verify_url, {
            'verification_status': 1, # Approved
            'rejection_reason': ''
        }, format='json')
        self.assertEqual(approve_res.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_res.data['verification_status'], 1)

    def test_admin_can_reject_document_with_reason(self):
        self.authenticate_as_student()
        pdf = self.generate_test_pdf("blurry_id.pdf")
        create_res = self.client.post(reverse('student-documents-list'), {
            'document_name': 'Blurry ID',
            'document_type': 'id_card',
            'document_file': pdf
        }, format='multipart')
        doc_id = create_res.data['id']

        # Admin rejects
        self.authenticate_as_admin()
        verify_url = reverse('student-documents-verify', kwargs={'pk': doc_id})
        reject_res = self.client.post(verify_url, {
            'verification_status': 2, # Rejected
            'rejection_reason': 'Document is blurry and unreadable. Please re-upload a clean scan.'
        }, format='json')
        self.assertEqual(reject_res.status_code, status.HTTP_200_OK)
        self.assertEqual(reject_res.data['verification_status'], 2)
        self.assertEqual(reject_res.data['rejection_reason'], 'Document is blurry and unreadable. Please re-upload a clean scan.')

    def test_student_cannot_verify_documents(self):
        self.authenticate_as_student()
        pdf = self.generate_test_pdf("doc.pdf")
        create_res = self.client.post(reverse('student-documents-list'), {
            'document_name': 'Passport',
            'document_type': 'id_card',
            'document_file': pdf
        }, format='multipart')
        doc_id = create_res.data['id']

        # Student tries to verify -> 403 Forbidden
        verify_url = reverse('student-documents-verify', kwargs={'pk': doc_id})
        res = self.client.post(verify_url, {'verification_status': 1}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_create_with_avatar_by_admin(self):
        self.authenticate_as_admin()
        avatar = self.generate_test_image("student_avatar.png")
        url = reverse('students-list')

        res = self.client.post(url, {
            'username': 'newavatarstudent',
            'email': 'avatarstudent@test.com',
            'password': 'password123',
            'first_name': 'Avatar',
            'last_name': 'Student',
            'gender': 'Male',
            'address': 'Main Hall',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'profile_pic': avatar
        }, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('profile_pic', res.data)
        self.assertIsNotNone(res.data['profile_pic'])
