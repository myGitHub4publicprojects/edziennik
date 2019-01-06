# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.core.mail import send_mail

from twilio.rest import Client

from edziennik.models import SMS, Admin_Profile


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
    ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    parent_phone_number = '+48' + str(parent.phone_number)
    twilio_message = client.messages.create(to=parent_phone_number,
                                    # from_=settings.TWILIO_TEST_PHONE_NO,
                                    messaging_service_sid=settings.MESSAGING_SERVICE_SID,
                                    body=message)

    SMS.objects.create(service='twilio',
                       message=message,
                       addressee=parent.user,
                       twilio_message_sid=twilio_message.sid)


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
