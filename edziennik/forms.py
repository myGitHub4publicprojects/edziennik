from django.forms import ModelForm, Textarea
from .models import Admin_Profile


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
