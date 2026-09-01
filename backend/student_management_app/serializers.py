from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from student_management_app.models import (
    CustomUser, Admins, Staffs, Courses, Subjects, Students,
    SessionYearModel, Attendance, AttendanceReport,
    LeaveReportStudent, LeaveReportStaff,
    FeedBackStudent, FeedBackStaffs,
    NotificationStudent, NotificationStaffs,
    StudentResult, FeeStructure, StudentFeeInvoice, FeePayment
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': str(user.user_type),
        }
        if str(user.user_type) == '2' and hasattr(user, 'staffs'):
            data['user']['profile_id'] = user.staffs.id
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            data['user']['profile_id'] = user.students.id
        elif str(user.user_type) == '1' and hasattr(user, 'admins'):
            data['user']['profile_id'] = user.admins.id
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type']


class SessionYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionYearModel
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course_id.course_name', read_only=True)
    staff_name = serializers.SerializerMethodField()
    syllabus_file = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)

    class Meta:
        model = Subjects
        fields = ['id', 'subject_name', 'course_id', 'course_name', 'staff_id', 'staff_name', 'syllabus_file', 'created_at', 'updated_at']

    def get_staff_name(self, obj):
        if obj.staff_id:
            return f"{obj.staff_id.first_name} {obj.staff_id.last_name}".strip() or obj.staff_id.username
        return ""


class StaffSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Staffs
        fields = ['id', 'admin', 'address', 'created_at', 'updated_at', 'first_name', 'last_name', 'username', 'email', 'password']

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        username = validated_data.pop('username', '')
        email = validated_data.pop('email', '')
        password = validated_data.pop('password', '')
        address = validated_data.pop('address', '')

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=2
        )
        staff = Staffs.objects.get(admin=user)
        staff.address = address
        staff.save()
        return staff

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        username = validated_data.pop('username', None)

        user = instance.admin
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        if password:
            user.set_password(password)
        user.save()

        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance


class StudentSerializer(serializers.ModelSerializer):
    admin = UserSerializer(read_only=True)
    course_name = serializers.CharField(source='course_id.course_name', read_only=True)
    session_year = serializers.SerializerMethodField()

    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    profile_pic = serializers.FileField(required=False, allow_null=True, allow_empty_file=True)

    class Meta:
        model = Students
        fields = [
            'id', 'admin', 'gender', 'profile_pic', 'address',
            'course_id', 'course_name', 'session_year_id', 'session_year',
            'created_at', 'updated_at',
            'first_name', 'last_name', 'username', 'email', 'password'
        ]
        extra_kwargs = {
            'profile_pic': {'required': False, 'allow_null': True},
            'address': {'required': False},
            'gender': {'required': False},
            'course_id': {'required': False},
            'session_year_id': {'required': False},
        }

    def get_session_year(self, obj):
        if obj.session_year_id:
            return f"{obj.session_year_id.session_start_year} TO {obj.session_year_id.session_end_year}"
        return ""

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        username = validated_data.pop('username', '')
        email = validated_data.pop('email', '')
        password = validated_data.pop('password', '')
        address = validated_data.pop('address', '')
        gender = validated_data.pop('gender', 'Male')
        course_id = validated_data.pop('course_id')
        session_year_id = validated_data.pop('session_year_id')
        profile_pic = validated_data.pop('profile_pic', '')

        user = CustomUser.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type=3
        )
        student, _ = Students.objects.get_or_create(
            admin=user,
            defaults={
                'course_id': course_id or Courses.objects.first(),
                'session_year_id': session_year_id or SessionYearModel.objects.first(),
                'gender': gender,
                'address': address
            }
        )
        student.address = address
        student.gender = gender
        if course_id:
            student.course_id = course_id
        if session_year_id:
            student.session_year_id = session_year_id
        if profile_pic:
            student.profile_pic = profile_pic
        student.save()
        return student

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        email = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        username = validated_data.pop('username', None)

        user = instance.admin
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        if username is not None:
            user.username = username
        if password:
            user.set_password(password)
        user.save()

        instance.address = validated_data.get('address', instance.address)
        instance.gender = validated_data.get('gender', instance.gender)
        if 'course_id' in validated_data:
            instance.course_id = validated_data['course_id']
        if 'session_year_id' in validated_data:
            instance.session_year_id = validated_data['session_year_id']
        if 'profile_pic' in validated_data and validated_data['profile_pic']:
            instance.profile_pic = validated_data['profile_pic']
        instance.save()
        return instance


class AttendanceSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject_id.subject_name', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'subject_id', 'subject_name', 'attendance_date', 'session_year_id', 'created_at']


class AttendanceReportSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceReport
        fields = ['id', 'student_id', 'student_name', 'attendance_id', 'status', 'created_at']

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}".strip() or obj.student_id.admin.username


class LeaveReportStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveReportStudent
        fields = ['id', 'student_id', 'student_name', 'leave_date', 'leave_message', 'leave_status', 'created_at']

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}".strip() or obj.student_id.admin.username


class LeaveReportStaffSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()

    class Meta:
        model = LeaveReportStaff
        fields = ['id', 'staff_id', 'staff_name', 'leave_date', 'leave_message', 'leave_status', 'created_at']

    def get_staff_name(self, obj):
        return f"{obj.staff_id.admin.first_name} {obj.staff_id.admin.last_name}".strip() or obj.staff_id.admin.username


class FeedBackStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = FeedBackStudent
        fields = ['id', 'student_id', 'student_name', 'feedback', 'feedback_reply', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}".strip() or obj.student_id.admin.username


class FeedBackStaffsSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()

    class Meta:
        model = FeedBackStaffs
        fields = ['id', 'staff_id', 'staff_name', 'feedback', 'feedback_reply', 'created_at', 'updated_at']

    def get_staff_name(self, obj):
        return f"{obj.staff_id.admin.first_name} {obj.staff_id.admin.last_name}".strip() or obj.staff_id.admin.username


class StudentResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_username = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='subject_id.subject_name', read_only=True)
    course_name = serializers.CharField(source='student_id.course_id.course_name', read_only=True)
    total_marks = serializers.SerializerMethodField()
    grade = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = StudentResult
        fields = [
            'id', 'student_id', 'student_name', 'student_username',
            'subject_id', 'subject_name', 'course_name',
            'subject_exam_marks', 'subject_assignment_marks',
            'total_marks', 'grade', 'status',
            'created_at', 'updated_at'
        ]

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}".strip() or obj.student_id.admin.username

    def get_student_username(self, obj):
        return obj.student_id.admin.username

    def get_total_marks(self, obj):
        return round(float(obj.subject_exam_marks) + float(obj.subject_assignment_marks), 2)

    def get_grade(self, obj):
        total = float(obj.subject_exam_marks) + float(obj.subject_assignment_marks)
        if total >= 90:
            return 'A+'
        elif total >= 80:
            return 'A'
        elif total >= 70:
            return 'B'
        elif total >= 60:
            return 'C'
        elif total >= 50:
            return 'D'
        return 'F'

    def get_status(self, obj):
        total = float(obj.subject_exam_marks) + float(obj.subject_assignment_marks)
        return 'Passed' if total >= 50 else 'Failed'


class NotificationStudentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_username = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='student_id.course_id.course_name', read_only=True)

    class Meta:
        model = NotificationStudent
        fields = ['id', 'student_id', 'student_name', 'student_username', 'course_name', 'message', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}".strip() or obj.student_id.admin.username

    def get_student_username(self, obj):
        return obj.student_id.admin.username


class NotificationStaffsSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    staff_username = serializers.SerializerMethodField()

    class Meta:
        model = NotificationStaffs
        fields = ['id', 'staff_id', 'staff_name', 'staff_username', 'message', 'created_at', 'updated_at']

    def get_staff_name(self, obj):
        return f"{obj.staff_id.admin.first_name} {obj.staff_id.admin.last_name}".strip() or obj.staff_id.admin.username

    def get_staff_username(self, obj):
        return obj.staff_id.admin.username


class FeeStructureSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course_id.course_name', read_only=True)
    session_year = serializers.SerializerMethodField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = FeeStructure
        fields = [
            'id', 'fee_name', 'course_id', 'course_name',
            'session_year_id', 'session_year',
            'tuition_fee', 'lab_fee', 'library_fee', 'exam_fee', 'other_fee',
            'total_amount', 'due_date', 'created_at', 'updated_at'
        ]

    def get_session_year(self, obj):
        if obj.session_year_id:
            return f"{obj.session_year_id.session_start_year} TO {obj.session_year_id.session_end_year}"
        return ""


class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ['id', 'invoice_id', 'amount_paid', 'payment_method', 'transaction_id', 'payment_date', 'remarks']


class StudentFeeInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_username = serializers.SerializerMethodField()
    course_name = serializers.CharField(source='student_id.course_id.course_name', read_only=True)
    fee_name = serializers.CharField(source='fee_structure_id.fee_name', read_only=True)
    due_date = serializers.DateField(source='fee_structure_id.due_date', read_only=True)
    balance_amount = serializers.ReadOnlyField()
    payments = FeePaymentSerializer(many=True, read_only=True)

    class Meta:
        model = StudentFeeInvoice
        fields = [
            'id', 'student_id', 'student_name', 'student_username', 'course_name',
            'fee_structure_id', 'fee_name', 'due_date',
            'total_amount', 'paid_amount', 'balance_amount',
            'payment_status', 'payments', 'created_at', 'updated_at'
        ]

    def get_student_name(self, obj):
        return f"{obj.student_id.admin.first_name} {obj.student_id.admin.last_name}".strip() or obj.student_id.admin.username

    def get_student_username(self, obj):
        return obj.student_id.admin.username



