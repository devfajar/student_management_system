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
    FeeStructure, StudentFeeInvoice, FeePayment
)
from student_management_app.serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    StaffSerializer, StudentSerializer, CourseSerializer, SubjectSerializer,
    SessionYearSerializer, AttendanceSerializer, AttendanceReportSerializer,
    LeaveReportStudentSerializer, LeaveReportStaffSerializer,
    FeedBackStudentSerializer, FeedBackStaffsSerializer,
    StudentResultSerializer, NotificationStudentSerializer, NotificationStaffsSerializer,
    FeeStructureSerializer, StudentFeeInvoiceSerializer, FeePaymentSerializer
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



