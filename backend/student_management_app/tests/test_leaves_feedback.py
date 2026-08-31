from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import (
    LeaveReportStudent, LeaveReportStaff, FeedBackStudent, FeedBackStaffs
)

class LeavesFeedbackAPITests(BaseAPITestCase):

    def test_student_apply_leave_and_admin_approve(self):
        # 1. Student applies for leave
        self.authenticate_as_student()
        url = reverse('student-leaves-list')
        payload = {
            'leave_date': '2026-09-15',
            'leave_message': 'Attending family event'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        leave_id = response.data['id']

        # 2. Admin approves leave
        self.authenticate_as_admin()
        approve_url = reverse('student-leaves-approve', kwargs={'pk': leave_id})
        approve_res = self.client.post(approve_url)
        self.assertEqual(approve_res.status_code, status.HTTP_200_OK)

        leave_obj = LeaveReportStudent.objects.get(id=leave_id)
        self.assertEqual(leave_obj.leave_status, 1)

    def test_staff_apply_leave_and_admin_disapprove(self):
        # 1. Staff applies for leave
        self.authenticate_as_staff()
        url = reverse('staff-leaves-list')
        payload = {
            'leave_date': '2026-10-01',
            'leave_message': 'Medical appointment'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        leave_id = response.data['id']

        # 2. Admin disapproves leave
        self.authenticate_as_admin()
        disapprove_url = reverse('staff-leaves-disapprove', kwargs={'pk': leave_id})
        disapprove_res = self.client.post(disapprove_url)
        self.assertEqual(disapprove_res.status_code, status.HTTP_200_OK)

        leave_obj = LeaveReportStaff.objects.get(id=leave_id)
        self.assertEqual(leave_obj.leave_status, 2)

    def test_student_feedback_and_admin_reply(self):
        # 1. Student sends feedback
        self.authenticate_as_student()
        url = reverse('student-feedback-list')
        response = self.client.post(url, {'feedback': 'Library AC needs repair'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        feedback_id = response.data['id']

        # 2. Admin replies
        self.authenticate_as_admin()
        reply_url = reverse('student-feedback-reply', kwargs={'pk': feedback_id})
        reply_res = self.client.post(reply_url, {'feedback_reply': 'Fixed by maintenance team'}, format='json')
        self.assertEqual(reply_res.status_code, status.HTTP_200_OK)

        fb_obj = FeedBackStudent.objects.get(id=feedback_id)
        self.assertEqual(fb_obj.feedback_reply, 'Fixed by maintenance team')

    def test_staff_feedback_and_admin_reply(self):
        # 1. Staff sends feedback
        self.authenticate_as_staff()
        url = reverse('staff-feedback-list')
        response = self.client.post(url, {'feedback': 'Request for new projector in lab 2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        feedback_id = response.data['id']

        # 2. Admin replies
        self.authenticate_as_admin()
        reply_url = reverse('staff-feedback-reply', kwargs={'pk': feedback_id})
        reply_res = self.client.post(reply_url, {'feedback_reply': 'New projector ordered'}, format='json')
        self.assertEqual(reply_res.status_code, status.HTTP_200_OK)

        fb_obj = FeedBackStaffs.objects.get(id=feedback_id)
        self.assertEqual(fb_obj.feedback_reply, 'New projector ordered')
