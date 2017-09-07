# -*- coding: utf-8 -*-
from django.conf import settings
from smsapi.client import SmsAPI
from smsapi.responses import ApiError
from twilio.rest import Client

from edziennik.models import SMS, Student
from edziennik.tasks import twilio_first_sms_status_check_task,\
                            twilio_second_sms_status_check_task,\
                            admin_email

# smsapi.pl
def send_sms_smsapi(parent_phone, message):
    api = SmsAPI()
    # autoryzacyja standardowa
    api.set_username(settings.SMS_API_USERNAME)
    api.set_password(settings.SMS_API_PASS)
    try:
        api.service('sms').action('send')
        api.set_content(message)
        api.set_to(parent_phone)
        api.set_from('Info')
        result = api.execute()
        for r in result:
            # print r.id, r.points, r.status
            mail_body = 'Wyslano sms do %s o tresci: %s \n\
            id: %s, points: %s, status: %s' % (parent_phone, message, r.id, r.points, r.status)
            mail_title = 'SMS wyslany do %s' % parent_phone
            admin_email(mail_title, mail_body)
    except ApiError, e:
        # print '%s - %s' % (e.code, e.message)
        mail_body = 'Blad wysylania smsa do %s, o tresci: %s \n\
        kod bledu: %s, tresc bledu: %s, points: %s' % (parent_phone, message, r.id, r.status, r.points)
        mail_title = 'Blad SMSa do %s' % parent_phone
        admin_email(mail_title, mail_body)

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

    twilio_first_sms_status_check_task.apply_async(countdown=300)
    twilio_second_sms_status_check_task.apply_async(countdown=1200)

def student_absence(student):
    parent = student.parent
    male_student_msg = 'Informujemy ze %s nie byl dzis obecny na lekcji jezyka angielskiego w szkole Energy' % student.name
    female_student_msg = 'Informujemy ze %s nie byla dzis obecna na lekcji jezyka angielskiego w szkole Energy' % student.name
    message = male_student_msg if student.gender == 'M' else female_student_msg
    
    # send sms via SmsApi.pl
    # send_sms_smsapi(parent_phone, message)

    # send sms via twilio
    # send_sms_twilio(parent, message)

