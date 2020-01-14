import io
import os
import shutil
import tempfile

from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, Client, TransactionTestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import auth
from django.core import mail
from mixer.backend.django import mixer
import pytest
from datetime import datetime, timedelta
from edziennik.models import (Lector, Group, Parent, Student, ClassDate, Grades, 
            Admin_Profile, Initial_Import, Initial_Import_Usage, Initial_Import_Usage_Errors)

from edziennik.utils import (admin_email, generate_weekly_admin_report,
        signup_email, import_students)

pytestmark = pytest.mark.django_db
today = datetime.today().date()

class Testgenerate_weekly_admin_report(TestCase):
    def test_no_students(self):
        """
        if setup is correct title and body are returned
        """
        email_title, email_body = generate_weekly_admin_report()
        expected_title = 'Attendance and grades report from example.com'
        expected_body = 'Attendance has not been checked this week\n' + 'No grades have been given last week'
        self.assertEqual(email_title, expected_title)
        self.assertEqual(email_body, expected_body)

    def test_two_student_one_present_no_grades(self):
        """
        should return attendance report with one date and one student
        """
        yesterday = today-timedelta(1)
        
        student1 = mixer.blend(Student,
                               first_name='f1',
                               last_name='l1',
                               )
        student2 = mixer.blend(Student,
                               first_name='f2',
                               last_name='l2',
                               )

        group = mixer.blend(Group, name='g1')
        group.student.add(student1, student2)
        class_date = mixer.blend(ClassDate,
                                date_of_class=yesterday,
                                subject='subject1',
                                group=group)
        class_date.student.add(student1)
        class_date.save()

        head = 'On %s\nin group: %s\n' % (str(yesterday), group.name)
        f = 'the following students were present:'
        attendance = '\n' + str(student1) + '\n--------------------------------\n'
        grades = 'No grades have been given last week'
        email_title, email_body = generate_weekly_admin_report()
        expected_title = 'Attendance and grades report from example.com'
        expected_body = head + f + attendance + grades
        self.assertEqual(email_title, expected_title)
        self.assertEqual(email_body, expected_body)

    def test_two_student_one_present_one_grade(self):
        """
        should return attendance report with one date and one student,
        one grade for one student
        """
        yesterday = today-timedelta(1)
        student1 = mixer.blend(Student,
                                first_name='f1',
                                last_name='l1',
                                )
        student2 = mixer.blend(Student,
                                first_name='f2',
                                last_name='l2',
                                )
        group = mixer.blend(Group, name='g1')
        group.student.add(student1, student2)
        class_date = mixer.blend(ClassDate,
                                date_of_class=yesterday,
                                subject='subject1',
                                group=group)
        class_date.student.add(student1)
        class_date.save()

        head = 'On %s\nin group: %s\n' % (str(yesterday), group.name)
        f = 'the following students were present:'
        attendance = '\n' + str(student1) + '\n--------------------------------\n'

        grade = Grades.objects.create(
                name='g1',
                student = student1,
                score = 2,
                group=group)
        head2 = '\n' + 'Last week the following grades were given:\n'
        students_grades = ' '.join([str(grade.timestamp.date()), 'group:', group.name, 'student:', str(student1),
                         'for:', grade.name, 'score:', str(grade.score), '\n'])
                         
        grades = head2 + students_grades
        email_title, email_body = generate_weekly_admin_report()
        expected_title = 'Attendance and grades report from example.com'
        expected_body = head + f + attendance + grades
        self.assertEqual(email_title, expected_title)
        self.assertEqual(email_body, expected_body)


class TestAdmin_Email(TestCase):
    def test_two_args_without_admin_profile(self):
        '''should send one email to the address specified in settings.py'''
        mail_title = 'Test title'
        mail_body = 'Test body'
        admin_email(mail_title, mail_body)

        expected_title = 'Test title'
        expected_body = 'Test body'
        expected_email_address = [settings.ADMIN_EMAIL]

        # should send only one email
        self.assertEqual(len(mail.outbox), 1)

        # should have expeceted title and body
        self.assertEqual(mail.outbox[0].subject, expected_title)
        self.assertEqual(mail.outbox[0].body, expected_body)

        # should have an expected recipient
        self.assertEqual(mail.outbox[0].to, expected_email_address)

    def test_two_args_with_admin_profile(self):
        '''should send one email to the address specified in admin_profile'''
        admin_profile_email = 'jlennon@beatles.com'
        User.objects.create_superuser(
            username='admin', email=admin_profile_email, password='glassonion')
        Admin_Profile.objects.create(
            user=User.objects.get(username='admin'), school_admin_email=admin_profile_email)

        admin_email('title', 'body')

        # should send only one email
        self.assertEqual(len(mail.outbox), 1)

        # should have an expected recipient
        self.assertEqual(mail.outbox[0].to, [admin_profile_email])

    def test_three_args_with_admin_profile(self):
        '''should send one email to the address specified in args'''
        admin_profile_email = 'jlennon@beatles.com'
        User.objects.create_superuser(
            username='admin', email=admin_profile_email, password='glassonion')
        Admin_Profile.objects.create(
            user=User.objects.get(username='admin'), school_admin_email=admin_profile_email)

        admin_email('title', 'body', email='test@example.com')

        # should send only one email
        self.assertEqual(len(mail.outbox), 1)

        # should have an expected recipient
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])


class TestSignUp_Email(TestCase):
    def test_signup_with_no_other_users(self):
        '''should send one email to the address specified in settings.py'''
        p1 = 'somePass'
        e1 = 'example@email.com'
        fname = 'Oloo'
        home_url = 'example.com'
        user = User.objects.create(username='johnlenon', password=p1, email=e1)
        parent = mixer.blend(Parent, user=user)
        student = mixer.blend(Student, parent=parent, first_name=fname)
        signup_email(parent, student, p1)

        expected_title = 'Witaj w szkole Energy Czerwonak!'
        expected_body = """Witamy w szkole Energy Czerwonak!
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
                        password=p1)
        expected_email_address = [parent.user.email]

        # should send only one email
        self.assertEqual(len(mail.outbox), 1)

        # should have expeceted title and body
        self.assertEqual(mail.outbox[0].subject, expected_title)
        self.assertEqual(mail.outbox[0].body, expected_body)

        # should have an expected recipient
        self.assertEqual(mail.outbox[0].to, expected_email_address)

class Test_import_students(TestCase):
    maxDiff = None
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_dir

    def make_initial_import_obj(self, file_name):
        '''file_name - .xlsx file, creates Initial_Import instance''' 
        path = os.getcwd() + '/edziennik/tests/test_files/' + file_name
        with open(path, 'rb') as f:
            fF = InMemoryUploadedFile(io.BytesIO(f.read()), 'fileobj',
                                      'name.xlsx', 'application/xlsx',
                                      os.path.getsize(path), None)
            return Initial_Import.objects.create(file=fF)

    def test_creates_Initial_Import_Usage_obj(self):
        import_students(self.make_initial_import_obj('test_1student.xlsx'))
        # should create 1 IIU instance
        self.assertEqual(Initial_Import_Usage.objects.all().count(), 1)
        # there should be no Initial_Import_Usage_Errors instances
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 0)

    def test_one_student_one_parent_one_group(self):
        import_students(self.make_initial_import_obj('test_1student.xlsx'))
        self.assertEqual(Initial_Import_Usage.objects.all().count(), 1)

        # should create 1 Student object
        self.assertEqual(Student.objects.all().count(), 1)
        # should create 1 Parent object
        self.assertEqual(Parent.objects.all().count(), 1)
        # should create 1 Group object
        self.assertEqual(Group.objects.all().count(), 1)

    def test_2_students_2_parents_2_groups(self):
        import_students(self.make_initial_import_obj('test_2students.xlsx'))

        # should create 2 Students objects
        self.assertEqual(Student.objects.all().count(), 2)
        # should create 2 Parents object
        self.assertEqual(Parent.objects.all().count(), 2)
        # should create 2 Group objects
        self.assertEqual(Group.objects.all().count(), 2)


    def test_3_students_2_parents_3_groups(self):
        import_students(self.make_initial_import_obj('test_3students.xlsx'))

        # should create 3 Students objects
        self.assertEqual(Student.objects.all().count(), 3)
        # should create 2 Parents object
        self.assertEqual(Parent.objects.all().count(), 2)
        # should create 3 Group objects
        self.assertEqual(Group.objects.all().count(), 3)

    def test_2_students_1_parent_3_groups(self):
        import_students(self.make_initial_import_obj(
            'test_2students_1p_3g.xlsx'))

        # should create 2 Students objects
        self.assertEqual(Student.objects.all().count(), 2)
        # should create 1 Parent object
        self.assertEqual(Parent.objects.all().count(), 1)
        # should create 3 Group objects
        self.assertEqual(Group.objects.all().count(), 3)

    def test_2_students_1e(self):
        '''missing parent first name
        should not create Student, Parent and Group instances'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_parent_fname.xlsx'))

        # should create 0 Students objects
        self.assertEqual(Student.objects.all().count(), 0)
        # should create 0 Parents object
        self.assertEqual(Parent.objects.all().count(), 0)
        # should create 0 Group objects
        self.assertEqual(Group.objects.all().count(), 0)

    def test_2_students_1e_generate_error(self):
        '''missing parent first name
        should create Initial_Import_Usage_Errors instance'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_parent_fname.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)

        # Initial_Import_Usage should have 1 corresponding
        # Initial_Import_Usage_Errors instance
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        self.assertEqual(e.count(), 1)

    def test_2_students_1e_generate_error_logs_and_data(self):
        '''missing parent first name
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_parent_fname.xlsx'))

        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

        # should have correct line
        exp_line = "(None, 'Wolek', 'Marta', 'Kass', 'f', None, 'ważna grupa2 AĄŁ', 777222333, 'ala@gmail.com', 'nota o Izie Ąś')"
        self.assertEqual(e.first().line, exp_line)

        # should have correct error_log
        exp_log = "Traceback (most recent call last):"
        self.assertIn(exp_log, e.first().error_log)

    def test_2_students_1e_parent_no_surname(self):
        '''missing parent surname,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_parent_sname.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_no_fname(self):
        '''missing student firstname,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_student_fname.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_no_sname(self):
        '''missing student surname,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_student_sname.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_no_gender(self):
        '''missing student gender,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_student_gender.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_no_group(self):
        '''missing student group,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_student_group.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_no_tel(self):
        '''missing tel,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_tel.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_short_tel(self):
        '''too short tel'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_short_tel.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_long_tel(self):
        '''too long tel'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_long_tel.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_invalid_tel(self):
        '''invalid character in tel - space'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_invalid_tel.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    def test_2_students_1e_student_invalid_tel2(self):
        '''invalid character in tel - letter'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_invalid_tel2.xlsx'))

        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

        # invalid email

        # error in second line, first and third ok - should create none



    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)


class Test_import_students2(TransactionTestCase):
    '''use TransactionTestCase to avoid problems with transactions'''
    maxDiff = None

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_dir

    def make_initial_import_obj(self, file_name):
        '''file_name - .xlsx file, creates Initial_Import instance'''
        path = os.getcwd() + '/edziennik/tests/test_files/' + file_name
        with open(path, 'rb') as f:
            fF = InMemoryUploadedFile(io.BytesIO(f.read()), 'fileobj',
                                      'name.xlsx', 'application/xlsx',
                                      os.path.getsize(path), None)
            return Initial_Import.objects.create(file=fF)

    def test_2_students_1e_student_no_email(self):
        '''missing email,
        Initial_Import_Usage_Errors instance should have correct properties'''
        iiu = import_students(self.make_initial_import_obj(
            'test_2students_1e_missing_email.xlsx'))
            
        # there should be 1 Initial_Import_Usage_Errors instance
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        e = Initial_Import_Usage_Errors.objects.filter(
            initial_import_usage=iiu)
        # error sould be in row number 3 (row_number 2 as 0 indexed)
        self.assertEqual(e.first().row_number, 2)

    
    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)
