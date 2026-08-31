from django import forms

from student_management_app.models import Courses, SessionYearModel

class DateInput(forms.DateInput):
    input_type = "date"

class AddStudentForm(forms.Form):
    email = forms.CharField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control", "autocomplete":"off"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control", "autocomplete":"off"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    
    gender_choice = (
        ("Male", "Male"),
        ("Female", "Female")
    )

    course = forms.ChoiceField(label="Course", choices=[], widget=forms.Select(attrs={"class":"form-control"}))
    sex = forms.ChoiceField(label="Sex", choices=gender_choice, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", widget=forms.Select(attrs={"class":"form-control"}), choices=[])
    profile_pic = forms.FileField(label="Profile Pic", max_length=50, widget=forms.FileInput(attrs={"class":"form-control"}))

    def __init__(self, *args, **kwargs):
        super(AddStudentForm, self).__init__(*args, **kwargs)
        course_list = []
        try:
            courses = Courses.objects.all()
            for course in courses:
                course_list.append((course.id, course.course_name))
        except Exception:
            course_list = []
        self.fields['course'].choices = course_list

        session_list = []
        try:
            sessions = SessionYearModel.objects.all()
            for ses in sessions:
                session_list.append((ses.id, f"{ses.session_start_year} TO {ses.session_end_year}"))
        except Exception:
            session_list = []
        self.fields['session_year_id'].choices = session_list


class EditStudentForm(forms.Form):
    email = forms.CharField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    first_name = forms.CharField(label="First Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    last_name = forms.CharField(label="Last Name", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    address = forms.CharField(label="Address", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))

    gender_choice = (
        ("Male", "Male"),
        ("Female", "Female")
    )

    course = forms.ChoiceField(label="Course", choices=[], widget=forms.Select(attrs={"class":"form-control"}))
    sex = forms.ChoiceField(label="Sex", choices=gender_choice, widget=forms.Select(attrs={"class":"form-control"}))
    session_year_id = forms.ChoiceField(label="Session Year", widget=forms.Select(attrs={"class":"form-control"}), choices=[])
    profile_pic = forms.FileField(label="Profile Pic", max_length=50, widget=forms.FileInput(attrs={"class":"form-control"}), required=False)

    def __init__(self, *args, **kwargs):
        super(EditStudentForm, self).__init__(*args, **kwargs)
        course_list = []
        try:
            courses = Courses.objects.all()
            for course in courses:
                course_list.append((course.id, course.course_name))
        except Exception:
            course_list = []
        self.fields['course'].choices = course_list

        session_list = []
        try:
            sessions = SessionYearModel.objects.all()
            for ses in sessions:
                session_list.append((ses.id, f"{ses.session_start_year} TO {ses.session_end_year}"))
        except Exception:
            session_list = []
        self.fields['session_year_id'].choices = session_list
    