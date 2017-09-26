from django.test import TestCase, Client
# from django.core.urlresolvers import reverse
# from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import auth
from mixer.backend.django import mixer
import pytest
from datetime import datetime, timedelta
# from django.contrib.staticfiles.templatetags.staticfiles import static
from edziennik.models import Lector, Group, Parent, Student, ClassDate, Grades

from edziennik.utils2 import generate_weekly_admin_report

pytestmark = pytest.mark.django_db
today = datetime.today().date()

class Testgenerate_eekly_admin_report(TestCase):
    def test_no_students(self):
        """
        if setup is correct title and body are returned
        """
        email_title, email_body = generate_weekly_admin_report()
        expected_title = 'Attendance and grades report'
        expected_body = 'Attendance has not been checked this week\n' + 'No grades have been given last week'
        self.assertEqual(email_title, expected_title)
        self.assertEqual(email_body, expected_body)

    def test_two_student_one_present_no_grades(self):
        """
        should return attendance report with one date and one student
        """
        yesterday = today-timedelta(1)
        group = mixer.blend(Group, name='g1')
        student1 = mixer.blend(Student, name='s1', group=group)
        student2 = mixer.blend(Student, name='s2', group=group)
        class_date = mixer.blend(ClassDate,
                                date_of_class=yesterday,
                                subject='subject1')
        class_date.student.add(student1)
        class_date.save()

        head = 'On %s\nin group: %s\n' % (str(yesterday), group.name)
        f = 'the following students were present:'
        attendance = '\n' + student1.name + '\n--------------------------------\n'
        grades = 'No grades have been given last week'
        email_title, email_body = generate_weekly_admin_report()
        expected_title = 'Attendance and grades report'
        expected_body = head + f + attendance + grades
        self.assertEqual(email_title, expected_title)
        self.assertEqual(email_body, expected_body)

    def test_two_student_one_present_one_grade(self):
        """
        should return attendance report with one date and one student,
        one grade for one student
        """
        yesterday = today-timedelta(1)
        group = mixer.blend(Group, name='g1')
        student1 = mixer.blend(Student, name='s1', group=group)
        student2 = mixer.blend(Student, name='s2', group=group)
        class_date = mixer.blend(ClassDate,
                                date_of_class=yesterday,
                                subject='subject1')
        class_date.student.add(student1)
        class_date.save()

        head = 'On %s\nin group: %s\n' % (str(yesterday), group.name)
        f = 'the following students were present:'
        attendance = '\n' + student1.name + '\n--------------------------------\n'

        grade = Grades.objects.create(
                name='g1',
                student = student1,
                score = 2)
        head2 = '\n' + 'Last week the following grades were given:\n'
        students_grades = ' '.join([str(grade.timestamp.date()), 'group:', group.name, 'student:', student1.name,
                         'for:', grade.name, 'score:', str(grade.score), '\n'])
                         
        grades = head2 + students_grades
        email_title, email_body = generate_weekly_admin_report()
        expected_title = 'Attendance and grades report'
        expected_body = head + f + attendance + grades
        self.assertEqual(email_title, expected_title)
        self.assertEqual(email_body, expected_body)