from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import Assignment, StudentAssignmentSubmission

class AssignmentAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.future_deadline = (timezone.now() + timedelta(days=7)).isoformat()
        self.past_deadline = (timezone.now() - timedelta(days=2)).isoformat()

    def test_staff_create_assignment_success(self):
        self.authenticate_as_staff()
        url = reverse('assignments-list')
        payload = {
            'subject_id': self.subject.id,
            'session_year_id': self.session_year.id,
            'title': 'Midterm Calculus Project',
            'description': 'Solve calculus problem set chapters 1-4',
            'deadline': self.future_deadline,
            'max_marks': 100.0
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Midterm Calculus Project')
        self.assertEqual(response.data['created_by_username'], self.staff_user.username)
        self.assertTrue(Assignment.objects.filter(title='Midterm Calculus Project').exists())

    def test_student_cannot_create_assignment(self):
        self.authenticate_as_student()
        url = reverse('assignments-list')
        payload = {
            'subject_id': self.subject.id,
            'session_year_id': self.session_year.id,
            'title': 'Illegal Assignment',
            'description': 'Student trying to post assignment',
            'deadline': self.future_deadline,
            'max_marks': 50.0
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_list_assignments_for_enrolled_course(self):
        # Create assignment for student's course subject
        Assignment.objects.create(
            subject_id=self.subject,
            session_year_id=self.session_year,
            title='Physics Lab Report',
            description='Analyze kinematics experiment',
            deadline=timezone.now() + timedelta(days=5),
            max_marks=50.0,
            created_by=self.staff_user
        )

        self.authenticate_as_student()
        url = reverse('assignments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        self.assertEqual(response.data[0]['title'], 'Physics Lab Report')

    def test_student_submit_assignment_on_time(self):
        assignment = Assignment.objects.create(
            subject_id=self.subject,
            session_year_id=self.session_year,
            title='Chemistry Worksheet',
            description='Complete organic chemistry equations',
            deadline=timezone.now() + timedelta(days=3),
            max_marks=100.0,
            created_by=self.staff_user
        )

        self.authenticate_as_student()
        url = reverse('assignments-submit', kwargs={'pk': assignment.id})
        payload = {
            'submission_text': 'Here are my solutions to problems 1 through 10.'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'Submitted')
        self.assertFalse(response.data['is_late'])
        self.assertEqual(response.data['student_name'], f"{self.student_user.first_name} {self.student_user.last_name}")

    def test_student_submit_assignment_late_detection(self):
        assignment = Assignment.objects.create(
            subject_id=self.subject,
            session_year_id=self.session_year,
            title='Overdue Essay',
            description='History essay',
            deadline=timezone.now() - timedelta(days=1), # Past deadline
            max_marks=100.0,
            created_by=self.staff_user
        )

        self.authenticate_as_student()
        url = reverse('assignments-submit', kwargs={'pk': assignment.id})
        payload = {
            'submission_text': 'Late submission of history essay.'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_late'])

    def test_staff_grade_submission_success(self):
        assignment = Assignment.objects.create(
            subject_id=self.subject,
            session_year_id=self.session_year,
            title='Algebra Quiz',
            description='Quiz solutions',
            deadline=timezone.now() + timedelta(days=2),
            max_marks=100.0,
            created_by=self.staff_user
        )
        submission = StudentAssignmentSubmission.objects.create(
            assignment_id=assignment,
            student_id=self.student_profile,
            submission_text='My quiz answers'
        )

        self.authenticate_as_staff()
        url = reverse('assignment-submissions-grade', kwargs={'pk': submission.id})
        payload = {
            'marks_obtained': 92.5,
            'feedback_remarks': 'Excellent proof techniques, minor typo on question 3.'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Graded')
        self.assertEqual(float(response.data['marks_obtained']), 92.5)
        self.assertEqual(response.data['feedback_remarks'], 'Excellent proof techniques, minor typo on question 3.')
        self.assertEqual(response.data['graded_by_username'], self.staff_user.username)

    def test_student_cannot_grade_submission(self):
        assignment = Assignment.objects.create(
            subject_id=self.subject,
            session_year_id=self.session_year,
            title='Biology Homework',
            description='Cell structure review',
            deadline=timezone.now() + timedelta(days=2),
            max_marks=50.0,
            created_by=self.staff_user
        )
        submission = StudentAssignmentSubmission.objects.create(
            assignment_id=assignment,
            student_id=self.student_profile,
            submission_text='Cell biology answers'
        )

        self.authenticate_as_student()
        url = reverse('assignment-submissions-grade', kwargs={'pk': submission.id})
        payload = {
            'marks_obtained': 50.0,
            'feedback_remarks': 'Student attempting to self-grade'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_assignment_access_denied(self):
        url = reverse('assignments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
