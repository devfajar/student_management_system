from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from student_management_app.api_views import (
    CustomTokenObtainPairView, current_user_view, dashboard_stats_view,
    StaffViewSet, StudentViewSet, CourseViewSet, SubjectViewSet,
    SessionYearViewSet, StudentLeaveViewSet, StaffLeaveViewSet,
    StudentFeedbackViewSet, StaffFeedbackViewSet, StudentResultViewSet,
    get_students_for_attendance, save_attendance,
    get_attendance_dates, get_attendance_student_reports,
    update_attendance_data, student_view_attendance,
    get_students_for_results, save_student_results, student_view_results,
    student_notifications_view, staff_notifications_view,
    broadcast_to_students, broadcast_to_staff,
    admin_notifications_history, delete_student_notification, delete_staff_notification
)

router = DefaultRouter()
router.register(r'staff', StaffViewSet, basename='staff')
router.register(r'students', StudentViewSet, basename='students')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'sessions', SessionYearViewSet, basename='sessions')
router.register(r'student-leaves', StudentLeaveViewSet, basename='student-leaves')
router.register(r'staff-leaves', StaffLeaveViewSet, basename='staff-leaves')
router.register(r'student-feedback', StudentFeedbackViewSet, basename='student-feedback')
router.register(r'staff-feedback', StaffFeedbackViewSet, basename='staff-feedback')
router.register(r'results', StudentResultViewSet, basename='results')

urlpatterns = [
    # API Documentation (Swagger & Redoc)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Auth
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', current_user_view, name='current_user'),

    # Dashboard
    path('dashboard/stats/', dashboard_stats_view, name='dashboard_stats'),

    # Attendance
    path('attendance/get-students/', get_students_for_attendance, name='attendance_get_students'),
    path('attendance/save-attendance/', save_attendance, name='attendance_save'),
    path('attendance/get-dates/', get_attendance_dates, name='attendance_get_dates'),
    path('attendance/get-reports/', get_attendance_student_reports, name='attendance_get_reports'),
    path('attendance/update-attendance/', update_attendance_data, name='attendance_update'),
    path('attendance/student-view/', student_view_attendance, name='student_attendance_view'),

    # Results & Grading
    path('results/get-students/', get_students_for_results, name='results_get_students'),
    path('results/save-results/', save_student_results, name='results_save'),
    path('results/my-results/', student_view_results, name='results_student_view'),

    # In-App Notifications & Broadcasts
    path('notifications/student/', student_notifications_view, name='notifications_student'),
    path('notifications/staff/', staff_notifications_view, name='notifications_staff'),
    path('notifications/broadcast-students/', broadcast_to_students, name='broadcast_students'),
    path('notifications/broadcast-staff/', broadcast_to_staff, name='broadcast_staff'),
    path('notifications/admin-history/', admin_notifications_history, name='notifications_admin_history'),
    path('notifications/student-notification/<int:pk>/', delete_student_notification, name='delete_student_notification'),
    path('notifications/staff-notification/<int:pk>/', delete_staff_notification, name='delete_staff_notification'),

    # Routers
    path('', include(router.urls)),
]
