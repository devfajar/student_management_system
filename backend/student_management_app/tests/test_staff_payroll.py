import io
from rest_framework import status
from student_management_app.models import CustomUser, Staffs
from student_management_app.tests.base import BaseAPITestCase

class StaffPayrollAPITestCase(BaseAPITestCase):
    def setUp(self):
        super().setUp()

        # Second staff member for multi-tenancy / isolation testing
        self.staff_user_2 = CustomUser.objects.create_user(
            username='staff_jane',
            email='jane@test.com',
            password='password123',
            first_name='Jane',
            last_name='Smith',
            user_type='2'
        )
        self.staff_profile_2, _ = Staffs.objects.get_or_create(
            admin=self.staff_user_2,
            defaults={'address': 'Faculty Quarters 204'}
        )

    def test_admin_create_staff_salary_structure(self):
        """Admin can configure salary structure for staff."""
        self.authenticate_as_admin()
        payload = {
            'staff': self.staff_profile.id,
            'designation': 'Assistant Professor',
            'base_salary': '5000.00',
            'allowance': '800.00',
            'tax_percentage': '5.00',
            'effective_date': '2026-01-01',
            'is_active': True
        }
        response = self.client.post('/api/staff-salaries/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['designation'], 'Assistant Professor')
        self.assertEqual(float(response.data['base_salary']), 5000.00)
        self.assertEqual(float(response.data['allowance']), 800.00)

    def test_staff_view_own_salary_structure(self):
        """Staff can view their own configured salary details."""
        from student_management_app.models import StaffSalary
        StaffSalary.objects.create(
            staff=self.staff_profile,
            designation='Lecturer',
            base_salary=4500.00,
            allowance=500.00,
            tax_percentage=4.50,
            effective_date='2026-01-01'
        )
        self.authenticate_as_staff()
        response = self.client.get('/api/staff-salaries/my_salary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['designation'], 'Lecturer')
        self.assertEqual(float(response.data['base_salary']), 4500.00)

    def test_staff_cannot_view_or_modify_other_staff_salary(self):
        """Staff cannot modify or inspect other staff member's salary."""
        from student_management_app.models import StaffSalary
        salary_2 = StaffSalary.objects.create(
            staff=self.staff_profile_2,
            designation='Professor & Department Head',
            base_salary=9000.00,
            allowance=1500.00,
            tax_percentage=10.00
        )
        self.authenticate_as_staff()
        # Direct detail access to other staff's salary record
        detail_response = self.client.get(f'/api/staff-salaries/{salary_2.id}/')
        self.assertIn(detail_response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

        # Attempting to modify other staff's salary
        patch_response = self.client.patch(f'/api/staff-salaries/{salary_2.id}/', {'base_salary': '12000.00'})
        self.assertIn(patch_response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_admin_generate_individual_monthly_payroll(self):
        """Admin can generate individual payroll calculation for a staff member."""
        from student_management_app.models import StaffSalary
        StaffSalary.objects.create(
            staff=self.staff_profile,
            designation='Assistant Professor',
            base_salary=5000.00,
            allowance=800.00,
            tax_percentage=5.00
        )
        self.authenticate_as_admin()
        payload = {
            'staff': self.staff_profile.id,
            'payroll_month': 9,
            'payroll_year': 2026,
            'bonus': '250.00',
            'deductions': '100.00',
            'remarks': 'September 2026 Academic Payroll'
        }
        response = self.client.post('/api/staff-payrolls/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Expected: base(5000) + allowance(800) + bonus(250) - deductions(100) = 5950.00
        self.assertEqual(float(response.data['net_salary']), 5950.00)
        self.assertEqual(response.data['payment_status'], 'Pending')

    def test_admin_batch_generate_monthly_payroll(self):
        """Admin can trigger monthly payroll generation batch for all active staff."""
        from student_management_app.models import StaffSalary
        StaffSalary.objects.create(
            staff=self.staff_profile,
            designation='Senior Lecturer',
            base_salary=6000.00,
            allowance=1000.00,
            tax_percentage=5.00
        )
        StaffSalary.objects.create(
            staff=self.staff_profile_2,
            designation='Instructor',
            base_salary=4000.00,
            allowance=500.00,
            tax_percentage=3.00
        )
        self.authenticate_as_admin()
        response = self.client.post('/api/staff-payrolls/batch_generate/', {
            'payroll_month': 9,
            'payroll_year': 2026
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data.get('generated_count', 0), 2)

    def test_admin_update_payroll_payment_status(self):
        """Admin can mark a payroll record as Paid with date and payment method."""
        from student_management_app.models import StaffSalary, StaffPayroll
        salary = StaffSalary.objects.create(
            staff=self.staff_profile,
            designation='Lecturer',
            base_salary=5000.00,
            allowance=500.00
        )
        payroll = StaffPayroll.objects.create(
            staff=self.staff_profile,
            payroll_month=9,
            payroll_year=2026,
            basic_salary=5000.00,
            allowances=500.00,
            bonus=0.00,
            deductions=0.00,
            net_salary=5500.00,
            payment_status='Pending'
        )
        self.authenticate_as_admin()
        response = self.client.post(f'/api/staff-payrolls/{payroll.id}/mark_paid/', {
            'payment_method': 'Bank Transfer',
            'payment_date': '2026-09-30',
            'remarks': 'Transferred via Federal Bank direct deposit'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_status'], 'Paid')
        self.assertEqual(response.data['payment_method'], 'Bank Transfer')

    def test_staff_view_own_payroll_history(self):
        """Staff can view their own payroll records but not others."""
        from student_management_app.models import StaffPayroll
        payroll_1 = StaffPayroll.objects.create(
            staff=self.staff_profile,
            payroll_month=8,
            payroll_year=2026,
            basic_salary=5000.00,
            allowances=500.00,
            net_salary=5500.00,
            payment_status='Paid'
        )
        payroll_2 = StaffPayroll.objects.create(
            staff=self.staff_profile_2,
            payroll_month=8,
            payroll_year=2026,
            basic_salary=7000.00,
            allowances=800.00,
            net_salary=7800.00,
            payment_status='Paid'
        )
        self.authenticate_as_staff()
        response = self.client.get('/api/staff-payrolls/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        ids = [p['id'] for p in results]
        self.assertIn(payroll_1.id, ids)
        self.assertNotIn(payroll_2.id, ids)

    def test_staff_download_own_payslip_pdf(self):
        """Staff can download official PDF payslip for their payroll record."""
        from student_management_app.models import StaffPayroll
        payroll = StaffPayroll.objects.create(
            staff=self.staff_profile,
            payroll_month=9,
            payroll_year=2026,
            basic_salary=5000.00,
            allowances=500.00,
            bonus=200.00,
            deductions=150.00,
            net_salary=5550.00,
            payment_status='Paid',
            payment_date='2026-09-30',
            payment_method='Bank Transfer'
        )
        self.authenticate_as_staff()
        response = self.client.get(f'/api/staff-payrolls/{payroll.id}/download_payslip_pdf/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.headers.get('Content-Type'), 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
        self.assertIn('attachment;', response.headers.get('Content-Disposition', ''))

    def test_staff_cannot_download_other_staff_payslip_pdf(self):
        """Staff attempting to download another staff member's payslip receives 403 Forbidden."""
        from student_management_app.models import StaffPayroll
        payroll_2 = StaffPayroll.objects.create(
            staff=self.staff_profile_2,
            payroll_month=9,
            payroll_year=2026,
            basic_salary=7000.00,
            allowances=800.00,
            net_salary=7800.00,
            payment_status='Paid'
        )
        self.authenticate_as_staff()
        response = self.client.get(f'/api/staff-payrolls/{payroll_2.id}/download_payslip_pdf/')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_student_forbidden_from_payroll_endpoints(self):
        """Students are strictly forbidden from all payroll and salary endpoints."""
        self.authenticate_as_student()
        res1 = self.client.get('/api/staff-salaries/')
        self.assertEqual(res1.status_code, status.HTTP_403_FORBIDDEN)
        res2 = self.client.get('/api/staff-payrolls/')
        self.assertEqual(res2.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_payroll_access_denied(self):
        """Anonymous callers are rejected with 401 Unauthorized."""
        res1 = self.client.get('/api/staff-salaries/')
        self.assertEqual(res1.status_code, status.HTTP_401_UNAUTHORIZED)
        res2 = self.client.get('/api/staff-payrolls/')
        self.assertEqual(res2.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_export_payroll_excel_and_csv(self):
        """Admin can export monthly payroll report in Excel and CSV formats."""
        from student_management_app.models import StaffPayroll
        StaffPayroll.objects.create(
            staff=self.staff_profile,
            payroll_month=9,
            payroll_year=2026,
            basic_salary=5000.00,
            allowances=500.00,
            net_salary=5500.00,
            payment_status='Paid'
        )
        self.authenticate_as_admin()

        # CSV Export
        csv_resp = self.client.get('/api/staff-payrolls/export_csv/?month=9&year=2026')
        self.assertEqual(csv_resp.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', csv_resp.headers.get('Content-Type'))
        self.assertIn(b'Basic Salary', csv_resp.content)

        # Excel Export
        excel_resp = self.client.get('/api/staff-payrolls/export_excel/?month=9&year=2026')
        self.assertEqual(excel_resp.status_code, status.HTTP_200_OK)
        self.assertIn('spreadsheetml', excel_resp.headers.get('Content-Type'))
