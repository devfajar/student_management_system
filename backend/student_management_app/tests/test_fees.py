from rest_framework import status
from django.urls import reverse
from student_management_app.tests.base import BaseAPITestCase
from student_management_app.models import (
    CustomUser, Students, Courses, SessionYearModel
)

class FeeAPITests(BaseAPITestCase):

    def setUp(self):
        super().setUp()

        # Additional student in same course for bulk testing
        self.student2_user = CustomUser.objects.create_user(
            username='student2',
            email='student2@test.com',
            password='password123',
            first_name='Jane',
            last_name='Smith',
            user_type='3'
        )
        self.student2_profile, _ = Students.objects.get_or_create(
            admin=self.student2_user,
            defaults={
                'gender': 'Female',
                'address': 'Dormitory A',
                'course_id': self.course,
                'session_year_id': self.session_year
            }
        )

    def test_fee_structure_crud(self):
        self.authenticate_as_admin()
        url = reverse('fee_structures-list')

        # 1. Create Fee Structure
        payload = {
            'fee_name': 'Tuition & Lab Fee Term 1',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 1200.00,
            'lab_fee': 300.00,
            'library_fee': 100.00,
            'exam_fee': 150.00,
            'other_fee': 50.00,
            'due_date': '2026-10-31'
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(res.data['total_amount']), 1800.00)
        fee_id = res.data['id']

        # 2. List Fee Structures
        list_res = self.client.get(url)
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_res.data), 1)

        # 3. Update Fee Structure
        update_url = reverse('fee_structures-detail', kwargs={'pk': fee_id})
        update_res = self.client.put(update_url, {
            'fee_name': 'Tuition & Lab Fee Term 1 (Updated)',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 1300.00,
            'lab_fee': 300.00,
            'library_fee': 100.00,
            'exam_fee': 150.00,
            'other_fee': 50.00,
            'due_date': '2026-11-15'
        }, format='json')
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)
        self.assertEqual(float(update_res.data['total_amount']), 1900.00)

        # 4. Delete Fee Structure
        del_res = self.client.delete(update_url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

    def test_fee_structure_permission_denied_for_student_and_staff(self):
        # Staff cannot create fee structure
        self.authenticate_as_staff()
        url = reverse('fee_structures-list')
        res = self.client.post(url, {
            'fee_name': 'Staff Unauthorized Fee',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 1000.0
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Student cannot create fee structure
        self.authenticate_as_student()
        res2 = self.client.post(url, {
            'fee_name': 'Student Unauthorized Fee',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 1000.0
        }, format='json')
        self.assertEqual(res2.status_code, status.HTTP_403_FORBIDDEN)

    def test_generate_student_invoices(self):
        self.authenticate_as_admin()

        # 1. Setup Fee Structure
        fee_struct_res = self.client.post(reverse('fee_structures-list'), {
            'fee_name': 'Annual Tuition 2026',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 2000.0,
            'due_date': '2026-12-01'
        }, format='json')
        fee_structure_id = fee_struct_res.data['id']

        # 2. Generate Invoices
        gen_url = reverse('fees_generate_invoices')
        gen_res = self.client.post(gen_url, {
            'fee_structure_id': fee_structure_id
        }, format='json')
        self.assertEqual(gen_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(gen_res.data['invoices_created'], 2)

        # 3. Verify Invoices list
        invoices_url = reverse('fee_invoices-list')
        inv_res = self.client.get(invoices_url)
        self.assertEqual(inv_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(inv_res.data), 2)
        self.assertEqual(inv_res.data[0]['payment_status'], 'Unpaid')
        self.assertEqual(float(inv_res.data[0]['balance_amount']), 2000.0)

    def test_collect_payment_full_and_partial(self):
        self.authenticate_as_admin()

        # 1. Create fee structure & generate invoice
        fee_res = self.client.post(reverse('fee_structures-list'), {
            'fee_name': 'Semester 1 Fees',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 1000.0,
            'due_date': '2026-11-30'
        }, format='json')
        fee_id = fee_res.data['id']

        self.client.post(reverse('fees_generate_invoices'), {'fee_structure_id': fee_id}, format='json')
        invoices = self.client.get(reverse('fee_invoices-list')).data
        invoice_id = invoices[0]['id']

        # 2. Collect partial payment ($400 out of $1000)
        pay_url = reverse('fees_collect_payment')
        pay_res = self.client.post(pay_url, {
            'invoice_id': invoice_id,
            'amount_paid': 400.0,
            'payment_method': 'Bank Transfer',
            'remarks': 'First installment'
        }, format='json')
        self.assertEqual(pay_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pay_res.data['invoice']['payment_status'], 'Partial')
        self.assertEqual(float(pay_res.data['invoice']['paid_amount']), 400.0)
        self.assertEqual(float(pay_res.data['invoice']['balance_amount']), 600.0)

        # 3. Collect remaining payment ($600)
        pay_res2 = self.client.post(pay_url, {
            'invoice_id': invoice_id,
            'amount_paid': 600.0,
            'payment_method': 'Cash',
            'remarks': 'Final settlement'
        }, format='json')
        self.assertEqual(pay_res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pay_res2.data['invoice']['payment_status'], 'Paid')
        self.assertEqual(float(pay_res2.data['invoice']['balance_amount']), 0.0)

    def test_collect_payment_overpayment_rejected(self):
        self.authenticate_as_admin()

        fee_res = self.client.post(reverse('fee_structures-list'), {
            'fee_name': 'Exam Fee',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 500.0,
            'due_date': '2026-11-30'
        }, format='json')
        self.client.post(reverse('fees_generate_invoices'), {'fee_structure_id': fee_res.data['id']}, format='json')
        invoices = self.client.get(reverse('fee_invoices-list')).data
        invoice_id = invoices[0]['id']

        # Try to pay $600 for a $500 invoice
        pay_url = reverse('fees_collect_payment')
        pay_res = self.client.post(pay_url, {
            'invoice_id': invoice_id,
            'amount_paid': 600.0,
            'payment_method': 'Cash'
        }, format='json')
        self.assertEqual(pay_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', pay_res.data)

    def test_student_my_invoices_and_receipt(self):
        self.authenticate_as_admin()

        # 1. Setup invoice and record payment
        fee_res = self.client.post(reverse('fee_structures-list'), {
            'fee_name': 'Lab Fee',
            'course_id': self.course.id,
            'session_year_id': self.session_year.id,
            'tuition_fee': 800.0,
            'due_date': '2026-11-30'
        }, format='json')
        self.client.post(reverse('fees_generate_invoices'), {'fee_structure_id': fee_res.data['id']}, format='json')
        invoices = self.client.get(f"{reverse('fee_invoices-list')}?student_id={self.student_profile.id}").data
        invoice_id = invoices[0]['id']

        pay_res = self.client.post(reverse('fees_collect_payment'), {
            'invoice_id': invoice_id,
            'amount_paid': 800.0,
            'payment_method': 'Card',
            'remarks': 'Paid via credit card'
        }, format='json')
        payment_id = pay_res.data['payment']['id']

        # 2. Student views their own invoices
        self.authenticate_as_student()
        my_invoices_url = reverse('fees_my_invoices')
        my_res = self.client.get(my_invoices_url)
        self.assertEqual(my_res.status_code, status.HTTP_200_OK)
        self.assertIn('invoices', my_res.data)
        self.assertIn('summary', my_res.data)
        self.assertEqual(float(my_res.data['summary']['total_paid']), 800.0)
        self.assertEqual(float(my_res.data['summary']['total_balance']), 0.0)

        # 3. Student fetches printable receipt
        receipt_url = reverse('fees_receipt_detail', kwargs={'pk': payment_id})
        receipt_res = self.client.get(receipt_url)
        self.assertEqual(receipt_res.status_code, status.HTTP_200_OK)
        self.assertEqual(receipt_res.data['receipt_no'], f"REC-{payment_id:06d}")
        self.assertEqual(float(receipt_res.data['amount_paid']), 800.0)
        self.assertEqual(receipt_res.data['payment_method'], 'Card')
