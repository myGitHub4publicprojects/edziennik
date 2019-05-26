import pytest
from .. import forms
from edziennik.models import Admin_Profile
from mixer.backend.django import mixer
from datetime import date

pytestmark = pytest.mark.django_db


class TestAdminProfileForm():
    def test_empty_form(self):
        form = forms.AdminProfileForm(data={})
        assert form.is_valid() is True, 'fields are not required, should be True'

    def test_partially_filled_form(self):
        data = {'quizlet_username': 'usr',
                'quizlet_password': 'pass',
                'twilio_account_sid': 'twilio',
                }
        form = forms.AdminProfileForm(data=data)
        assert form.errors == {}, 'shoud be empty'
        assert form.is_valid() is True, 'Should be valid'

    def test_fully_filled_form(self):
        data = {'quizlet_username': 'usr',
                'quizlet_password': 'pass',
                'twilio_account_sid': 'twilio',
                'twilio_auth_token': 'token',
                'sms_when_absent': True,
                'sms_when_no_homework': True,
                'sms_message_absence': 'student is absent',
                'sms_message_no_homework': 'student has no homework',
                'school_admin_email': 'john@example.com',
                'send_email_weekly_attendance_report': False
                }
        form = forms.AdminProfileForm(data=data)
        assert form.errors == {}, 'shoud be empty'
        assert form.is_valid() is True, 'Should be valid'


class TestSignUpForm():
    def test_empty_form(self):
        form = forms.SignUpForm(data={})
        assert form.is_valid() is False, 'fields are required, should be False'

    def test_fully_filled_form(self):
        data = {
                # 'password1': 'cotmbyc23',
                # 'password2': 'cotmbyc23',
                'first_name': 'oloo',
                'last_name': 'Nowak',
                'email': 'asdfljwoejf@gmail.com',
                }
        form = forms.SignUpForm(data=data)
        assert form.errors == {}, 'shoud be empty'
        assert form.is_valid() is True, 'Should be valid'
