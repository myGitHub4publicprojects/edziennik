from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ModelForm, Textarea
from .models import Admin_Profile, Student, Parent, Homework, Lector
from edziennik.utils import create_unique_username
from .validators_forms import UniqueEmailValidator, UniquePhoneValidator, UniqueEmailValidator_Lector


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


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'date_of_birth', 'school',
            'class_in_school', 'language_of_interest', 'language_at_school',
            'experience', 'book', 'avaliability', 'other_classes', 'focus', 'gender']


class LectorCreateForm(ModelForm):
    first_name = forms.CharField(max_length=30, label='Imię')
    last_name = forms.CharField(max_length=50, label='Nazwisko')
    email = forms.EmailField(required=False,
                             validators=[UniqueEmailValidator_Lector])

    class Meta:
        model = Lector
        fields = ['first_name', 'last_name', 'email']
        help_texts = {
            'email': 'jeśli nie podasz będzie losowo utworzony np.: wjayvao@test.test'
        }


class ParentCreateForm(ModelForm):
    first_name = forms.CharField(max_length=30, label='Imię rodzica')
    last_name = forms.CharField(max_length=50, label='Nazwisko rodzica')
    email = forms.EmailField(required=False,
                             validators=[UniqueEmailValidator])
    class Meta:
        model = Parent
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'street',
            'house_number', 'apartment_number', 'city', 'zip_code']
        help_texts = {
            'phone_number': '9 cyfr, bez spacji',
            'email': 'jeśli nie podasz będzie losowo utworzony np.: wjayvao@test.test'
        }


class ParentForm(ModelForm):
    class Meta:
        model = Parent
        fields = ['phone_number', 'street',
                  'house_number', 'apartment_number', 'city', 'zip_code']


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254)

class SignUpForm2(forms.Form):
    parent_first_name = forms.CharField(max_length=30, label='Imię rodzica')
    parent_last_name = forms.CharField(max_length=50, label='Nazwisko rodzica')
    email = forms.EmailField(
        max_length=254,
        help_text='jeśli nie podasz będzie losowo utworzony np.: wjayvao@test.test',
        required=False)
    phone_number = forms.IntegerField(
        label='Nr telefonu',
        help_text='9 cyfr, bez spacji',
        validators=[MinValueValidator(100000000), MaxValueValidator(999999999)])


class HomeworkForm(ModelForm):
    class Meta:
        model = Homework
        fields = ['message',]
