import json
import datetime
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from student_management_app.models import (
    CustomUser, Admins, Staffs, Courses, Subjects, Students,
    SessionYearModel, Attendance, AttendanceReport,
    LeaveReportStudent, LeaveReportStaff,
    FeedBackStudent, FeedBackStaffs,
    StudentResult
)
from student_management_app.serializers import (
    CustomTokenObtainPairSerializer, UserSerializer,
    StaffSerializer, StudentSerializer, CourseSerializer, SubjectSerializer,
    SessionYearSerializer, AttendanceSerializer, AttendanceReportSerializer,
    LeaveReportStudentSerializer, LeaveReportStaffSerializer,
    FeedBackStudentSerializer, FeedBackStaffsSerializer,
    StudentResultSerializer
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
        elif str(user.user_type) == '3' and hasattr(user, 'students'):
            profile_data['id'] = user.students.id
            profile_data['address'] = user.students.address
            profile_data['gender'] = user.students.gender
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

        user.first_name = first_name
        user.last_name = last_name
        if password:
            user.set_password(password)
        user.save()

        if str(user.user_type) == '2' and hasattr(user, 'staffs') and address is not None:
            user.staffs.address = address
            user.staffs.save()
        elif str(user.user_type) == '3' and hasattr(user, 'students') and address is not None:
            user.students.address = address
            user.students.save()

        return Response({'message': 'Profile updated successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats_view(request):
    user = request.user
    user_type = str(user.user_type)

    if user_type == '1': # Admin
        return Response({
            'user_type': '1',
            'student_count': Students.objects.all().count(),
            'staff_count': Staffs.objects.all().count(),
            'course_count': Courses.objects.all().count(),
            'subject_count': Subjects.objects.all().count(),
            'pending_student_leaves': LeaveReportStudent.objects.filter(leave_status=0).count(),
            'pending_staff_leaves': LeaveReportStaff.objects.filter(leave_status=0).count(),
        })

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

        return Response({
            'user_type': '2',
            'students_count': students_count,
            'attendance_count': attendance_count,
            'leave_count': leave_count,
            'total_leave': total_leave,
            'subject_count': subject_count,
        })

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

        return Response({
            'user_type': '3',
            'total_attendance': total_attendance,
            'attendance_present': attendance_present,
            'attendance_absent': attendance_absent,
            'subjects_count': subjects_count,
            'leaves_applied': leaves_applied,
            'leaves_approved': leaves_approved,
        })

    return Response({'error': 'Unknown role'}, status=status.HTTP_400_BAD_REQUEST)


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staffs.objects.all().order_by('-id')
    serializer_class = StaffSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        staff = self.get_object()
        user = staff.admin
        user.delete() # Also deletes staff
        return Response({'message': 'Staff deleted successfully'}, status=status.HTTP_200_OK)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Students.objects.all().order_by('-id')
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        user = student.admin
        user.delete() # Also deletes student
        return Response({'message': 'Student deleted successfully'}, status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Courses.objects.all().order_by('-id')
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subjects.objects.all().order_by('-id')
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]


class SessionYearViewSet(viewsets.ModelViewSet):
    queryset = SessionYearModel.objects.all().order_by('-id')
    serializer_class = SessionYearSerializer
    permission_classes = [permissions.IsAuthenticated]


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

