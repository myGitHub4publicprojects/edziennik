from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ModelForm, Textarea
from .models import Admin_Profile, Student, Parent, Homework
from edziennik.utils import create_unique_username


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

# class StudentMinimalForm():
#     pass

#     model = Student
#     fields = ['parent', 'first_name', 'last_name', 'gender']

#     class TestTableModelChoiceField(forms.ModelChoiceField):
#         def label_from_instance(self, obj):
#          # return the field you want to display
#          return obj.display_field

# class TestForm(forms.ModelForm):
#     type = TestTableModelChoiceField(queryset=Property.objects.all().order_by('desc1'))

    
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
    email = forms.EmailField(max_length=254)
    phone_number = forms.IntegerField(
        label='Nr telefonu',
        help_text='9 cyfr, bez spacji',
        validators=[MinValueValidator(100000000), MaxValueValidator(999999999)])

class HomeworkForm(ModelForm):
    class Meta:
        model = Homework
        fields = ['message',]
