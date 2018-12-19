from django.forms import ModelForm
from .models import Admin_Profile


class AdminProfileForm(ModelForm):
    class Meta:
        model = Admin_Profile
        fields = ['quizlet_username',
                  'quizlet_password', 'twilio_account_sid', 'twilio_auth_token',
                  'sms_when_absent', 'sms_when_no_homework', 'sms_message_absence',
                  'sms_message_no_homework', 'school_admin_email',
                  'send_email_weekly_attendance_report']
