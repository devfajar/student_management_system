import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from student_management_app.models import (
    CustomUser, Admins, Staffs, Students, Courses, Subjects, SessionYearModel,
    Attendance, AttendanceReport, StudentResult, FeeStructure, StudentFeeInvoice, FeePayment,
    StudentDocument, Assignment, StudentAssignmentSubmission,
    StaffSalary, StaffPayroll, NotificationStudent, NotificationStaffs
)

class Command(BaseCommand):
    help = "Seeds the database with a comprehensive, realistic demo ecosystem for all roles."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("==> Seeding Student Management System demo data..."))

        # 1. Academic Sessions
        session_1, _ = SessionYearModel.objects.get_or_create(
            id=1,
            defaults={
                'session_start_year': '2025-08-01',
                'session_end_year': '2026-05-31'
            }
        )
        session_2, _ = SessionYearModel.objects.get_or_create(
            id=2,
            defaults={
                'session_start_year': '2026-08-01',
                'session_end_year': '2027-05-31'
            }
        )
        self.stdout.write(self.style.SUCCESS("  [✓] Academic Sessions configured (2025-2026, 2026-2027)"))

        # 2. Courses
        courses_data = [
            (1, "Computer Science & Engineering"),
            (2, "Electrical & Electronics Engineering"),
            (3, "Information Technology & AI")
        ]
        courses = {}
        for c_id, c_name in courses_data:
            course, _ = Courses.objects.get_or_create(id=c_id, defaults={'course_name': c_name})
            courses[c_id] = course
        self.stdout.write(self.style.SUCCESS(f"  [✓] {len(courses)} Academic Degree Programs active"))

        # 3. Administrator
        admin_user, admin_created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@school.com',
                'first_name': 'Principal',
                'last_name': 'Administrator',
                'user_type': '1',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if admin_created:
            admin_user.set_password('admin123')
            admin_user.save()
        Admins.objects.get_or_create(admin=admin_user)
        self.stdout.write(self.style.SUCCESS("  [✓] System Administrator active ('admin' / 'admin123')"))

        # 4. Faculty Staff & Salary Packages
        faculty_data = [
            {
                'username': 'prof_smith',
                'email': 'alan.smith@school.com',
                'first_name': 'Alan',
                'last_name': 'Smith',
                'address': 'Faculty Quarters Building A-102',
                'designation': 'Professor & Department Head',
                'base_salary': 8500.00,
                'allowance': 1500.00,
                'tax': 8.00
            },
            {
                'username': 'dr_johnson',
                'email': 'sarah.johnson@school.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'address': 'Faculty Quarters Building B-205',
                'designation': 'Associate Professor',
                'base_salary': 6800.00,
                'allowance': 1000.00,
                'tax': 6.00
            },
            {
                'username': 'lecturer_emily',
                'email': 'emily.davis@school.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'address': '124 Academic Way, Campus Heights',
                'designation': 'Lecturer & Lab Director',
                'base_salary': 5000.00,
                'allowance': 600.00,
                'tax': 5.00
            }
        ]

        faculty_staff = {}
        for f in faculty_data:
            user, created = CustomUser.objects.get_or_create(
                username=f['username'],
                defaults={
                    'email': f['email'],
                    'first_name': f['first_name'],
                    'last_name': f['last_name'],
                    'user_type': '2'
                }
            )
            if created:
                user.set_password('staff123')
                user.save()
            staff_profile, _ = Staffs.objects.get_or_create(admin=user, defaults={'address': f['address']})
            faculty_staff[f['username']] = (user, staff_profile)

            # Salary Tier Configuration
            StaffSalary.objects.get_or_create(
                staff=staff_profile,
                defaults={
                    'designation': f['designation'],
                    'base_salary': f['base_salary'],
                    'allowance': f['allowance'],
                    'tax_percentage': f['tax'],
                    'effective_date': '2026-01-01',
                    'is_active': True
                }
            )
        self.stdout.write(self.style.SUCCESS("  [✓] 3 Faculty Staff Members & Salary Packages initialized ('staff123')"))

        # 5. Academic Subjects
        subjects_data = [
            (1, "Data Structures & Algorithms", 1, 'prof_smith'),
            (2, "Operating Systems", 1, 'dr_johnson'),
            (3, "Database Management Systems", 1, 'lecturer_emily'),
            (4, "Digital Electronics", 2, 'dr_johnson'),
            (5, "Artificial Intelligence & ML", 3, 'prof_smith'),
            (6, "Computer Networks", 3, 'lecturer_emily')
        ]
        subjects = {}
        for s_id, s_name, c_id, staff_uname in subjects_data:
            subj, _ = Subjects.objects.get_or_create(
                id=s_id,
                defaults={
                    'subject_name': s_name,
                    'course_id': courses[c_id],
                    'staff_id': faculty_staff[staff_uname][0]
                }
            )
            subjects[s_id] = subj
        self.stdout.write(self.style.SUCCESS(f"  [✓] {len(subjects)} Course Subjects & Faculty Instructors mapped"))

        # 6. Students
        students_data = [
            ('student_alex', 'alex.morgan@student.school.com', 'Alex', 'Morgan', 'Male', 'Dormitory Alpha 101', 1, session_2),
            ('student_bella', 'bella.thorne@student.school.com', 'Bella', 'Thorne', 'Female', 'Dormitory Beta 204', 1, session_2),
            ('student_chris', 'chris.evans@student.school.com', 'Chris', 'Evans', 'Male', 'Off-Campus Apt 12', 2, session_2),
            ('student_diana', 'diana.prince@student.school.com', 'Diana', 'Prince', 'Female', 'Dormitory Alpha 305', 2, session_2),
            ('student_ethan', 'ethan.hunt@student.school.com', 'Ethan', 'Hunt', 'Male', 'Dormitory Gamma 102', 3, session_2),
            ('student_fiona', 'fiona.g@student.school.com', 'Fiona', 'Gallagher', 'Female', 'Off-Campus Apt 4B', 3, session_2)
        ]

        students = {}
        for uname, email, fname, lname, gender, addr, c_id, sess in students_data:
            u, created = CustomUser.objects.get_or_create(
                username=uname,
                defaults={
                    'email': email,
                    'first_name': fname,
                    'last_name': lname,
                    'user_type': '3'
                }
            )
            if created:
                u.set_password('student123')
                u.save()

            st_profile, _ = Students.objects.get_or_create(
                admin=u,
                defaults={
                    'gender': gender,
                    'address': addr,
                    'course_id': courses[c_id],
                    'session_year_id': sess
                }
            )
            students[uname] = (u, st_profile)
        self.stdout.write(self.style.SUCCESS(f"  [✓] {len(students)} Students enrolled in degree programs ('student123')"))

        # 7. Fee Structures & Student Invoices
        fee_struct, _ = FeeStructure.objects.get_or_create(
            fee_name="Academic Year 2026-2027 Standard Tuition & Fees",
            course_id=courses[1],
            session_year_id=session_2,
            defaults={
                'tuition_fee': 4000.00,
                'lab_fee': 500.00,
                'library_fee': 200.00,
                'exam_fee': 150.00,
                'other_fee': 100.00,
                'due_date': '2026-10-15'
            }
        )

        total_fee = fee_struct.total_amount
        # Invoices
        for uname in ['student_alex', 'student_bella', 'student_chris']:
            st_prof = students[uname][1]
            paid = total_fee if uname == 'student_alex' else (2500.00 if uname == 'student_bella' else 0.00)
            status_inv = 'Paid' if uname == 'student_alex' else ('Partial' if uname == 'student_bella' else 'Unpaid')
            inv, created_inv = StudentFeeInvoice.objects.get_or_create(
                student_id=st_prof,
                fee_structure_id=fee_struct,
                defaults={
                    'total_amount': total_fee,
                    'paid_amount': paid,
                    'payment_status': status_inv
                }
            )
            if created_inv and paid > 0:
                FeePayment.objects.create(
                    invoice_id=inv,
                    amount_paid=paid,
                    payment_method='Bank Wire' if uname == 'student_alex' else 'Cash',
                    transaction_id=f"TXN-{inv.id:04d}-DEMO",
                    remarks="Official Registration Fee Payment"
                )
        self.stdout.write(self.style.SUCCESS("  [✓] Fee Structures, Student Invoices & Payment Ledger seeded"))

        # 8. Coursework Assignments & Submissions
        now = timezone.now()
        assign_1, _ = Assignment.objects.get_or_create(
            title="Lab Project: Balanced Search Trees Implementation",
            subject_id=subjects[1],
            session_year_id=session_2,
            defaults={
                'description': "Implement AVL and Red-Black tree self-balancing routines with unit test coverage.",
                'deadline': now + datetime.timedelta(days=7),
                'max_marks': 100.0,
                'created_by': faculty_staff['prof_smith'][0]
            }
        )

        assign_2, _ = Assignment.objects.get_or_create(
            title="Kernel Process Scheduler Simulation",
            subject_id=subjects[2],
            session_year_id=session_2,
            defaults={
                'description': "Simulate Round-Robin and Priority Scheduling algorithms in Python or C++.",
                'deadline': now - datetime.timedelta(days=2),
                'max_marks': 50.0,
                'created_by': faculty_staff['dr_johnson'][0]
            }
        )

        # Submissions
        alex_prof = students['student_alex'][1]
        bella_prof = students['student_bella'][1]

        sub_1, _ = StudentAssignmentSubmission.objects.get_or_create(
            assignment_id=assign_1,
            student_id=alex_prof,
            defaults={
                'submission_text': "GitHub repository link: https://github.com/alexmorgan/trees-project with benchmark suite.",
                'status': 'Graded',
                'marks_obtained': 96.0,
                'feedback_remarks': "Exceptional tree rotation algorithms and edge-case handling.",
                'graded_by': faculty_staff['prof_smith'][0],
                'graded_at': now
            }
        )

        sub_2, _ = StudentAssignmentSubmission.objects.get_or_create(
            assignment_id=assign_1,
            student_id=bella_prof,
            defaults={
                'submission_text': "Included full implementation documentation and source code bundle.",
                'status': 'Submitted'
            }
        )
        self.stdout.write(self.style.SUCCESS("  [✓] Assignments & Student Submissions with Grading benchmarks active"))

        # 9. Attendance & Reports
        att_date = (now - datetime.timedelta(days=1)).date()
        att, _ = Attendance.objects.get_or_create(
            subject_id=subjects[1],
            attendance_date=att_date,
            session_year_id=session_2
        )
        for uname, present in [('student_alex', True), ('student_bella', True), ('student_chris', False)]:
            st_prof = students[uname][1]
            AttendanceReport.objects.get_or_create(
                student_id=st_prof,
                attendance_id=att,
                defaults={'status': present}
            )
        self.stdout.write(self.style.SUCCESS("  [✓] Daily Attendance Records & Session Reports populated"))

        # 10. Academic Results & Grades
        StudentResult.objects.get_or_create(
            student_id=alex_prof,
            subject_id=subjects[1],
            defaults={
                'subject_exam_marks': 88.0,
                'subject_assignment_marks': 96.0
            }
        )
        StudentResult.objects.get_or_create(
            student_id=bella_prof,
            subject_id=subjects[1],
            defaults={
                'subject_exam_marks': 82.0,
                'subject_assignment_marks': 85.0
            }
        )
        self.stdout.write(self.style.SUCCESS("  [✓] Examination Marks & GPA Grades computed"))

        # 11. Staff Payroll
        curr_month = now.month
        curr_year = now.year
        for uname, staff_tuple in faculty_staff.items():
            staff_user, staff_prof = staff_tuple
            sal = staff_prof.salary_structure
            is_paid = uname != 'lecturer_emily'
            StaffPayroll.objects.get_or_create(
                staff=staff_prof,
                payroll_month=curr_month,
                payroll_year=curr_year,
                defaults={
                    'basic_salary': sal.base_salary,
                    'allowances': sal.allowance,
                    'bonus': 300.00 if uname == 'prof_smith' else 0.00,
                    'deductions': 150.00 if uname == 'prof_smith' else 0.00,
                    'net_salary': float(sal.base_salary) + float(sal.allowance) + (150.00 if uname == 'prof_smith' else 0.00),
                    'payment_status': 'Paid' if is_paid else 'Pending',
                    'payment_method': 'Bank Direct Deposit' if is_paid else 'Bank Transfer',
                    'payment_date': now.date() if is_paid else None,
                    'generated_by': admin_user
                }
            )
        self.stdout.write(self.style.SUCCESS("  [✓] Monthly Faculty Payroll records & PDF payslip targets generated"))

        # 12. Announcements & Circulars
        NotificationStudent.objects.get_or_create(
            student_id=alex_prof,
            message="Welcome to the Fall semester! Please review your course syllabus in your student portal."
        )
        NotificationStaffs.objects.get_or_create(
            staff_id=faculty_staff['prof_smith'][1],
            message="Faculty Departmental Meeting scheduled for Thursday 2:00 PM in Conference Room 3."
        )
        self.stdout.write(self.style.SUCCESS("  [✓] Broadcast Notifications & System Circulars initialized"))

        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("✨ DEMO ENVIRONMENT SEEDING COMPLETED SUCCESSFULLY!"))
        self.stdout.write(self.style.SUCCESS("========================================================"))
        self.stdout.write(self.style.NOTICE("Credentials Summary:"))
        self.stdout.write("  - Administrator:  username: 'admin'          password: 'admin123'")
        self.stdout.write("  - Faculty Staff:  username: 'prof_smith'     password: 'staff123'")
        self.stdout.write("  - Faculty Staff:  username: 'dr_johnson'     password: 'staff123'")
        self.stdout.write("  - Faculty Staff:  username: 'lecturer_emily' password: 'staff123'")
        self.stdout.write("  - Student:        username: 'student_alex'   password: 'student123'")
        self.stdout.write("  - Student:        username: 'student_bella'  password: 'student123'")
        self.stdout.write(self.style.SUCCESS("========================================================\n"))
