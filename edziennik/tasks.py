# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail

from twilio.rest import Client

from celery.decorators import task
from celery.utils.log import get_task_logger
from celery.task.schedules import crontab
from celery.decorators import periodic_task

from edziennik.models import SMS, Student

from edziennik.utils2 import generate_weekly_admin_report

logger = get_task_logger(__name__)

def admin_email(mail_title, mail_body):
    send_mail(mail_title,
        mail_body,
        settings.EMAIL_HOST_USER,
        [settings.ADMIN_EMAIL],
        fail_silently=False)

@periodic_task(
    run_every=(crontab(minute=1, hour=1)),
    name="weekly_email_admin",
    ignore_result=True
)
def weekly_admin_email():
    email_title, email_body = generate_weekly_admin_report()
    admin_email(email_title, email_body)
    logger.info("email to admin has been sent")

#twilio sms
@task(name='twilio_first_sms_status_check_task')
def twilio_first_sms_status_check_task():
    ''' after time specified in call parameter checks msg status with sms provider '''
    logger.info("first sms status check")
    new_msgs = SMS.objects.filter(checked_once=False)
    ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for msg in new_msgs:
        fetched = client.messages(msg.twilio_message_sid).fetch()
        msg.checked_once = True
        msg.save()
        if fetched.status == 'delivered':
            msg.twilio_message_status = 'delivered'
            msg.delivered = True
            msg.save()
        else:
            msg.twilio_message_status = fetched.status
            msg.save()

@task(name='twilio_second_sms_status_check_task')
def twilio_second_sms_status_check_task():
    '''  after time specified in call parameter checks msg status
    with sms provider for messages which had not "delivered" status '''
    logger.info("second sms status check")
    undelivered_msgs = SMS.objects.filter(checked_once=True, checked_twice=False, delivered=False)
    ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    for msg in undelivered_msgs:
        fetched = client.messages(msg.twilio_message_sid).fetch()
        msg.checked_twice = True
        msg.save()
        if fetched.status == 'delivered':
            msg.twilio_message_status = 'delivered'
            msg.delivered = True
            msg.save()
        else:
            msg.twilio_message_status = fetched.status
            mail_title = 'SMS undelivered to %s' % msg.addressee.username
            mail_body = 'SMS to {parent_name} was undelivered. Message details:\n\
            phone_number: {phone_number}\n\
            service: Twilio\n\
            message: {msg_body}\n\
            message sid: {msg_sid}\n\
            message status: {msg_status}'.format(parent_name=msg.addressee.username,
                                                    phone_number=msg.to, msg_body=msg.body,
                                                    msg_sid=msg.sid,
                                                    msg_status=msg.status)
            admin_email(mail_title, mail_body)
            