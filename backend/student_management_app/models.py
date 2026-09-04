from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class SessionYearModel(models.Model):
    id = models.AutoField(primary_key=True)
    session_start_year = models.DateField()
    session_end_year = models.DateField()
    objects = models.Manager()

class CustomUser(AbstractUser):
    user_type_data = ((1,"Admin"),(2,"Staff"),(3,"Student"))
    user_type = models.CharField(default=1,choices=user_type_data,max_length=10)

class Admins(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Staffs(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    address = models.TextField()
    profile_pic = models.FileField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Subjects(models.Model):
    id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)
    course_id = models.ForeignKey(Courses,on_delete=models.CASCADE,default=1)
    staff_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    syllabus_file = models.FileField(upload_to='syllabi/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Students(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    gender = models.CharField(max_length=255)
    profile_pic = models.FileField(upload_to='profiles/', blank=True, null=True)
    address = models.TextField()
    course_id = models.ForeignKey(Courses,on_delete=models.DO_NOTHING)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects,on_delete=models.DO_NOTHING)
    attendance_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students,on_delete=models.DO_NOTHING)
    attendance_id = models.ForeignKey(Attendance,on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class LeaveReportStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id= models.ForeignKey(Students,on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

class LeaveReportStaff(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    leave_date = models.CharField(max_length=255)
    leave_message = models.TextField()
    leave_status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class FeedBackStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class NotificationStaffs(models.Model):
    id = models.AutoField(primary_key=True)
    staff_id = models.ForeignKey(Staffs, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class StudentResult(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    subject_exam_marks = models.FloatField(default=0)
    subject_assignment_marks = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('student_id', 'subject_id')


class FeeStructure(models.Model):
    id = models.AutoField(primary_key=True)
    fee_name = models.CharField(max_length=255)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE)
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    exam_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    @property
    def total_amount(self):
        return sum([
            self.tuition_fee or 0,
            self.lab_fee or 0,
            self.library_fee or 0,
            self.exam_fee or 0,
            self.other_fee or 0
        ])


class StudentFeeInvoice(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='fee_invoices')
    fee_structure_id = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='invoices')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_status = models.CharField(max_length=20, default='Unpaid') # 'Unpaid', 'Partial', 'Paid', 'Overdue'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('student_id', 'fee_structure_id')

    @property
    def balance_amount(self):
        return max(0.0, float(self.total_amount) - float(self.paid_amount))


class FeePayment(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_id = models.ForeignKey(StudentFeeInvoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Cash')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    objects = models.Manager()


class StudentDocument(models.Model):
    DOCUMENT_TYPES = (
        ('transcript', 'Academic Transcript'),
        ('id_card', 'National ID / Passport'),
        ('certificate', 'Diploma / Certificate'),
        ('medical', 'Medical Document'),
        ('other', 'Other Document'),
    )
    VERIFICATION_STATUSES = (
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Rejected'),
    )

    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='documents')
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, default='other')
    document_file = models.FileField(upload_to='documents/')
    verification_status = models.IntegerField(choices=VERIFICATION_STATUSES, default=0)
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    subject_id = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name='assignments')
    session_year_id = models.ForeignKey(SessionYearModel, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    max_marks = models.FloatField(default=100.0)
    attachment = models.FileField(upload_to='assignments/', null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()


class StudentAssignmentSubmission(models.Model):
    STATUS_CHOICES = (
        ('Submitted', 'Submitted'),
        ('Graded', 'Graded'),
        ('Resubmission_Requested', 'Resubmission Requested')
    )

    id = models.AutoField(primary_key=True)
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student_id = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='assignment_submissions')
    submission_file = models.FileField(upload_to='submissions/', null=True, blank=True)
    submission_text = models.TextField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    marks_obtained = models.FloatField(null=True, blank=True)
    feedback_remarks = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Submitted')
    graded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('assignment_id', 'student_id')


class StaffSalary(models.Model):
    id = models.AutoField(primary_key=True)
    staff = models.OneToOneField(Staffs, on_delete=models.CASCADE, related_name='salary_structure')
    designation = models.CharField(max_length=100, default='Lecturer')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    effective_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f"{self.staff.admin.first_name} {self.staff.admin.last_name} - {self.designation} (${self.base_salary})"


class StaffPayroll(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Paid', 'Paid'),
    )

    id = models.AutoField(primary_key=True)
    staff = models.ForeignKey(Staffs, on_delete=models.CASCADE, related_name='payrolls')
    payroll_month = models.IntegerField()
    payroll_year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, default='Bank Transfer')
    remarks = models.TextField(blank=True, null=True)
    generated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_payrolls')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        unique_together = ('staff', 'payroll_month', 'payroll_year')

    def __str__(self):
        return f"Payroll {self.staff.admin.first_name} {self.staff.admin.last_name} - {self.payroll_month}/{self.payroll_year} (${self.net_salary})"






@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if str(instance.user_type) == '1':
            Admins.objects.get_or_create(admin=instance)
        elif str(instance.user_type) == '2':
            Staffs.objects.get_or_create(admin=instance, defaults={'address': ''})
        elif str(instance.user_type) == '3':
            default_course = Courses.objects.first()
            default_session = SessionYearModel.objects.first()
            if default_course and default_session:
                Students.objects.get_or_create(
                    admin=instance,
                    defaults={
                        'course_id': default_course,
                        'session_year_id': default_session,
                        'address': '',
                        'profile_pic': '',
                        'gender': ''
                    }
                )

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if str(instance.user_type) == '1' and hasattr(instance, 'admins'):
        instance.admins.save()
    elif str(instance.user_type) == '2' and hasattr(instance, 'staffs'):
        instance.staffs.save()
    elif str(instance.user_type) == '3' and hasattr(instance, 'students'):
        instance.students.save()

