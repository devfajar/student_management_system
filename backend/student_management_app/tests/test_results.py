from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import StudentResult

class ResultsAPITests(BaseAPITestCase):

    def test_results_and_grading_workflow(self):
        # 1. Staff fetches students for results
        self.authenticate_as_staff()
        get_students_url = reverse('results_get_students')
        get_res = self.client.get(f"{get_students_url}?subject_id={self.subject.id}&session_year_id={self.session_year.id}")
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(get_res.data), 1)

        # 2. Staff saves student examination & assignment marks
        save_url = reverse('results_save')
        payload = {
            'subject_id': self.subject.id,
            'student_results': [{
                'student_id': self.student_profile.id,
                'assignment_marks': 45.0,
                'exam_marks': 48.0
            }]
        }
        save_res = self.client.post(save_url, payload, format='json')
        self.assertEqual(save_res.status_code, status.HTTP_200_OK)

        result_obj = StudentResult.objects.get(student_id=self.student_profile, subject_id=self.subject)
        self.assertEqual(result_obj.subject_assignment_marks, 45.0)
        self.assertEqual(result_obj.subject_exam_marks, 48.0)

        # 3. Student views their own academic transcript
        self.authenticate_as_student()
        transcript_url = reverse('results_student_view')
        transcript_res = self.client.get(transcript_url)
        self.assertEqual(transcript_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(transcript_res.data['results']), 1)
        first_result = transcript_res.data['results'][0]
        self.assertEqual(first_result['total_marks'], 93.0)
        self.assertEqual(first_result['grade'], 'A+')
        self.assertEqual(first_result['status'], 'Passed')
        self.assertEqual(transcript_res.data['summary']['passed_subjects'], 1)
        self.assertEqual(transcript_res.data['summary']['average_score'], 93.0)

        # 4. Admin audits and lists results
        self.authenticate_as_admin()
        list_url = reverse('results-list')
        list_res = self.client.get(list_url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data), 1)

        # 5. Admin deletes result
        delete_url = reverse('results-detail', kwargs={'pk': result_obj.id})
        delete_res = self.client.delete(delete_url)
        self.assertEqual(delete_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StudentResult.objects.filter(id=result_obj.id).exists())
