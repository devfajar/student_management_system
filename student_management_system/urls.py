"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path

from student_management_app import views, adminViews, StaffViews, StudentViews
from student_management_system import settings

urlpatterns = [
    path('demo', views.showDemoPage),
    path('admin/', admin.site.urls),
    path('', views.showLoginPage, name="show_login"),
    path('get_user_details', views.GetUserDetail),
    path('logout_user', views.logout_user, name="logout"),
    path('doLogin', views.doLogin, name="doLogin"),
    path('admin_home', adminViews.admin_home, name="admin_home"),
    path('add_staff', adminViews.add_staff, name="add_staff"),
    path('add_staff_save', adminViews.add_staff_save, name="add_staff_save"),
    path('add_course', adminViews.add_course, name="add_course"),
    path('add_course_save', adminViews.add_course_save, name="add_course_save"),
    path('add_student', adminViews.add_student, name="add_student"),
    path('add_student_save', adminViews.add_student_save, name="add_student_save"),
    path('add_subject', adminViews.add_subject, name="add_subject"),
    path('add_subject_save', adminViews.add_subject_save, name="add_subject_save"),
    path('manage_staff', adminViews.manage_staff, name="manage_staff"),
    path('manage_student', adminViews.manage_student, name="manage_student"),
    path('manage_course', adminViews.manage_course, name="manage_course"),
    path('manage_subject', adminViews.manage_subject, name="manage_subject"),
    path('edit_staff/<str:staff_id>', adminViews.edit_staff, name="edit_staff"),
    path('edit_staff_save', adminViews.edit_staff_save, name="edit_staff_save"),
    path('edit_student/<str:student_id>', adminViews.edit_student, name="edit_student"),
    path('edit_student_save', adminViews.edit_student_save, name="edit_student_save"),
    path('edit_subject/<str:subject_id>', adminViews.edit_subject, name="edit_subject"),
    path('edit_subject_save', adminViews.edit_subject_save, name="edit_subject_save"),
    path('edit_course/<str:course_id>', adminViews.edit_course, name="edit_course"),
    path('edit_course_save', adminViews.edit_course_save, name="edit_course_save"),
    path('manage_session', adminViews.manage_session, name="manage_session"),
    path('add_session_save', adminViews.add_session_save, name="add_session_save"),
    # Staff Path
    path('staff_home', StaffViews.staff_home, name="staff_home"),
    path('staff_take_attendance', StaffViews.staff_take_attendance, name="staff_take_attendance"),
    path('staff_update_attendance', StaffViews.staff_update_attendance, name="staff_update_attendance"),
    path('get_students', StaffViews.get_students, name="get_students"),
    path('get_attendance_dates', StaffViews.get_attendance_dates, name="get_attendance_dates"),
    path('get_attendance_student', StaffViews.get_attendance_student, name="get_attendance_student"),
    path('save_attendance_data', StaffViews.save_attendance_data, name="save_attendance_data"),
    path('save_updateattendance_data', StaffViews.save_updateattendance_data, name="save_updateattendance_data"),
    path('staff_apply_leave', StaffViews.staff_apply_leave, name="staff_apply_leave"),
    path('staff_apply_leave_save', StaffViews.staff_apply_leave_save, name="staff_apply_leave_save"),
    path('staff_feedback', StaffViews.staff_feedback, name="staff_feedback"),
    path('staff_feedback_save', StaffViews.staff_feedback_save, name="staff_feedback_save"),

    # Student Path
    path('student_home', StudentViews.student_home, name="student_home"),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+ static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
