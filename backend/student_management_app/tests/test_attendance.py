from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import Attendance, AttendanceReport

class AttendanceAPITests(BaseAPITestCase):

    def test_attendance_workflow(self):
        # 1. Staff fetches students for attendance
        self.authenticate_as_staff()
        url = reverse('attendance_get_students')
        response = self.client.get(f"{url}?subject_id={self.subject.id}&session_year_id={self.session_year.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        # 2. Staff saves attendance
        save_url = reverse('attendance_save')
        payload = {
            'subject_id': self.subject.id,
            'session_year_id': self.session_year.id,
            'attendance_date': '2026-09-01',
            'student_ids': [{'id': self.student_profile.id, 'status': 1}]
        }
        save_res = self.client.post(save_url, payload, format='json')
        self.assertEqual(save_res.status_code, status.HTTP_201_CREATED)
        attendance_id = save_res.data['attendance_id']

        # 3. Staff fetches attendance dates
        dates_url = reverse('attendance_get_dates')
        dates_res = self.client.get(f"{dates_url}?subject_id={self.subject.id}&session_year_id={self.session_year.id}")
        self.assertEqual(dates_res.status_code, status.HTTP_200_OK)
        self.assertTrue(any(d['attendance_date'] == '2026-09-01' for d in dates_res.data))

        # 4. Staff fetches attendance reports
        reports_url = reverse('attendance_get_reports')
        reports_res = self.client.get(f"{reports_url}?attendance_id={attendance_id}")
        self.assertEqual(reports_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reports_res.data), 1)
        report_id = reports_res.data[0]['id']

        # 5. Staff updates attendance
        update_url = reverse('attendance_update')
        update_payload = {
            'student_data': [{'id': report_id, 'status': False}]
        }
        update_res = self.client.post(update_url, update_payload, format='json')
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)

        report_obj = AttendanceReport.objects.get(id=report_id)
        self.assertFalse(report_obj.status)

        # 6. Student views attendance
        self.authenticate_as_student()
        view_url = reverse('student_attendance_view')
        view_res = self.client.get(f"{view_url}?subject_id={self.subject.id}")
        self.assertEqual(view_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(view_res.data), 1)
