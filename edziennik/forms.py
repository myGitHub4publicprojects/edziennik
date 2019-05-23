from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea
from .models import Admin_Profile, Student, Parent


class AdminProfileForm(ModelForm):
    class Meta:
        model = Admin_Profile
        fields = ['quizlet_username', 'quizlet_password', 
                  'check_quizlet_automatically', 'twilio_account_sid', 'twilio_auth_token',
                  'twilio_messaging_service_sid', 'sms_when_absent', 'sms_when_no_homework',
                  'sms_message_absence', 'sms_message_no_homework', 'school_admin_email',
                  'send_email_weekly_attendance_report']
        widgets = {
            'sms_message_absence': Textarea(attrs={'cols': 100, 'rows': 3}),
            'sms_message_no_homework': Textarea(attrs={'cols': 100, 'rows': 3}),
        }


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254)


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'date_of_birth', 'school',
            'class_in_school', 'language_of_interest', 'language_at_school',
            'experience', 'book', 'avaliability', 'other_classes', 'focus', 'gender']

    
class ParentForm(ModelForm):
    class Meta:
        model = Parent
        fields = ['phone_number']