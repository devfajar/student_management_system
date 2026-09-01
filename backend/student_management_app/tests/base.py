from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from student_management_app.models import (
    CustomUser, Admins, Staffs, Students, Courses, Subjects, SessionYearModel
)

class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create Session Year
        self.session_year = SessionYearModel.objects.create(
            session_start_year='2026-01-01',
            session_end_year='2026-12-31'
        )

        # Create Course
        self.course = Courses.objects.create(course_name='Computer Science')

        # Create Admin User (user_type=1)
        self.admin_user = CustomUser.objects.create_superuser(
            username='test_admin',
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            last_name='User',
            user_type='1'
        )
        self.admin_profile, _ = Admins.objects.get_or_create(admin=self.admin_user)

        # Create Staff User (user_type=2)
        self.staff_user = CustomUser.objects.create_user(
            username='test_staff',
            email='staff@test.com',
            password='password123',
            first_name='Staff',
            last_name='Instructor',
            user_type='2'
        )
        self.staff_profile, _ = Staffs.objects.get_or_create(
            admin=self.staff_user,
            defaults={'address': 'Staff Residence 101'}
        )

        # Create Subject taught by Staff
        self.subject = Subjects.objects.create(
            subject_name='Data Structures',
            course_id=self.course,
            staff_id=self.staff_user
        )

        # Create Student User (user_type=3)
        self.student_user = CustomUser.objects.create_user(
            username='test_student',
            email='student@test.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            user_type='3'
        )
        self.student_profile, _ = Students.objects.get_or_create(
            admin=self.student_user,
            defaults={
                'gender': 'Male',
                'address': 'Dormitory B',
                'course_id': self.course,
                'session_year_id': self.session_year
            }
        )

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate_as_admin(self):
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def authenticate_as_staff(self):
        token = self.get_jwt_token(self.staff_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def authenticate_as_student(self):
        token = self.get_jwt_token(self.student_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
