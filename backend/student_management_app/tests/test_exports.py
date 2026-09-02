from django.urls import reverse
from rest_framework import status
from student_management_app.models import (
    CustomUser, Courses, Subjects, Students, SessionYearModel,
    StudentResult, Attendance, AttendanceReport,
    FeeStructure, StudentFeeInvoice, FeePayment
)
from .base import BaseAPITestCase
import csv
import io

class ExportReportingAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        # Create subjects and results
        self.subject = Subjects.objects.create(
            subject_name="Advanced Mathematics",
            course_id=self.course,
            staff_id=self.staff_user
        )
        self.result = StudentResult.objects.create(
            student_id=self.student_profile,
            subject_id=self.subject,
            subject_exam_marks=45.0,
            subject_assignment_marks=40.0
        )
        # Create attendance record
        self.attendance = Attendance.objects.create(
            subject_id=self.subject,
            attendance_date="2026-09-01",
            session_year_id=self.session_year
        )
        self.attendance_report = AttendanceReport.objects.create(
            student_id=self.student_profile,
            attendance_id=self.attendance,
            status=True
        )
        # Create Fee Invoice
        self.fee_structure = FeeStructure.objects.create(
            fee_name="Semester 1 Fee",
            course_id=self.course,
            session_year_id=self.session_year,
            tuition_fee=1000.0,
            lab_fee=200.0,
            library_fee=100.0,
            exam_fee=150.0,
            other_fee=50.0,
            due_date="2026-10-01"
        )
        self.invoice = StudentFeeInvoice.objects.create(
            student_id=self.student_profile,
            fee_structure_id=self.fee_structure,
            total_amount=1500.0,
            paid_amount=500.0,
            payment_status='Partial'
        )

        # Another student
        self.student2_user = CustomUser.objects.create_user(
            username='student2_exp', email='s2_exp@test.com', password='password123',
            user_type=3, first_name='Alice', last_name='Smith'
        )
        self.student2 = self.student2_user.students
        self.student2.course_id = self.course
        self.student2.session_year_id = self.session_year
        self.student2.save()

    def test_student_download_own_report_card_pdf(self):
        self.authenticate_as_student()
        url = reverse('export-report-card')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertTrue('attachment;' in res['Content-Disposition'])
        self.assertTrue(res.content.startswith(b'%PDF-'))

    def test_admin_download_any_student_report_card_pdf(self):
        self.authenticate_as_admin()
        url = reverse('export-report-card')
        res = self.client.get(f"{url}?student_id={self.student_profile.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'application/pdf')
        self.assertTrue(res.content.startswith(b'%PDF-'))

    def test_student_cannot_download_other_student_report_card(self):
        self.authenticate_as_student()
        url = reverse('export-report-card')
        # Attempting to fetch student 2's report card as student 1
        res = self.client.get(f"{url}?student_id={self.student2.id}")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_export_attendance_csv(self):
        self.authenticate_as_admin()
        url = reverse('export-attendance-csv')
        res = self.client.get(f"{url}?subject_id={self.subject.id}&session_year_id={self.session_year.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/csv')
        self.assertTrue('attachment;' in res['Content-Disposition'])
        
        # Parse CSV content
        content = res.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertGreater(len(rows), 1) # Header + at least 1 record
        header = rows[0]
        self.assertIn("Student ID", header)
        self.assertIn("Student Name", header)
        self.assertIn("Status", header)

    def test_admin_export_fees_csv(self):
        self.authenticate_as_admin()
        url = reverse('export-fees-csv')
        res = self.client.get(f"{url}?course_id={self.course.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/csv')
        
        content = res.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertGreater(len(rows), 1)
        header = rows[0]
        self.assertIn("Invoice ID", header)
        self.assertIn("Total Amount", header)
        self.assertIn("Paid Amount", header)
        self.assertIn("Balance Due", header)

    def test_admin_export_students_csv(self):
        self.authenticate_as_admin()
        url = reverse('export-students-csv')
        res = self.client.get(f"{url}?course_id={self.course.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/csv')
        
        content = res.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        self.assertGreater(len(rows), 1)
        header = rows[0]
        self.assertIn("Username", header)
        self.assertIn("Full Name", header)
        self.assertIn("Course", header)

    def test_student_cannot_export_admin_reports(self):
        self.authenticate_as_student()
        # Student cannot export fees CSV
        res = self.client.get(reverse('export-fees-csv'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # Student cannot export all students CSV
        res = self.client.get(reverse('export-students-csv'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_export_denied(self):
        self.client.credentials() # Clear auth
        res = self.client.get(reverse('export-report-card'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        res = self.client.get(reverse('export-attendance-csv'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
