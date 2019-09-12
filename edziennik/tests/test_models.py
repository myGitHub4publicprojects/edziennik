from django.test import TestCase
from edziennik.models import (Lector, Group, Parent, Student, ClassDate, Grades,
                              Admin_Profile, Quizlet)
from django.utils import timezone
from mixer.backend.django import mixer
import pytest

# models test


class Test_Student(TestCase):

    def test_student_creation(self):
        s = mixer.blend('edziennik.Student', first_name='fname', last_name='lname')
        self.assertEqual(s.__str__(), 'fname lname')

# class Group(TestCase):
#     def test_group_creation(self):
#         pass


class Test_Student_added_to_group(TestCase):
    def setUp(self):
        for i in range(4):
            mixer.blend('edziennik.Student')
            mixer.blend('edziennik.Group')
    def test_student_added_to_group(self):
        s = Student.objects.get(id=1)
        g = Group.objects.get(id=1)
        g.student.add(s)

        self.assertTrue(Quizlet.objects.filter(group=g, student=s).exists())

    def test_three_students_added_to_group(self):
        s = Student.objects.get(id=1)
        s1 = Student.objects.get(id=2)
        s2 = Student.objects.get(id=3)
        g = Group.objects.get(id=1)
        g.student.add(s, s1, s2)

        for q in Quizlet.objects.all():
            print(q.student, q.group)

        # should create 3 Quizlet instances
        self.assertEqual(Quizlet.objects.filter(group=g).count(),3)

        # one Quizlet instance should correspond to s1 attending group g
        self.assertEqual(Quizlet.objects.filter(group=g, student=s1).count(), 1)


class Test_add_email_to_user(TestCase):

    def test_add_email_to_user(self):
        p = mixer.blend('edziennik.Parent')
        self.assertEqual(p.user.email, p.email)