import json
import datetime
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.cache import cache

from student_management_app.cache_utils import (
    COURSES_CACHE_KEY, SUBJECTS_CACHE_KEY, SESSIONS_CACHE_KEY, FEE_STRUCTURES_CACHE_KEY,
    get_dashboard_cache_key, invalidate_dashboard_cache, invalidate_courses_cache,
    invalidate_subjects_cache, invalidate_sessions_cache, invalidate_fee_structures_cache
)

from student_management_app.models import (
    CustomUser, Admins, Staffs, Courses, Subjects, Students,
    SessionYearModel, Attendance, AttendanceReport,
    LeaveReportStudent, LeaveReportStaff,
    FeedBackStudent, FeedBackStaffs,
    StudentResult, NotificationStudent, NotificationStaffs,
    FeeStructure, StudentFeeInvoice, FeePayment,
    StudentDocument, Assignment, StudentAssignmentSubmission
)
from student_management_app.serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    StaffSerializer, StudentSerializer, CourseSerializer, SubjectSerializer,
    SessionYearSerializer, AttendanceSerializer, AttendanceReportSerializer,
    LeaveReportStudentSerializer, LeaveReportStaffSerializer,
    FeedBackStudentSerializer, FeedBackStaffsSerializer,
    StudentResultSerializer, NotificationStudentSerializer, NotificationStaffsSerializer,
    FeeStructureSerializer, StudentFeeInvoiceSerializer, FeePaymentSerializer,
    StudentDocumentSerializer, AssignmentSerializer, StudentAssignmentSubmissionSerializer
)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    user = request.user
    if request.method == 'GET':
        user_data = UserSerializer(user).data
        profile_data = {}
        if str(user.user_type) == '1' and hasattr(user, 'admins'):
            profile_data['id'] = user.admins.id
        elif str(user.user_type) == '2' and hasattr(user, 'staffs'):
            profile_data['id'] = user.staffs.id
            profile_data['address'] = user.staffs.address
            profile_data['profile_pic'] = request.build_absolute_uri(user.staffs.profile_pic.url) if user.staffs.profile_pic else None
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            profile_data['id'] = user.students.id
            profile_data['address'] = user.students.address
            profile_data['gender'] = user.students.gender
            profile_data['profile_pic'] = request.build_absolute_uri(user.students.profile_pic.url) if user.students.profile_pic else None
            profile_data['course_id'] = user.students.course_id.id if user.students.course_id else None
            profile_data['course_name'] = user.students.course_id.course_name if user.students.course_id else ""
            profile_data['session_year_id'] = user.students.session_year_id.id if user.students.session_year_id else None
            if user.students.session_year_id:
                profile_data['session_year'] = f"{user.students.session_year_id.session_start_year} TO {user.students.session_year_id.session_end_year}"
        user_data['profile'] = profile_data
        return Response(user_data)

    elif request.method == 'PUT':
        first_name = request.data.get('first_name', user.first_name)
        last_name = request.data.get('last_name', user.last_name)
        password = request.data.get('password')
        address = request.data.get('address')
        profile_pic = request.FILES.get('profile_pic')

        user.first_name = first_name
        user.last_name = last_name
        if password:
            user.set_password(password)
        user.save()

        if str(user.user_type) == '2' and hasattr(user, 'staffs'):
            if address is not None:
                user.staffs.address = address
            if profile_pic:
                user.staffs.profile_pic = profile_pic
            user.staffs.save()
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            if address is not None:
                user.students.address = address
            if profile_pic:
                user.students.profile_pic = profile_pic
            user.students.save()

        return Response({'message': 'Profile updated successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_view(request):
    user = request.user
    user_type = str(user.user_type)
    cache_key = get_dashboard_cache_key(user)

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return Response(cached_data)

    if user_type == '1': # Admin
        data = {
            'user_type': '1',
            'student_count': Students.objects.all().count(),
            'total_students': Students.objects.all().count(),
            'staff_count': Staffs.objects.all().count(),
            'total_staff': Staffs.objects.all().count(),
            'course_count': Courses.objects.all().count(),
            'total_courses': Courses.objects.all().count(),
            'subject_count': Subjects.objects.all().count(),
            'total_subjects': Subjects.objects.all().count(),
            'pending_student_leaves': LeaveReportStudent.objects.filter(leave_status=0).count(),
            'pending_staff_leaves': LeaveReportStaff.objects.filter(leave_status=0).count(),
        }

    elif user_type == '2': # Staff
        subjects = Subjects.objects.filter(staff_id=user.id)
        subject_count = subjects.count()
        course_ids = list(set([s.course_id.id for s in subjects]))
        students_count = Students.objects.filter(course_id__in=course_ids).count()
        attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
        leave_count = 0
        total_leave = 0
        if hasattr(user, 'staffs'):
            leave_count = LeaveReportStaff.objects.filter(staff_id=user.staffs, leave_status=1).count()
            total_leave = LeaveReportStaff.objects.filter(staff_id=user.staffs).count()

        data = {
            'user_type': '2',
            'students_count': students_count,
            'attendance_count': attendance_count,
            'leave_count': leave_count,
            'total_leave': total_leave,
            'subject_count': subject_count,
        }

    elif user_type == '3': # Student
        total_attendance = 0
        attendance_present = 0
        attendance_absent = 0
        subjects_count = 0
        leaves_applied = 0
        leaves_approved = 0

        if hasattr(user, 'students'):
            student_obj = user.students
            total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
            attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
            attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()
            if student_obj.course_id:
                subjects_count = Subjects.objects.filter(course_id=student_obj.course_id).count()
            leaves_applied = LeaveReportStudent.objects.filter(student_id=student_obj).count()
            leaves_approved = LeaveReportStudent.objects.filter(student_id=student_obj, leave_status=1).count()

        data = {
            'user_type': '3',
            'total_attendance': total_attendance,
            'attendance_present': attendance_present,
            'attendance_absent': attendance_absent,
            'subjects_count': subjects_count,
            'leaves_applied': leaves_applied,
            'leaves_approved': leaves_approved,
        }
    else:
        return Response({'error': 'Unknown role'}, status=status.HTTP_400_BAD_REQUEST)

    cache.set(cache_key, data, timeout=300)
    return Response(data)


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staffs.objects.all().order_by('-id')
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_dashboard_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_dashboard_cache()

    def destroy(self, request, *args, **kwargs):
        staff = self.get_object()
        user = staff.admin
        user.delete() # Also deletes staff
        invalidate_dashboard_cache()
        return Response({'message': 'Staff deleted successfully'}, status=status.HTTP_200_OK)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Students.objects.all().order_by('-id')
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_dashboard_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_dashboard_cache()

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        user = student.admin
        user.delete() # Also deletes student
        invalidate_dashboard_cache()
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Courses.objects.all().order_by('-id')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cached = cache.get(COURSES_CACHE_KEY)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(COURSES_CACHE_KEY, response.data, timeout=600)
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_courses_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_courses_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        invalidate_courses_cache()


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subjects.objects.all().order_by('-id')
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cached = cache.get(SUBJECTS_CACHE_KEY)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(SUBJECTS_CACHE_KEY, response.data, timeout=600)
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_subjects_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_subjects_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        invalidate_subjects_cache()


class SessionYearViewSet(viewsets.ModelViewSet):
    queryset = SessionYearModel.objects.all().order_by('-id')
    serializer_class = SessionYearSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cached = cache.get(SESSIONS_CACHE_KEY)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(SESSIONS_CACHE_KEY, response.data, timeout=600)
        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        invalidate_sessions_cache()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        invalidate_sessions_cache()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        invalidate_sessions_cache()



class StudentLeaveViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveReportStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if str(user.user_type) == '1': # Admin sees all
            return LeaveReportStudent.objects.all().order_by('-id')
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            return LeaveReportStudent.objects.filter(student_id=user.students).order_by('-id')
        return LeaveReportStudent.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'students'):
            return Response({'error': 'Only students can apply for student leave'}, status=status.HTTP_403_FORBIDDEN)
        leave_date = request.data.get('leave_date')
        leave_message = request.data.get('leave_message')
        leave = LeaveReportStudent.objects.create(
            student_id=user.students,
            leave_date=leave_date,
            leave_message=leave_message,
            leave_status=0
        )
        return Response(LeaveReportStudentSerializer(leave).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.leave_status = 1
        leave.save()
        return Response({'message': 'Leave approved successfully'})

    @action(detail=True, methods=['post'])
    def disapprove(self, request, pk=None):
        leave = self.get_object()
        leave.leave_status = 2
        leave.save()
        return Response({'message': 'Leave disapproved successfully'})


class StaffLeaveViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveReportStaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if str(user.user_type) == '1': # Admin sees all
            return LeaveReportStaff.objects.all().order_by('-id')
        elif str(user.user_type) == '2' and hasattr(user, 'staffs'):
            return LeaveReportStaff.objects.filter(staff_id=user.staffs).order_by('-id')
        return LeaveReportStaff.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'staffs'):
            return Response({'error': 'Only staff can apply for staff leave'}, status=status.HTTP_403_FORBIDDEN)
        leave_date = request.data.get('leave_date')
        leave_message = request.data.get('leave_message')
        leave = LeaveReportStaff.objects.create(
            staff_id=user.staffs,
            leave_date=leave_date,
            leave_message=leave_message,
            leave_status=0
        )
        return Response(LeaveReportStaffSerializer(leave).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.leave_status = 1
        leave.save()
        return Response({'message': 'Leave approved successfully'})

    @action(detail=True, methods=['post'])
    def disapprove(self, request, pk=None):
        leave = self.get_object()
        leave.leave_status = 2
        leave.save()
        return Response({'message': 'Leave disapproved successfully'})


class StudentFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedBackStudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if str(user.user_type) == '1':
            return FeedBackStudent.objects.all().order_by('-id')
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            return FeedBackStudent.objects.filter(student_id=user.students).order_by('-id')
        return FeedBackStudent.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'students'):
            return Response({'error': 'Only students can submit feedback'}, status=status.HTTP_403_FORBIDDEN)
        feedback_text = request.data.get('feedback')
        feedback_obj = FeedBackStudent.objects.create(
            student_id=user.students,
            feedback=feedback_text,
            feedback_reply=""
        )
        return Response(FeedBackStudentSerializer(feedback_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        feedback_obj = self.get_object()
        reply_message = request.data.get('feedback_reply', '')
        feedback_obj.feedback_reply = reply_message
        feedback_obj.save()
        return Response({'message': 'Replied successfully', 'feedback': FeedBackStudentSerializer(feedback_obj).data})


class StaffFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedBackStaffsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if str(user.user_type) == '1':
            return FeedBackStaffs.objects.all().order_by('-id')
        elif str(user.user_type) == '2' and hasattr(user, 'staffs'):
            return FeedBackStaffs.objects.filter(staff_id=user.staffs).order_by('-id')
        return FeedBackStaffs.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'staffs'):
            return Response({'error': 'Only staff can submit feedback'}, status=status.HTTP_403_FORBIDDEN)
        feedback_text = request.data.get('feedback')
        feedback_obj = FeedBackStaffs.objects.create(
            staff_id=user.staffs,
            feedback=feedback_text,
            feedback_reply=""
        )
        return Response(FeedBackStaffsSerializer(feedback_obj).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        feedback_obj = self.get_object()
        reply_message = request.data.get('feedback_reply', '')
        feedback_obj.feedback_reply = reply_message
        feedback_obj.save()
        return Response({'message': 'Replied successfully', 'feedback': FeedBackStaffsSerializer(feedback_obj).data})


# Attendance APIs
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_students_for_attendance(request):
    subject_id = request.query_params.get('subject_id')
    session_year_id = request.query_params.get('session_year_id')

    if not subject_id or not session_year_id:
        return Response({'error': 'subject_id and session_year_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subject = Subjects.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)
        students = Students.objects.filter(course_id=subject.course_id, session_year_id=session_year)
        data = []
        for s in students:
            data.append({
                'id': s.id,
                'name': f"{s.admin.first_name} {s.admin.last_name}".strip() or s.admin.username,
                'email': s.admin.email
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_attendance(request):
    try:
        student_ids = request.data.get('student_ids', [])
        subject_id = request.data.get('subject_id')
        attendance_date = request.data.get('attendance_date')
        session_year_id = request.data.get('session_year_id')

        subject_obj = Subjects.objects.get(id=subject_id)
        session_year_obj = SessionYearModel.objects.get(id=session_year_id)
        attendance = Attendance.objects.create(
            subject_id=subject_obj,
            attendance_date=attendance_date,
            session_year_id=session_year_obj
        )

        for stud in student_ids:
            stud_obj = Students.objects.get(id=stud.get('id'))
            AttendanceReport.objects.create(
                student_id=stud_obj,
                attendance_id=attendance,
                status=stud.get('status', False)
            )

        return Response({'message': 'Attendance saved successfully', 'attendance_id': attendance.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_attendance_dates(request):
    subject_id = request.query_params.get('subject_id')
    session_year_id = request.query_params.get('session_year_id')

    if not subject_id or not session_year_id:
        return Response({'error': 'subject_id and session_year_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        attendances = Attendance.objects.filter(subject_id=subject_id, session_year_id=session_year_id)
        data = [{'id': a.id, 'attendance_date': str(a.attendance_date)} for a in attendances]
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_attendance_student_reports(request):
    attendance_id = request.query_params.get('attendance_id')
    if not attendance_id:
        return Response({'error': 'attendance_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        reports = AttendanceReport.objects.filter(attendance_id=attendance_id)
        data = []
        for r in reports:
            data.append({
                'id': r.id,
                'student_id': r.student_id.id,
                'name': f"{r.student_id.admin.first_name} {r.student_id.admin.last_name}".strip() or r.student_id.admin.username,
                'status': r.status
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_attendance_data(request):
    student_data = request.data.get('student_data', [])
    try:
        for stud in student_data:
            report_id = stud.get('id')
            status_val = stud.get('status')
            report = AttendanceReport.objects.get(id=report_id)
            report.status = status_val
            report.save()
        return Response({'message': 'Attendance updated successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_view_attendance(request):
    user = request.user
    if not hasattr(user, 'students'):
        return Response({'error': 'Only students can view their attendance history'}, status=status.HTTP_403_FORBIDDEN)

    subject_id = request.query_params.get('subject_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    student_obj = user.students
    reports_query = AttendanceReport.objects.filter(student_id=student_obj)

    if subject_id:
        reports_query = reports_query.filter(attendance_id__subject_id=subject_id)
    if start_date and end_date:
        reports_query = reports_query.filter(attendance_id__attendance_date__range=[start_date, end_date])

    data = []
    for r in reports_query.order_by('-attendance_id__attendance_date'):
        data.append({
            'id': r.id,
            'subject_name': r.attendance_id.subject_id.subject_name,
            'attendance_date': str(r.attendance_id.attendance_date),
            'status': r.status
        })

    return Response(data)


class StudentResultViewSet(viewsets.ModelViewSet):
    serializer_class = StudentResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentResult.objects.all().order_by('-created_at')

        # Role-based scoping
        if str(user.user_type) == '2' and hasattr(user, 'staffs'):
            # Staff only sees results for subjects they teach
            subjects = Subjects.objects.filter(staff_id=user)
            queryset = queryset.filter(subject_id__in=subjects)
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            # Student only sees their own results
            queryset = queryset.filter(student_id=user.students)

        # Filters
        course_id = self.request.query_params.get('course_id')
        subject_id = self.request.query_params.get('subject_id')
        student_id = self.request.query_params.get('student_id')
        if course_id:
            queryset = queryset.filter(student_id__course_id=course_id)
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_students_for_results(request):
    subject_id = request.query_params.get('subject_id')
    session_year_id = request.query_params.get('session_year_id')

    if not subject_id or not session_year_id:
        return Response({'error': 'subject_id and session_year_id are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subject = Subjects.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)
        students = Students.objects.filter(course_id=subject.course_id, session_year_id=session_year)

        data = []
        for s in students:
            # Check if result already exists
            existing_result = StudentResult.objects.filter(student_id=s, subject_id=subject).first()
            data.append({
                'student_id': s.id,
                'name': f"{s.admin.first_name} {s.admin.last_name}".strip() or s.admin.username,
                'username': s.admin.username,
                'exam_marks': existing_result.subject_exam_marks if existing_result else 0,
                'assignment_marks': existing_result.subject_assignment_marks if existing_result else 0,
                'result_id': existing_result.id if existing_result else None
            })
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_student_results(request):
    subject_id = request.data.get('subject_id')
    results_list = request.data.get('student_results', [])

    if not subject_id:
        return Response({'error': 'subject_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        subject = Subjects.objects.get(id=subject_id)
        updated_count = 0
        for item in results_list:
            student_id = item.get('student_id')
            exam_marks = float(item.get('exam_marks', 0))
            assignment_marks = float(item.get('assignment_marks', 0))

            student = Students.objects.get(id=student_id)
            StudentResult.objects.update_or_create(
                student_id=student,
                subject_id=subject,
                defaults={
                    'subject_exam_marks': exam_marks,
                    'subject_assignment_marks': assignment_marks
                }
            )
            updated_count += 1

        return Response({'message': f'Results for {updated_count} students saved successfully.'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_view_results(request):
    user = request.user
    if not hasattr(user, 'students'):
        return Response({'error': 'Only students can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)

    student = user.students
    results = StudentResult.objects.filter(student_id=student).order_by('-created_at')
    serializer = StudentResultSerializer(results, many=True)

    # Compute transcript summaries
    total_subjects = results.count()
    if total_subjects > 0:
        total_score_sum = sum([float(r.subject_exam_marks) + float(r.subject_assignment_marks) for r in results])
        average_score = round(total_score_sum / total_subjects, 2)
        passed_subjects = sum([1 for r in results if (float(r.subject_exam_marks) + float(r.subject_assignment_marks)) >= 50])
    else:
        average_score = 0.0
        passed_subjects = 0

    return Response({
        'results': serializer.data,
        'summary': {
            'total_subjects': total_subjects,
            'passed_subjects': passed_subjects,
            'failed_subjects': total_subjects - passed_subjects,
            'average_score': average_score
        }
    })


# -------------------------------------------------------------
# In-App Notifications & Broadcasts
# -------------------------------------------------------------

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_notifications_view(request):
    user = request.user
    if not hasattr(user, 'students'):
        return Response({'error': 'Only students can view student notifications'}, status=status.HTTP_403_FORBIDDEN)

    notifications = NotificationStudent.objects.filter(student_id=user.students).order_by('-created_at')
    serializer = NotificationStudentSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def staff_notifications_view(request):
    user = request.user
    if not hasattr(user, 'staffs'):
        return Response({'error': 'Only staff can view staff notifications'}, status=status.HTTP_403_FORBIDDEN)

    notifications = NotificationStaffs.objects.filter(staff_id=user.staffs).order_by('-created_at')
    serializer = NotificationStaffsSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def broadcast_to_students(request):
    user = request.user
    if str(user.user_type) != '1':
        return Response({'error': 'Only administrators can broadcast notifications'}, status=status.HTTP_403_FORBIDDEN)

    message = request.data.get('message', '').strip()
    target_type = request.data.get('target_type', 'all') # 'all' or 'course'
    course_id = request.data.get('course_id')

    if not message:
        return Response({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

    students_query = Students.objects.all()
    if target_type == 'course' and course_id:
        students_query = students_query.filter(course_id=course_id)

    recipient_count = 0
    notifications = []
    for s in students_query:
        notifications.append(NotificationStudent(student_id=s, message=message))
        recipient_count += 1

    if notifications:
        NotificationStudent.objects.bulk_create(notifications)

    return Response({
        'message': f'Announcement broadcasted successfully to {recipient_count} student(s).',
        'recipient_count': recipient_count
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def broadcast_to_staff(request):
    user = request.user
    if str(user.user_type) != '1':
        return Response({'error': 'Only administrators can broadcast notifications'}, status=status.HTTP_403_FORBIDDEN)

    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Message content is required'}, status=status.HTTP_400_BAD_REQUEST)

    staff_members = Staffs.objects.all()
    recipient_count = 0
    notifications = []
    for st in staff_members:
        notifications.append(NotificationStaffs(staff_id=st, message=message))
        recipient_count += 1

    if notifications:
        NotificationStaffs.objects.bulk_create(notifications)

    return Response({
        'message': f'Announcement broadcasted successfully to {recipient_count} staff member(s).',
        'recipient_count': recipient_count
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_notifications_history(request):
    user = request.user
    if str(user.user_type) != '1':
        return Response({'error': 'Only administrators can view broadcast logs'}, status=status.HTTP_403_FORBIDDEN)

    student_notifs = NotificationStudent.objects.all().order_by('-created_at')[:50]
    staff_notifs = NotificationStaffs.objects.all().order_by('-created_at')[:50]

    return Response({
        'student_notifications': NotificationStudentSerializer(student_notifs, many=True).data,
        'staff_notifications': NotificationStaffsSerializer(staff_notifs, many=True).data
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_student_notification(request, pk):
    user = request.user
    try:
        if str(user.user_type) == '1':
            notif = NotificationStudent.objects.get(id=pk)
        elif str(user.user_type) == '3':
            notif = NotificationStudent.objects.get(id=pk, student_id=user.students)
        else:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        notif.delete()
        return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except NotificationStudent.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_staff_notification(request, pk):
    user = request.user
    try:
        if str(user.user_type) == '1':
            notif = NotificationStaffs.objects.get(id=pk)
        elif str(user.user_type) == '2':
            notif = NotificationStaffs.objects.get(id=pk, staff_id=user.staffs)
        else:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        notif.delete()
        return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except NotificationStaffs.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


# -------------------------------------------------------------
# Student Fee & Payment Management
# -------------------------------------------------------------

class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all().order_by('-created_at')
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        cached = cache.get(FEE_STRUCTURES_CACHE_KEY)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(FEE_STRUCTURES_CACHE_KEY, response.data, timeout=600)
        return response

    def create(self, request, *args, **kwargs):
        if str(request.user.user_type) != '1':
            return Response({'error': 'Only admins can create fee structures'}, status=status.HTTP_403_FORBIDDEN)
        res = super().create(request, *args, **kwargs)
        invalidate_fee_structures_cache()
        return res

    def update(self, request, *args, **kwargs):
        if str(request.user.user_type) != '1':
            return Response({'error': 'Only admins can update fee structures'}, status=status.HTTP_403_FORBIDDEN)
        res = super().update(request, *args, **kwargs)
        invalidate_fee_structures_cache()
        return res

    def destroy(self, request, *args, **kwargs):
        if str(request.user.user_type) != '1':
            return Response({'error': 'Only admins can delete fee structures'}, status=status.HTTP_403_FORBIDDEN)
        res = super().destroy(request, *args, **kwargs)
        invalidate_fee_structures_cache()
        return res


class StudentFeeInvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentFeeInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentFeeInvoice.objects.all().order_by('-created_at')

        if str(user.user_type) == '3' and hasattr(user, 'students'):
            return queryset.filter(student_id=user.students)
        elif str(user.user_type) == '1':
            course_id = self.request.query_params.get('course_id')
            payment_status = self.request.query_params.get('payment_status')
            student_id = self.request.query_params.get('student_id')

            if course_id:
                queryset = queryset.filter(student_id__course_id=course_id)
            if payment_status:
                queryset = queryset.filter(payment_status=payment_status)
            if student_id:
                queryset = queryset.filter(student_id=student_id)
            return queryset
        return queryset.none()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_fee_invoices(request):
    user = request.user
    if str(user.user_type) != '1':
        return Response({'error': 'Only admins can generate fee invoices'}, status=status.HTTP_403_FORBIDDEN)

    fee_structure_id = request.data.get('fee_structure_id')
    if not fee_structure_id:
        return Response({'error': 'fee_structure_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        fee_structure = FeeStructure.objects.get(id=fee_structure_id)
    except FeeStructure.DoesNotExist:
        return Response({'error': 'Fee structure not found'}, status=status.HTTP_404_NOT_FOUND)

    # Find enrolled students for the course and session year
    students = Students.objects.filter(
        course_id=fee_structure.course_id,
        session_year_id=fee_structure.session_year_id
    )

    invoices_created = 0
    total_fee = fee_structure.total_amount

    for s in students:
        _, created = StudentFeeInvoice.objects.get_or_create(
            student_id=s,
            fee_structure_id=fee_structure,
            defaults={
                'total_amount': total_fee,
                'paid_amount': 0.0,
                'payment_status': 'Unpaid'
            }
        )
        if created:
            invoices_created += 1

    return Response({
        'message': f'Successfully generated {invoices_created} fee invoice(s).',
        'invoices_created': invoices_created
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def collect_fee_payment(request):
    user = request.user
    if str(user.user_type) != '1':
        return Response({'error': 'Only admins can collect payments'}, status=status.HTTP_403_FORBIDDEN)

    invoice_id = request.data.get('invoice_id')
    amount_paid = request.data.get('amount_paid')
    payment_method = request.data.get('payment_method', 'Cash')
    transaction_id = request.data.get('transaction_id', '')
    remarks = request.data.get('remarks', '')

    if not invoice_id or amount_paid is None:
        return Response({'error': 'invoice_id and amount_paid are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount_paid = float(amount_paid)
        if amount_paid <= 0:
            return Response({'error': 'Payment amount must be greater than 0'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Invalid amount_paid format'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invoice = StudentFeeInvoice.objects.get(id=invoice_id)
    except StudentFeeInvoice.DoesNotExist:
        return Response({'error': 'Invoice not found'}, status=status.HTTP_404_NOT_FOUND)

    current_balance = invoice.balance_amount
    if amount_paid > current_balance:
        return Response({
            'error': f'Payment amount ({amount_paid}) exceeds outstanding balance ({current_balance})'
        }, status=status.HTTP_400_BAD_REQUEST)

    payment = FeePayment.objects.create(
        invoice_id=invoice,
        amount_paid=amount_paid,
        payment_method=payment_method,
        transaction_id=transaction_id,
        remarks=remarks
    )

    new_paid_amount = float(invoice.paid_amount) + amount_paid
    invoice.paid_amount = new_paid_amount
    if new_paid_amount >= float(invoice.total_amount):
        invoice.payment_status = 'Paid'
    elif new_paid_amount > 0:
        invoice.payment_status = 'Partial'
    invoice.save()

    return Response({
        'message': 'Payment recorded successfully',
        'payment': FeePaymentSerializer(payment).data,
        'invoice': StudentFeeInvoiceSerializer(invoice).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def student_my_invoices_view(request):
    user = request.user
    if not hasattr(user, 'students'):
        return Response({'error': 'Only students can view their fee invoices'}, status=status.HTTP_403_FORBIDDEN)

    invoices = StudentFeeInvoice.objects.filter(student_id=user.students).order_by('-created_at')
    serializer = StudentFeeInvoiceSerializer(invoices, many=True)

    total_billed = sum([float(inv.total_amount) for inv in invoices])
    total_paid = sum([float(inv.paid_amount) for inv in invoices])
    total_balance = total_billed - total_paid
    unpaid_count = sum([1 for inv in invoices if inv.payment_status != 'Paid'])

    return Response({
        'invoices': serializer.data,
        'summary': {
            'total_billed': round(total_billed, 2),
            'total_paid': round(total_paid, 2),
            'total_balance': round(max(0.0, total_balance), 2),
            'unpaid_invoices_count': unpaid_count
        }
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fee_receipt_detail(request, pk):
    try:
        payment = FeePayment.objects.get(id=pk)
    except FeePayment.DoesNotExist:
        return Response({'error': 'Payment receipt not found'}, status=status.HTTP_404_NOT_FOUND)

    invoice = payment.invoice_id
    student = invoice.student_id
    user = request.user

    # Object-level permission: Admin or the student themselves
    if str(user.user_type) == '3' and student.admin != user:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    return Response({
        'receipt_no': f"REC-{payment.id:06d}",
        'payment_id': payment.id,
        'payment_date': payment.payment_date,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'amount_paid': float(payment.amount_paid),
        'remarks': payment.remarks,
        'student': {
            'id': student.id,
            'name': f"{student.admin.first_name} {student.admin.last_name}".strip() or student.admin.username,
            'username': student.admin.username,
            'email': student.admin.email,
            'course': student.course_id.course_name if student.course_id else '',
            'session': f"{student.session_year_id.session_start_year} TO {student.session_year_id.session_end_year}" if student.session_year_id else ''
        },
        'fee': {
            'invoice_id': invoice.id,
            'fee_name': invoice.fee_structure_id.fee_name,
            'total_amount': float(invoice.total_amount),
            'total_paid_to_date': float(invoice.paid_amount),
            'remaining_balance': float(invoice.balance_amount),
            'payment_status': invoice.payment_status,
            'due_date': invoice.fee_structure_id.due_date
        }
    })


# -------------------------------------------------------------
# Student Document Management
# -------------------------------------------------------------

class StudentDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = StudentDocument.objects.all().order_by('-id')

        if str(user.user_type) == '3' and hasattr(user, 'students'):
            return queryset.filter(student_id=user.students)
        elif str(user.user_type) in ['1', '2']: # Admin or Staff
            student_id = self.request.query_params.get('student_id')
            status_param = self.request.query_params.get('status')
            doc_type = self.request.query_params.get('document_type')
            course_id = self.request.query_params.get('course_id')

            if student_id:
                queryset = queryset.filter(student_id_id=student_id)
            if status_param is not None:
                queryset = queryset.filter(verification_status=status_param)
            if doc_type:
                queryset = queryset.filter(document_type=doc_type)
            if course_id:
                queryset = queryset.filter(student_id__course_id_id=course_id)
            return queryset
        return StudentDocument.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user
        student_id_param = request.data.get('student_id')

        if str(user.user_type) == '3' and hasattr(user, 'students'):
            student = user.students
        elif str(user.user_type) == '1' and student_id_param:
            try:
                student = Students.objects.get(id=student_id_param)
            except Students.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Student context required'}, status=status.HTTP_400_BAD_REQUEST)

        document_name = request.data.get('document_name')
        document_type = request.data.get('document_type', 'other')
        document_file = request.FILES.get('document_file')

        if not document_name or not document_file:
            return Response({'error': 'Document name and file are required'}, status=status.HTTP_400_BAD_REQUEST)

        doc = StudentDocument.objects.create(
            student_id=student,
            document_name=document_name,
            document_type=document_type,
            document_file=document_file,
            verification_status=0
        )
        return Response(StudentDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        doc = self.get_object()
        user = request.user

        if str(user.user_type) == '3' and hasattr(user, 'students'):
            if doc.student_id != user.students:
                return Response({'error': 'Unauthorized to delete this document'}, status=status.HTTP_403_FORBIDDEN)
        elif str(user.user_type) not in ['1']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        doc.delete()
        return Response({'message': 'Document deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        user = request.user
        if str(user.user_type) not in ['1', '2']: # Admin or Staff
            return Response({'error': 'Only administrators or staff can verify documents'}, status=status.HTTP_403_FORBIDDEN)

        doc = self.get_object()
        new_status = request.data.get('verification_status')
        rejection_reason = request.data.get('rejection_reason', '')

        if new_status is None:
            return Response({'error': 'verification_status is required (1: Approved, 2: Rejected)'}, status=status.HTTP_400_BAD_REQUEST)

        doc.verification_status = int(new_status)
        if int(new_status) == 2:
            doc.rejection_reason = rejection_reason
        elif int(new_status) == 1:
            doc.rejection_reason = ''
        doc.save()

        return Response(StudentDocumentSerializer(doc).data, status=status.HTTP_200_OK)


# ==========================================
# Export & Reporting Engine Endpoints (PDF, Excel, CSV, Paginated Previews)
# ==========================================
from django.http import HttpResponse
from datetime import datetime
import io
import csv
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from student_management_app.report_utils import (
    generate_student_report_card_pdf,
    generate_attendance_excel_bytes,
    generate_fees_excel_bytes,
    generate_students_excel_bytes,
    generate_results_excel_bytes,
    calculate_grade
)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_report_card_pdf_view(request):
    user = request.user
    u_type = str(user.user_type)

    if u_type == '3':
        # Student requesting
        if not hasattr(user, 'students'):
            return Response({'error': 'Student profile not found'}, status=status.HTTP_404_NOT_FOUND)
        student = user.students
        target_student_id = request.query_params.get('student_id')
        if target_student_id and str(target_student_id) != str(student.id):
            return Response({'error': 'You are not authorized to access other students\' report cards'}, status=status.HTTP_403_FORBIDDEN)
    elif u_type in ['1', '2']: # Admin or Staff
        target_student_id = request.query_params.get('student_id')
        if target_student_id:
            try:
                student = Students.objects.get(id=target_student_id)
            except Students.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            student = Students.objects.first()
            if not student:
                return Response({'error': 'No students found in system'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    pdf_bytes = generate_student_report_card_pdf(student)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"report_card_{student.admin.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reports_preview_view(request):
    """
    Returns server-side paginated and searched data records for reporting dashboards.
    Supported types: 'students', 'attendance', 'fees', 'results'.
    """
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can view reports'}, status=status.HTTP_403_FORBIDDEN)

    report_type = request.query_params.get('type', 'students')
    search = request.query_params.get('search', '').strip()
    course_id = request.query_params.get('course_id')
    subject_id = request.query_params.get('subject_id')
    session_year_id = request.query_params.get('session_year_id')
    status_filter = request.query_params.get('status')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    paginator = CustomPagination()

    if report_type == 'attendance':
        qs = AttendanceReport.objects.all().select_related(
            'student_id__admin', 'student_id__course_id', 'attendance_id__subject_id', 'attendance_id__session_year_id'
        ).order_by('-attendance_id__attendance_date', '-id')

        if search:
            qs = qs.filter(
                Q(student_id__admin__username__icontains=search) |
                Q(student_id__admin__first_name__icontains=search) |
                Q(student_id__admin__last_name__icontains=search) |
                Q(attendance_id__subject_id__subject_name__icontains=search)
            )
        if subject_id:
            qs = qs.filter(attendance_id__subject_id=subject_id)
        if session_year_id:
            qs = qs.filter(attendance_id__session_year_id=session_year_id)
        if course_id:
            qs = qs.filter(student_id__course_id=course_id)
        if start_date and end_date:
            qs = qs.filter(attendance_id__attendance_date__range=[start_date, end_date])

        page = paginator.paginate_queryset(qs, request)
        data = []
        for r in page:
            att = r.attendance_id
            stud = r.student_id
            admin_user = stud.admin if stud else None
            data.append({
                'id': r.id,
                'student_id': stud.id if stud else None,
                'username': admin_user.username if admin_user else "",
                'full_name': f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "",
                'subject_name': att.subject_id.subject_name if att and att.subject_id else "",
                'attendance_date': att.attendance_date.strftime("%Y-%m-%d") if att and att.attendance_date else "",
                'status': r.status,
                'status_label': 'Present' if r.status else 'Absent'
            })
        return paginator.get_paginated_response(data)

    elif report_type == 'fees':
        qs = StudentFeeInvoice.objects.all().select_related(
            'student_id__admin', 'student_id__course_id', 'fee_structure_id'
        ).order_by('-created_at')

        if search:
            qs = qs.filter(
                Q(student_id__admin__username__icontains=search) |
                Q(student_id__admin__first_name__icontains=search) |
                Q(student_id__admin__last_name__icontains=search) |
                Q(fee_structure_id__fee_name__icontains=search)
            )
        if course_id:
            qs = qs.filter(student_id__course_id=course_id)
        if status_filter:
            qs = qs.filter(payment_status__iexact=status_filter)

        page = paginator.paginate_queryset(qs, request)
        data = []
        for inv in page:
            stud = inv.student_id
            admin_user = stud.admin if stud else None
            data.append({
                'id': inv.id,
                'student_id': stud.id if stud else None,
                'username': admin_user.username if admin_user else "",
                'full_name': f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "",
                'course_name': stud.course_id.course_name if stud and stud.course_id else "",
                'fee_name': inv.fee_structure_id.fee_name if inv.fee_structure_id else "",
                'total_amount': float(inv.total_amount),
                'paid_amount': float(inv.paid_amount),
                'balance_amount': float(inv.balance_amount),
                'payment_status': inv.payment_status,
                'due_date': inv.fee_structure_id.due_date.strftime("%Y-%m-%d") if inv.fee_structure_id and inv.fee_structure_id.due_date else ""
            })
        return paginator.get_paginated_response(data)

    elif report_type == 'results':
        qs = StudentResult.objects.all().select_related(
            'student_id__admin', 'student_id__course_id', 'subject_id'
        ).order_by('-id')

        if search:
            qs = qs.filter(
                Q(student_id__admin__username__icontains=search) |
                Q(student_id__admin__first_name__icontains=search) |
                Q(student_id__admin__last_name__icontains=search) |
                Q(subject_id__subject_name__icontains=search)
            )
        if subject_id:
            qs = qs.filter(subject_id=subject_id)
        if course_id:
            qs = qs.filter(student_id__course_id=course_id)

        page = paginator.paginate_queryset(qs, request)
        data = []
        for res in page:
            stud = res.student_id
            admin_user = stud.admin if stud else None
            total = float(res.subject_exam_marks or 0) + float(res.subject_assignment_marks or 0)
            grade, gpa, standing = calculate_grade(total)
            data.append({
                'id': res.id,
                'student_id': stud.id if stud else None,
                'username': admin_user.username if admin_user else "",
                'full_name': f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "",
                'course_name': stud.course_id.course_name if stud and stud.course_id else "",
                'subject_name': res.subject_id.subject_name if res.subject_id else "",
                'exam_marks': float(res.subject_exam_marks or 0),
                'assignment_marks': float(res.subject_assignment_marks or 0),
                'total_marks': total,
                'grade': grade,
                'standing': standing,
                'status': 'Pass' if total >= 50 else 'Fail'
            })
        return paginator.get_paginated_response(data)

    else: # Default: 'students'
        qs = Students.objects.all().select_related(
            'admin', 'course_id', 'session_year_id'
        ).order_by('-id')

        if search:
            qs = qs.filter(
                Q(admin__username__icontains=search) |
                Q(admin__first_name__icontains=search) |
                Q(admin__last_name__icontains=search) |
                Q(admin__email__icontains=search) |
                Q(course_id__course_name__icontains=search)
            )
        if course_id:
            qs = qs.filter(course_id=course_id)
        if session_year_id:
            qs = qs.filter(session_year_id=session_year_id)

        page = paginator.paginate_queryset(qs, request)
        data = []
        for stud in page:
            admin_user = stud.admin
            sess = stud.session_year_id
            data.append({
                'id': stud.id,
                'username': admin_user.username if admin_user else "",
                'full_name': f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "",
                'email': admin_user.email if admin_user else "",
                'gender': stud.gender or "",
                'course_name': stud.course_id.course_name if stud.course_id else "",
                'session_year': f"{sess.session_start_year} - {sess.session_end_year}" if sess else "",
                'address': stud.address or "",
                'created_at': stud.created_at.strftime("%Y-%m-%d") if stud.created_at else ""
            })
        return paginator.get_paginated_response(data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_attendance_csv_view(request):
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can export attendance reports'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    subject_id = request.query_params.get('subject_id')
    session_year_id = request.query_params.get('session_year_id')
    course_id = request.query_params.get('course_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    reports = AttendanceReport.objects.all().select_related(
        'student_id__admin', 'student_id__course_id', 'attendance_id__subject_id', 'attendance_id__session_year_id'
    ).order_by('-attendance_id__attendance_date')

    if search:
        reports = reports.filter(
            Q(student_id__admin__username__icontains=search) |
            Q(student_id__admin__first_name__icontains=search) |
            Q(student_id__admin__last_name__icontains=search) |
            Q(attendance_id__subject_id__subject_name__icontains=search)
        )
    if subject_id:
        reports = reports.filter(attendance_id__subject_id=subject_id)
    if session_year_id:
        reports = reports.filter(attendance_id__session_year_id=session_year_id)
    if course_id:
        reports = reports.filter(student_id__course_id=course_id)
    if start_date and end_date:
        reports = reports.filter(attendance_id__attendance_date__range=[start_date, end_date])

    # Generate CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Attendance Date", "Subject", "Course", "Session Year",
        "Student ID", "Student Name", "Username", "Status"
    ])

    for r in reports:
        att = r.attendance_id
        stud = r.student_id
        admin_user = stud.admin if stud else None

        writer.writerow([
            str(att.attendance_date) if att else "N/A",
            att.subject_id.subject_name if (att and att.subject_id) else "N/A",
            stud.course_id.course_name if (stud and stud.course_id) else "N/A",
            f"{att.session_year_id.session_start_year} - {att.session_year_id.session_end_year}" if (att and att.session_year_id) else "N/A",
            stud.id if stud else "N/A",
            f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "N/A",
            admin_user.username if admin_user else "N/A",
            "Present" if r.status else "Absent"
        ])

    csv_content = output.getvalue()
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_attendance_excel_view(request):
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can export attendance reports'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    subject_id = request.query_params.get('subject_id')
    course_id = request.query_params.get('course_id')
    session_year_id = request.query_params.get('session_year_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    reports = AttendanceReport.objects.all().select_related(
        'student_id__admin', 'student_id__course_id', 'attendance_id__subject_id', 'attendance_id__session_year_id'
    ).order_by('-attendance_id__attendance_date')

    if search:
        reports = reports.filter(
            Q(student_id__admin__username__icontains=search) |
            Q(student_id__admin__first_name__icontains=search) |
            Q(student_id__admin__last_name__icontains=search) |
            Q(attendance_id__subject_id__subject_name__icontains=search)
        )
    if subject_id:
        reports = reports.filter(attendance_id__subject_id=subject_id)
    if course_id:
        reports = reports.filter(student_id__course_id=course_id)
    if session_year_id:
        reports = reports.filter(attendance_id__session_year_id=session_year_id)
    if start_date and end_date:
        reports = reports.filter(attendance_id__attendance_date__range=[start_date, end_date])

    content = generate_attendance_excel_bytes(reports)
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="attendance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_fees_csv_view(request):
    user = request.user
    if str(user.user_type) != '1': # Admin Only
        return Response({'error': 'Only administrators can export fee and payment summaries'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    course_id = request.query_params.get('course_id')
    status_filter = request.query_params.get('status')

    invoices = StudentFeeInvoice.objects.all().select_related(
        'student_id__admin', 'student_id__course_id', 'fee_structure_id'
    ).order_by('-created_at')

    if search:
        invoices = invoices.filter(
            Q(student_id__admin__username__icontains=search) |
            Q(student_id__admin__first_name__icontains=search) |
            Q(student_id__admin__last_name__icontains=search) |
            Q(fee_structure_id__fee_name__icontains=search)
        )
    if course_id:
        invoices = invoices.filter(student_id__course_id=course_id)
    if status_filter:
        invoices = invoices.filter(payment_status__iexact=status_filter)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Invoice ID", "Student ID", "Student Name", "Username",
        "Course", "Fee Structure", "Total Amount", "Paid Amount",
        "Balance Due", "Status", "Created Date"
    ])

    for inv in invoices:
        stud = inv.student_id
        admin_user = stud.admin if stud else None
        writer.writerow([
            inv.id,
            stud.id if stud else "N/A",
            f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "N/A",
            admin_user.username if admin_user else "N/A",
            stud.course_id.course_name if (stud and stud.course_id) else "N/A",
            inv.fee_structure_id.fee_name if inv.fee_structure_id else "N/A",
            f"{inv.total_amount:.2f}",
            f"{inv.paid_amount:.2f}",
            f"{inv.balance_amount:.2f}",
            inv.payment_status,
            inv.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    csv_content = output.getvalue()
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="fee_invoices_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_fees_excel_view(request):
    user = request.user
    if str(user.user_type) != '1':
        return Response({'error': 'Only administrators can export fee and payment summaries'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    course_id = request.query_params.get('course_id')
    status_filter = request.query_params.get('status')

    invoices = StudentFeeInvoice.objects.all().select_related(
        'student_id__admin', 'student_id__course_id', 'fee_structure_id'
    ).order_by('-created_at')

    if search:
        invoices = invoices.filter(
            Q(student_id__admin__username__icontains=search) |
            Q(student_id__admin__first_name__icontains=search) |
            Q(student_id__admin__last_name__icontains=search) |
            Q(fee_structure_id__fee_name__icontains=search)
        )
    if course_id:
        invoices = invoices.filter(student_id__course_id=course_id)
    if status_filter:
        invoices = invoices.filter(payment_status__iexact=status_filter)

    content = generate_fees_excel_bytes(invoices)
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="fee_invoices_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_students_csv_view(request):
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can export student rosters'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    course_id = request.query_params.get('course_id')
    session_year_id = request.query_params.get('session_year_id')

    students = Students.objects.all().select_related('admin', 'course_id', 'session_year_id').order_by('-id')

    if search:
        students = students.filter(
            Q(admin__username__icontains=search) |
            Q(admin__first_name__icontains=search) |
            Q(admin__last_name__icontains=search) |
            Q(admin__email__icontains=search) |
            Q(course_id__course_name__icontains=search)
        )
    if course_id:
        students = students.filter(course_id=course_id)
    if session_year_id:
        students = students.filter(session_year_id=session_year_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Username", "Full Name", "Email",
        "Gender", "Course", "Session Year", "Address", "Created Date"
    ])

    for stud in students:
        admin_user = stud.admin
        sess = stud.session_year_id
        writer.writerow([
            stud.id,
            admin_user.username if admin_user else "N/A",
            f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "N/A",
            admin_user.email if admin_user else "N/A",
            stud.gender or "N/A",
            stud.course_id.course_name if stud.course_id else "N/A",
            f"{sess.session_start_year} - {sess.session_end_year}" if sess else "N/A",
            stud.address or "N/A",
            stud.created_at.strftime("%Y-%m-%d") if stud.created_at else "N/A"
        ])

    csv_content = output.getvalue()
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_students_excel_view(request):
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can export student rosters'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    course_id = request.query_params.get('course_id')
    session_year_id = request.query_params.get('session_year_id')

    students = Students.objects.all().select_related('admin', 'course_id', 'session_year_id').order_by('-id')

    if search:
        students = students.filter(
            Q(admin__username__icontains=search) |
            Q(admin__first_name__icontains=search) |
            Q(admin__last_name__icontains=search) |
            Q(admin__email__icontains=search) |
            Q(course_id__course_name__icontains=search)
        )
    if course_id:
        students = students.filter(course_id=course_id)
    if session_year_id:
        students = students.filter(session_year_id=session_year_id)

    content = generate_students_excel_bytes(students)
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="students_roster_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_results_csv_view(request):
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can export exam results'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    subject_id = request.query_params.get('subject_id')
    course_id = request.query_params.get('course_id')

    results = StudentResult.objects.all().select_related(
        'student_id__admin', 'student_id__course_id', 'subject_id'
    ).order_by('-id')

    if search:
        results = results.filter(
            Q(student_id__admin__username__icontains=search) |
            Q(student_id__admin__first_name__icontains=search) |
            Q(student_id__admin__last_name__icontains=search) |
            Q(subject_id__subject_name__icontains=search)
        )
    if subject_id:
        results = results.filter(subject_id=subject_id)
    if course_id:
        results = results.filter(student_id__course_id=course_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Result ID", "Student ID", "Username", "Student",
        "Course", "Subject", "Exam Marks", "Assignment Marks",
        "Total Score", "Grade", "Status"
    ])

    for res in results:
        stud = res.student_id
        admin_user = stud.admin if stud else None
        total = float(res.subject_exam_marks or 0) + float(res.subject_assignment_marks or 0)
        grade, _, _ = calculate_grade(total)
        writer.writerow([
            res.id,
            stud.id if stud else "N/A",
            admin_user.username if admin_user else "N/A",
            f"{admin_user.first_name} {admin_user.last_name}".strip() if admin_user else "N/A",
            stud.course_id.course_name if stud and stud.course_id else "N/A",
            res.subject_id.subject_name if res.subject_id else "N/A",
            float(res.subject_exam_marks or 0),
            float(res.subject_assignment_marks or 0),
            total,
            grade,
            "Pass" if total >= 50 else "Fail"
        ])

    csv_content = output.getvalue()
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="exam_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    return response


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def export_results_excel_view(request):
    user = request.user
    if str(user.user_type) not in ['1', '2']:
        return Response({'error': 'Only staff and administrators can export exam results'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    subject_id = request.query_params.get('subject_id')
    course_id = request.query_params.get('course_id')

    results = StudentResult.objects.all().select_related(
        'student_id__admin', 'student_id__course_id', 'subject_id'
    ).order_by('-id')

    if search:
        results = results.filter(
            Q(student_id__admin__username__icontains=search) |
            Q(student_id__admin__first_name__icontains=search) |
            Q(student_id__admin__last_name__icontains=search) |
            Q(subject_id__subject_name__icontains=search)
        )
    if subject_id:
        results = results.filter(subject_id=subject_id)
    if course_id:
        results = results.filter(student_id__course_id=course_id)

    content = generate_results_excel_bytes(results)
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="exam_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
    return response


# ==========================================
# Course Syllabus, Assignments & Submissions
# ==========================================
from django.utils import timezone

class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        u_type = str(user.user_type)

        if u_type == '1': # Admin
            queryset = Assignment.objects.all()
        elif u_type == '2' and hasattr(user, 'staffs'): # Staff
            subjects = Subjects.objects.filter(staff_id=user)
            queryset = Assignment.objects.filter(subject_id__in=subjects)
        elif u_type == '3' and hasattr(user, 'students'): # Student
            student = user.students
            if student.course_id:
                subjects = Subjects.objects.filter(course_id=student.course_id)
                queryset = Assignment.objects.filter(subject_id__in=subjects)
            else:
                queryset = Assignment.objects.none()
        else:
            queryset = Assignment.objects.none()

        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        return queryset.order_by('-deadline')

    def create(self, request, *args, **kwargs):
        user = request.user
        if str(user.user_type) not in ['1', '2']: # Only Admin or Staff
            return Response({'error': 'Only instructors and administrators can create assignments'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if str(user.user_type) not in ['1', '2']:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        assignment = self.get_object()
        user = request.user
        if str(user.user_type) not in ['1', '2']:
            return Response({'error': 'Only instructors can view assignment submissions'}, status=status.HTTP_403_FORBIDDEN)

        submissions = StudentAssignmentSubmission.objects.filter(assignment_id=assignment).select_related('student_id__admin', 'graded_by').order_by('-submitted_at')
        serializer = StudentAssignmentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        user = request.user
        if str(user.user_type) != '3' or not hasattr(user, 'students'):
            return Response({'error': 'Only students can submit assignments'}, status=status.HTTP_403_FORBIDDEN)

        assignment = self.get_object()
        student = user.students

        submission_file = request.FILES.get('submission_file')
        submission_text = request.data.get('submission_text', '')

        if not submission_file and not submission_text:
            return Response({'error': 'Please provide either a submission file or text response'}, status=status.HTTP_400_BAD_REQUEST)

        is_late = timezone.now() > assignment.deadline

        submission, created = StudentAssignmentSubmission.objects.update_or_create(
            assignment_id=assignment,
            student_id=student,
            defaults={
                'submission_file': submission_file if submission_file else None,
                'submission_text': submission_text,
                'is_late': is_late,
                'status': 'Submitted',
                'submitted_at': timezone.now()
            }
        )

        return Response(StudentAssignmentSubmissionSerializer(submission).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        user = request.user
        if str(user.user_type) != '3' or not hasattr(user, 'students'):
            return Response({'error': 'Only students can access their submissions'}, status=status.HTTP_403_FORBIDDEN)

        student = user.students
        submissions = StudentAssignmentSubmission.objects.filter(student_id=student).select_related('assignment_id__subject_id', 'graded_by').order_by('-submitted_at')
        serializer = StudentAssignmentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class StudentAssignmentSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentAssignmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if str(user.user_type) in ['1', '2']:
            return StudentAssignmentSubmission.objects.all().select_related('assignment_id', 'student_id__admin', 'graded_by').order_by('-submitted_at')
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            return StudentAssignmentSubmission.objects.filter(student_id=user.students).select_related('assignment_id', 'graded_by').order_by('-submitted_at')
        return StudentAssignmentSubmission.objects.none()

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        user = request.user
        if str(user.user_type) not in ['1', '2']: # Only Admin or Staff
            return Response({'error': 'Only instructors and administrators can grade submissions'}, status=status.HTTP_403_FORBIDDEN)

        submission = self.get_object()
        marks = request.data.get('marks_obtained')
        feedback = request.data.get('feedback_remarks', '')

        if marks is None:
            return Response({'error': 'marks_obtained is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            marks = float(marks)
        except ValueError:
            return Response({'error': 'marks_obtained must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

        submission.marks_obtained = marks
        submission.feedback_remarks = feedback
        submission.status = 'Graded'
        submission.graded_by = user
        submission.graded_at = timezone.now()
        submission.save()

        return Response(StudentAssignmentSubmissionSerializer(submission).data, status=status.HTTP_200_OK)






