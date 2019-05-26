from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, Textarea
from .models import Admin_Profile, Student, Parent
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


class SignUpFormOld(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # do not require password
        del self.fields['password1']
        del self.fields['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        # password = User.objects.make_random_password(length=8)
    #     print('pass: ', password)
    #     # user.set_password(password)
        # user.set_password(self.cleaned_data["password1"])
        user.set_password('tfs3kjhg7dd')
    #     fname = self.cleaned_data['first_name']
    #     lname = self.cleaned_data['last_name']

    #     user.username = create_unique_username(fname, lname)
    #     print('uname: ', user.username)
        if commit:
            user.save()
        return user

    def clean_username(self):
        fname = self.cleaned_data['first_name']
        fname = self.cleaned_data['first_name']
        lname = self.cleaned_data['last_name']
        return create_unique_username(fname, lname)
        # return 'myusername1'



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


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=254)
