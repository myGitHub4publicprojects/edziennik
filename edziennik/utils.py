# -*- coding: utf-8 -*-
import random
import re
import datetime
import traceback
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.db import transaction
from twilio.rest import Client
from openpyxl import load_workbook

from edziennik.models import (ClassDate, Grades, SMS, Admin_Profile, Initial_Import_Usage,
                              Initial_Import_Usage_Errors, Parent, Student, Group)


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
    current_site = Site.objects.get_current()
    
    title = 'Attendance and grades report from {0}'.format(current_site.domain,)
    class_dates = ClassDate.objects.filter(
        date_of_class__gte=today-datetime.timedelta(7))
    output = 'Attendance has not been checked this week\n'
    if class_dates:
        output = ''
    for class_date in class_dates:
        students = class_date.student.all()
        # group = students.first().group
        group = class_date.group
        date = class_date.date_of_class
        head = 'On %s\nin group: %s\n' % (str(date), group.name)
        f = 'the following students were present:'
        s = ''.join(['\n' + str(s) for s in students])
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
        # group = student.group.name
        group = g.group.name
        name = g.name
        score = g.score
        g_str = ' '.join([str(date), 'group:', group, 'student:', str(student),
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


def removeAccents(input_text):
    strange = 'ŮôῡΒძěἊἦëĐᾇόἶἧзвŅῑἼźἓŉἐÿἈΌἢὶЁϋυŕŽŎŃğûλВὦėἜŤŨîᾪĝžἙâᾣÚκὔჯᾏᾢĠфĞὝŲŊŁČῐЙῤŌὭŏყἀхῦЧĎὍОуνἱῺèᾒῘᾘὨШūლἚύсÁóĒἍŷöὄЗὤἥბĔõὅῥŋБщἝξĢюᾫაπჟῸდΓÕűřἅгἰშΨńģὌΥÒᾬÏἴქὀῖὣᾙῶŠὟὁἵÖἕΕῨčᾈķЭτἻůᾕἫжΩᾶŇᾁἣჩαἄἹΖеУŹἃἠᾞåᾄГΠКíōĪὮϊὂᾱიżŦИὙἮὖÛĮἳφᾖἋΎΰῩŚἷРῈĲἁéὃσňİΙῠΚĸὛΪᾝᾯψÄᾭêὠÀღЫĩĈμΆᾌἨÑἑïოĵÃŒŸζჭᾼőΣŻçųøΤΑËņĭῙŘАдὗპŰἤცᾓήἯΐÎეὊὼΘЖᾜὢĚἩħĂыῳὧďТΗἺĬὰὡὬὫÇЩᾧñῢĻᾅÆßшδòÂчῌᾃΉᾑΦÍīМƒÜἒĴἿťᾴĶÊΊȘῃΟúχΔὋŴćŔῴῆЦЮΝΛῪŢὯнῬũãáἽĕᾗნᾳἆᾥйᾡὒსᾎĆрĀüСὕÅýფᾺῲšŵкἎἇὑЛვёἂΏθĘэᾋΧĉᾐĤὐὴιăąäὺÈФĺῇἘſგŜæῼῄĊἏØÉПяწДĿᾮἭĜХῂᾦωთĦлðὩზკίᾂᾆἪпἸиᾠώᾀŪāоÙἉἾρаđἌΞļÔβĖÝᾔĨНŀęᾤÓцЕĽŞὈÞუтΈέıàᾍἛśìŶŬȚĳῧῊᾟάεŖᾨᾉςΡმᾊᾸįᾚὥηᾛġÐὓłγľмþᾹἲἔбċῗჰხοἬŗŐἡὲῷῚΫŭᾩὸùᾷĹēრЯĄὉὪῒᾲΜᾰÌœĥტ'
    ascii_replacements = 'UoyBdeAieDaoiiZVNiIzeneyAOiiEyyrZONgulVoeETUiOgzEaoUkyjAoGFGYUNLCiIrOOoqaKyCDOOUniOeiIIOSulEySAoEAyooZoibEoornBSEkGYOapzOdGOuraGisPngOYOOIikoioIoSYoiOeEYcAkEtIuiIZOaNaicaaIZEUZaiIaaGPKioIOioaizTIYIyUIifiAYyYSiREIaeosnIIyKkYIIOpAOeoAgYiCmAAINeiojAOYzcAoSZcuoTAEniIRADypUitiiIiIeOoTZIoEIhAYoodTIIIaoOOCSonyKaAsSdoACIaIiFIiMfUeJItaKEISiOuxDOWcRoiTYNLYTONRuaaIeinaaoIoysACRAuSyAypAoswKAayLvEaOtEEAXciHyiiaaayEFliEsgSaOiCAOEPYtDKOIGKiootHLdOzkiaaIPIIooaUaOUAIrAdAKlObEYiINleoOTEKSOTuTEeiaAEsiYUTiyIIaeROAsRmAAiIoiIgDylglMtAieBcihkoIrOieoIYuOouaKerYAOOiaMaIoht'
    translator = str.maketrans(strange, ascii_replacements)
    return input_text.translate(translator)

def create_unique_username(a, b):
    username = a+b

    # remove accents
    username = removeAccents(username)

    # remove non alphanumeric characters
    username = ''.join(e for e in username if e.isalnum())

    if len(username) < 5:
        username += 'Energy'

    if not User.objects.filter(username=username):
        return username
    else:
        r = str(random.randint(1, 10))
        return create_unique_username(a, b+r)


def signup_email(parent, student, password):
    home_url = Site.objects.get_current().domain
    title = 'Witaj w szkole Energy Czerwonak!'
    body = """Witamy w szkole Energy Czerwonak!
            Dziękujemy za wypełnienie formularza zgłoszeniowego. Mamy nadzieję, że {student} już wkrótce dołączy do naszego grona!
            W ciągu najbliższych kilku dni zadzwonimy pod podany w formularzu numer telefonu aby omówić
            szczegóły dotyczące rekrutacji.
            Poniżej znajdziesz link oraz swoje dane dostępu do naszego edziennka. Znajdziesz tam swoje dane oraz dane zgłoszonych przez Ciebie studentów.
            Strona logowania: {url}
            Nazwa użytkownika: {username}
            Hasło: {password}
            Do usłyszenia,
            Zespół szkoły Energy Czerwonak
            """.format(student=student.first_name,
                       url=home_url,
                       username=parent.user.username,
                       password=password)
    send_mail(title,
              body,
              settings.EMAIL_HOST_USER,
              [parent.user.email],
              fail_silently=False)


def create_fake_unique_email():
    rand_string = ''.join(
        [random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(10)])
    new_email = rand_string + '@test.test'
    if User.objects.filter(email=new_email).exists():
        return create_fake_unique_email()
    else:
        return new_email

        
def import_students(initial_import_instance):
    '''Accepts Initial_Import obj, imports clients and studetns data from obj.file,
    returns Initial_Import_Usage instance,
    if errors in file (eg. missing values) only IIU_Errors instances are created and
    all changes are reverted via transaction savepoint'''
    iiu = Initial_Import_Usage.objects.create(
        initial_import=initial_import_instance)
    wb = load_workbook(initial_import_instance.file)
    ws = wb.active
    sid = transaction.savepoint()
    errors = []
    for row_no, row in enumerate(ws.values):
        if row_no != 0:
            try:
                p_first_name = row[0].strip().capitalize()
                p_last_name = row[1].strip().title()
                s_first_name = row[2].strip().capitalize()
                s_last_name = row[3]
                if not s_last_name:
                    s_last_name = p_last_name
                else:
                    s_last_name = s_last_name.strip().title()
                s_gender = row[4].strip().upper()
                group_name = str(row[5]).strip()
                p_phone_number = int(row[6])
                p_email = row[7] or create_fake_unique_email()
                p_email = p_email.strip().lower()
                s_recruitment_note = str(row[8])
                if s_recruitment_note:
                    s_recruitment_note = s_recruitment_note.strip()
                try:
                    p = Parent.objects.get(phone_number=p_phone_number)
                except Parent.DoesNotExist:
                    u = User.objects.create(
                        first_name=p_first_name,
                        last_name=p_last_name,
                        email=p_email,
                        username=create_unique_username(
                            p_first_name, p_last_name),
                    )
                    password = User.objects.make_random_password(length=8)
                    u.set_password(password)
                    u.save()
                    p = Parent(
                        user = u,
                        phone_number=p_phone_number,
                        email=p_email,
                        initial_password=password,
                        iiu=iiu
                    )
                    p.full_clean() # a must for validation
                    p.save()
                # create a Student
                try:
                    s = Student.objects.get(parent=p,
                                        first_name=s_first_name,
                                        last_name=s_last_name)
                except Student.DoesNotExist:
                    s = Student(parent=p,
                                first_name=s_first_name,
                                last_name=s_last_name,
                                gender = s_gender,
                                recruitment_note = s_recruitment_note,
                                iiu=iiu
                                )
                    s.full_clean()  # a must for validation
                    s.save()
                if group_name!='None':
                    # create group
                    g, created = Group.objects.get_or_create(
                        name=group_name, defaults={'iiu': iiu})
                    # add Student to a Group
                    g.student.add(s)
            except:
                error={
                    'error_log': traceback.format_exc(),
                    'row_number': row_no,
                    'line': row
                }
                errors.append(error)
    if errors:
        transaction.savepoint_rollback(sid)
        for e in errors:
            Initial_Import_Usage_Errors.objects.create(
                initial_import_usage=iiu,
                error_log=e['error_log'],
                row_number=e['row_number'],
                line=e['line']
            )
    if not errors:
        transaction.savepoint_commit(sid)

    return iiu

def valid_email_or_errors(email, data):
    if Parent.objects.filter(email=email).exists():
        data['result'] = 'Error'
        data['errors'] = {'email': ['''Rodzic z takim adresem email już istnieje. 
            Wybierz inny email, lub użyj istniejącego Rodzica''']}

def valid_phone_or_errors(phone_number, data):
    if Parent.objects.filter(phone_number=phone_number).exists():
        data['result'] = 'Error'
        if data.get('errors'):
            data['errors'].update(
                {'phone_number': ['''Rodzic z takim numerem telefonu już istnieje.
                Wybierz inny nr tel, lub użyj istniejącego Rodzica''']
                    }
            )
        else:
            data['errors'] = {'phone_number': ['''Rodzic z takim numerem telefonu już istnieje.
                Wybierz inny nr tel, lub użyj istniejącego Rodzica''']
                                }


def create_parent_and_user(parent_form, email, phone_number):
    password = User.objects.make_random_password(length=8)
    user = User.objects.create(
        first_name=parent_form.cleaned_data['parent_first_name'].capitalize(
        ),
        last_name=parent_form.cleaned_data['parent_last_name'].title(),
        email=email,
        username=create_unique_username(
            parent_form.cleaned_data['parent_first_name'],
            parent_form.cleaned_data['parent_last_name']
        )
    )
    user.set_password(password)
    user.save()

    parent = Parent.objects.create(
        user=user,
        phone_number=phone_number,
        email=email,
        initial_password=password
    )
    return parent
