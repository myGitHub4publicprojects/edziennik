# -*- coding: utf-8 -*-
import re
import datetime
from django.conf import settings
from django.core.mail import send_mail

from twilio.rest import Client

from edziennik.models import ClassDate, Grades, SMS, Admin_Profile


def admin_email(mail_title, mail_body, email=None):
    if not email:
        recipient = settings.ADMIN_EMAIL
        admin_profile = Admin_Profile.objects.all().first()
        if admin_profile:
            if admin_profile.school_admin_email:
                recipient = admin_profile.school_admin_email
    else:
        recipient = email
    send_mail(mail_title,
              mail_body,
              settings.EMAIL_HOST_USER,
              [recipient],
              fail_silently=False)

# twilio
def send_sms_twilio(parent, message):
    # verify Admin_Profile instance - if not do not notify admin
    admin_profile = Admin_Profile.objects.all().first()
    if not admin_profile:
        mail_title = 'Problem z wiadomością SMS Twilio'
        mail_body = ('Nie można było wysłać wiadomości SMS do ' + parent.user.username +
                    ' o treści: ' + message + ' gdyż nie zostały wprowadzone ustawienia Twilio.')
        admin_email(mail_title, mail_body)
        return None
    if (not admin_profile.twilio_account_sid or not admin_profile.twilio_auth_token
        or not admin_profile.twilio_messaging_service_sid):
        mail_title='Problem z wiadomością SMS Twilio'
        mail_body=('Nie można było wysłać wiadomości SMS do ' + parent.user.username +
                    ' o treści: ' + message + ' gdyż brakuje części ustawień Twilio.')
        admin_email(mail_title, mail_body)
        return None
    client = Client(admin_profile.twilio_account_sid,
                    admin_profile.twilio_auth_token)
    parent_phone_number = '+48' + str(parent.phone_number)
    twilio_message = client.messages.create(
        to=parent_phone_number,
        # from_=settings.TWILIO_TEST_PHONE_NO,
        messaging_service_sid=admin_profile.twilio_messaging_service_sid,
        body=message)

    SMS.objects.create(service='twilio',
                       message=message,
                       addressee=parent.user,
                       twilio_message_sid=twilio_message.sid)


def test_sms_twilio(twilio_account_sid, twilio_auth_token, messaging_service_sid, phone_no, message):
    '''accepts four strings, phone no (+48111222333)'''
    client = Client(twilio_account_sid, twilio_auth_token)
    client.messages.create(to=phone_no,
                            # from_=settings.TWILIO_TEST_PHONE_NO,
                            messaging_service_sid=messaging_service_sid,
                            body=message)

def generate_weekly_admin_report():
    ''' genereates raport for last week '''
    today = datetime.date.today()
    title = 'Attendance and grades report'
    class_dates = ClassDate.objects.filter(
        date_of_class__gte=today-datetime.timedelta(7))
    output = 'Attendance has not been checked this week\n'
    if class_dates:
        output = ''
    for class_date in class_dates:
        students = class_date.student.all()
        group = students.first().group
        date = class_date.date_of_class
        head = 'On %s\nin group: %s\n' % (str(date), group.name)
        f = 'the following students were present:'
        s = ''.join(['\n' + s.name for s in students])
        end = '\n--------------------------------\n'
        section = head + f + s + end
        output += section

    grades = Grades.objects.filter(
        timestamp__date__gte=today-datetime.timedelta(7))
    output2 = 'No grades have been given last week'
    if grades:
        output2 = '\n' + 'Last week the following grades were given:\n'
    for g in grades:
        date = g.timestamp.date()
        student = g.student
        group = student.group.name
        name = g.name
        score = g.score
        g_str = ' '.join([str(date), 'group:', group, 'student:', student.name,
                          'for:', name, 'score:', str(score), '\n'])
        output2 += g_str

    body = output + output2
    return (title, body)


def generate_test_sms_msg(sex, user_msg, test_name):
    '''Accepts three strings, sex of a student (either 'male' or 'female'),
    message that user inuts in a form, name used for tests.
    {{name}} is replaced with student name and <<...#...>> is replaced with
    proper grammar form according to gender of a student.
    Returns str, message containing proper name and grammar form'''
    # validate grammar part
    if re.search('<<(.+?)>>', user_msg):
        if sex == 'male':
            grammar = re.search('<<(.+?)#', user_msg).group(1)
        if sex == 'female':
            grammar = re.search('#(.+?)>>', user_msg).group(1)
        # male = re.search('<<(.+?)#', st).group(1)
        grammar_choices = re.search('<<(.+?)>>', user_msg).group(0)
        user_msg = user_msg.replace(grammar_choices, grammar)
    # validate name part
    if not re.search('{{(.+?)}}', user_msg):
        return user_msg
    name_part = re.search('{{(.+?)}}', user_msg).group(0)
    final_msg = user_msg.replace(name_part, test_name)
    return final_msg
