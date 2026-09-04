from django.test import TestCase
from django.core.management import call_command
from student_management_app.models import (
    CustomUser, Admins, Staffs, Students, Courses, Subjects, SessionYearModel,
    FeeStructure, StudentFeeInvoice, Assignment, StudentAssignmentSubmission,
    StaffSalary, StaffPayroll, Attendance, AttendanceReport, NotificationStudent
)

class DemoDataSeederTestCase(TestCase):
    def test_seeder_creates_all_demo_entities(self):
        """Management command seed_demo_data creates complete school ecosystem."""
        call_command('seed_demo_data')

        # Admin Verification
        admin_user = CustomUser.objects.filter(username='admin', user_type='1').first()
        self.assertIsNotNone(admin_user)
        self.assertTrue(admin_user.check_password('admin123'))
        self.assertTrue(Admins.objects.filter(admin=admin_user).exists())

        # Faculty Staff Verification
        staff_count = Staffs.objects.count()
        self.assertGreaterEqual(staff_count, 3)
        self.assertTrue(StaffSalary.objects.filter(staff__admin__username='prof_smith').exists())

        # Academic Courses, Subjects & Sessions
        self.assertGreaterEqual(Courses.objects.count(), 3)
        self.assertGreaterEqual(Subjects.objects.count(), 4)
        self.assertGreaterEqual(SessionYearModel.objects.count(), 2)

        # Students Verification
        student_count = Students.objects.count()
        self.assertGreaterEqual(student_count, 5)
        alex = CustomUser.objects.filter(username='student_alex').first()
        self.assertIsNotNone(alex)
        self.assertTrue(alex.check_password('student123'))

        # Fee Invoices
        self.assertGreaterEqual(FeeStructure.objects.count(), 1)
        self.assertGreaterEqual(StudentFeeInvoice.objects.count(), 3)

        # Coursework Assignments & Submissions
        self.assertGreaterEqual(Assignment.objects.count(), 2)
        self.assertGreaterEqual(StudentAssignmentSubmission.objects.count(), 2)

        # Staff Payroll
        self.assertGreaterEqual(StaffPayroll.objects.count(), 3)

        # Attendance & Notifications
        self.assertGreaterEqual(Attendance.objects.count(), 1)
        self.assertGreaterEqual(AttendanceReport.objects.count(), 1)
        self.assertGreaterEqual(NotificationStudent.objects.count(), 1)

    def test_seeder_is_idempotent(self):
        """Calling seed_demo_data multiple times does not duplicate or fail."""
        call_command('seed_demo_data')
        first_staff_count = Staffs.objects.count()
        first_student_count = Students.objects.count()
        first_course_count = Courses.objects.count()

        # Run again
        call_command('seed_demo_data')
        self.assertEqual(Staffs.objects.count(), first_staff_count)
        self.assertEqual(Students.objects.count(), first_student_count)
        self.assertEqual(Courses.objects.count(), first_course_count)
