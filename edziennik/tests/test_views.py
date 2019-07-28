# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.messages import get_messages
from mixer.backend.django import mixer
import pytest
from datetime import date, datetime, timedelta
from django.templatetags.static import static
from freezegun import freeze_time
from edziennik.models import (Lector, Group, Parent, Student, ClassDate, Grades,
                              Admin_Profile, Quizlet)
pytestmark = pytest.mark.django_db
today = datetime.today().date()

class IndexViewTests(TestCase):
    def test_home_view_for_not_authenticated_noerror(self):
        """
        if setup is correct - status code 200
        """
        client = Client()
        user = auth.get_user(client) # it returns User or AnonymousUser
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_for_not_authenticated_correct_template(self):
        """
        if user is not authenticated should see log in page 'home_for_others.html'
        """
        client = Client()
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertEqual(response.templates[0].name, 'edziennik/home_for_others.html')


    def test_home_view_for_lectors_noerror(self):
        """
        if setup is correct - status code 200
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='john', password='glassonion')
        lector = Lector.objects.create(user=user_john)
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_for_lector_correct_template(self):
        """
        if user is lector template is home_for_lector.html
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='john', password='glassonion')
        lector = Lector.objects.create(user=user_john)
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertEqual(response.templates[0].name, 'edziennik/home_for_lector.html')

    def test_home_view_for_lector_no_groups(self):
        """
        if lector has no groups
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='john', password='glassonion')
        lector = Lector.objects.create(user=user_john)
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertQuerysetEqual(response.context['groups'], [])

    def test_home_view_for_lector_2_groups(self):
        """
        if lector has 2 of 3 groups, should have access to only 2
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        user_john2 = User.objects.create_user(username='john2',
                                 email='2jlennon@beatles.com',
                                 password='glassonion')
        lector = Lector.objects.create(user=user_john)
        lector2 = Lector.objects.create(user=user_john2)
        self.client.login(username='john', password='glassonion')
        group1 = Group.objects.create(name='group1', lector=lector)
        group2 = Group.objects.create(name='group2', lector=lector)
        group3 = Group.objects.create(name='group3', lector=lector2)
        groups = map(repr, Group.objects.filter(lector=lector))
        response = self.client.get(reverse('edziennik:name_home'))
        response_groups = list(response.context['groups'])
        self.assertQuerysetEqual(response_groups, groups)
  

    def test_home_view_for_admin_correct_template(self):
        """
        if user is admin template is home_for_admin.html
        """
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertEqual(response.templates[0].name, 'edziennik/home_for_admin.html')

    def test_home_view_for_admin_no_groups(self):
        """
        if there are no groups
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        lector = Lector.objects.create(user=user_john)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertQuerysetEqual(response.context['groups'], [])

    def test_home_view_for_admin_2_groups(self):
        """
        if there are 2 groups
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        lector = Lector.objects.create(user=user_john)
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='admin', password='glassonion')
        group1 = Group.objects.create(name='group1', lector=lector)
        group2 = Group.objects.create(name='group2', lector=lector)
        groups = map(repr, Group.objects.all())
        response = self.client.get(reverse('edziennik:name_home'))
        response_groups = list(response.context['groups'])
        self.assertQuerysetEqual(response_groups, groups)

    def test_home_view_for_admin_no_lectors(self):
        """
        if there are no lectors
        """
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertQuerysetEqual(response.context['lectors'], [])

    def test_home_view_for_admin_2_lectors(self):
        """
        if there are 2 lectors
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        lector = Lector.objects.create(user=user_john)
        user_john2 = User.objects.create_user(username='john2',
                                 email='jlennon@beatles2.com',
                                 password='glassonion2')
        lector2 = Lector.objects.create(user=user_john2)
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        self.client.login(username='admin', password='glassonion')
        lectors = map(repr, Lector.objects.all())
        response = self.client.get(reverse('edziennik:name_home'))
        response_lectors = list(response.context['lectors'])
        self.assertQuerysetEqual(response_lectors, lectors)
    
    def test_home_view_for_parent(self):
        """
        should log in
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        parent = mixer.blend('edziennik.Parent', user=user_john)
        student = mixer.blend('edziennik.Student', parent=parent)
        logged_in = self.client.login(username='john', password='glassonion')
        
        response = self.client.get(reverse('edziennik:name_home'))
    
        self.assertTrue(logged_in)
    

    def test_home_view_others(self):
        """
        if a user is authenticated but is not admin, lector nor parent return 404
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
    
        logged_in = self.client.login(username='john', password='glassonion')
        
        response = self.client.get(reverse('edziennik:name_home'))
        self.assertTrue(logged_in)
        self.assertEqual(response.status_code, 404)


class LectorViewTests(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
            
    def test_lector_view_for_not_admin(self):
        """
        non admin user should not have access - status code 404
        """
        client = Client()
        lector = mixer.blend('edziennik.Lector')
        response = self.client.get(reverse('edziennik:lector', args=(lector.id,)))
        self.assertEqual(response.status_code, 404)

    def test_lector_view_for_admin(self):
        """
        should display only groups associated with one lector
        """
        client = Client()
        lector = mixer.blend('edziennik.Lector')
        lector2 = mixer.blend('edziennik.Lector')
        group1 = Group.objects.create(name='group1', lector=lector)
        group2 = Group.objects.create(name='group2', lector=lector)
        group3 = Group.objects.create(name='group3', lector=lector2)
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:lector', args=(lector.id,)))
        self.assertTrue(logged_in)

        self.assertEqual(response.status_code, 200)
        response_lector_groups= list(response.context['lectors_groups'])
        self.assertEqual(len(response_lector_groups), 2)

    def test_lector_hours_0(self):
        """
        should have no hours
        """
        client = Client()
        lector = mixer.blend('edziennik.Lector')
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(
            reverse('edziennik:lector', args=(lector.id,)))
        self.assertEqual(response.context['total_hours_year'], 0)

    def test_lector_hours_1(self):
        """
        one lector should have no hours, second lector should have 1 hour
        """
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        lector2 = mixer.blend('edziennik.Lector')
        class_date = mixer.blend(
            'edziennik.ClassDate',
            lector=lector2,
            date_of_class=date.today())
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(
            reverse('edziennik:lector', args=(lector2.id,)))
        self.assertEqual(response.context['total_hours_year'], 1)

    def test_lector_hours_current_1(self):
        """
        one lector should have only 1 hour in current school year
        """
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        class_date1 = mixer.blend(
            'edziennik.ClassDate',
            lector=lector1,
            date_of_class=date.today())
        class_date2 = mixer.blend(
            'edziennik.ClassDate',
            lector=lector1,
            date_of_class=date(year=date.today().year -1, month=1, day=1))
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(
            reverse('edziennik:lector', args=(lector1.id,)))
        self.assertEqual(response.context['total_hours_year'], 1)

    @freeze_time('2018-03-10')
    def test_lector_hours_in_march(self):
        """
        one lector should have only 2 hour in current school year (one in dec one in feb),
        tested in march to see if school year definition is correct
        """
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        class_date1 = mixer.blend(
            'edziennik.ClassDate',
            lector=lector1,
            date_of_class=date(year=2018, month=2, day=20))
        class_date2 = mixer.blend(
            'edziennik.ClassDate',
            lector=lector1,
            date_of_class=date(year=2017, month=12, day=20))
        # this should be out of range - previous school year
        class_date2=mixer.blend(
            'edziennik.ClassDate',
            lector = lector1,
            date_of_class=date(year=2017, month=2, day=20))
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(
            reverse('edziennik:lector', args=(lector1.id,)))
        self.assertEqual(response.context['total_hours_year'], 2)

    @freeze_time('2018-03-10')
    def test_lector_hours_in_month(self):
        """
        there should be hours as follows: Oct: 1, Nov: 2, Dec: 0, Jan: 17, Feb:1
        """
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        mixer.blend(
            'edziennik.ClassDate',
            lector=lector1,
            date_of_class=date(year=2017, month=10, day=20))
        for i in range(2):
            mixer.blend(
                'edziennik.ClassDate',
                lector=lector1,
                date_of_class=date(year=2017, month=11, day=20))
        for i in range(17):
            mixer.blend(
                'edziennik.ClassDate',
                lector=lector1,
                date_of_class=date(year=2018, month=1, day=20))
        mixer.blend(
            'edziennik.ClassDate',
            lector=lector1,
            date_of_class=date(year=2018, month=2, day=20))
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(
            reverse('edziennik:lector', args=(lector1.id,)))
        expeced_hours = [
            ('10.2017', 1), ('11.2017', 2), ('1.2018', 17), ('2.2018', 1) ]
        self.assertEqual(
            response.context['hours_in_month_list'], expeced_hours)

class StudentViewTests(TestCase):
    def test_student_view_noerror(self):
        """
        if student's id exists - status code 200
        """
        client = Client()
        student = mixer.blend('edziennik.Student')
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))
        self.assertEqual(response.status_code, 200)
    
    def test_student_view_parent(self):
        """
        a parent should have access to his student
        """
        client = Client()
        user_john = User.objects.create_user(username='john',
                            email='jlennon@beatles.com',
                            password='glassonion')
        parent = Parent.objects.create(user=user_john, phone_number=111111111)
        student = mixer.blend('edziennik.Student',
                              first_name='johny',
                              last_name='smith',
                              parent=parent)
        logged_in = self.client.login(username='john', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))
        self.assertEqual(response.context['student'].id, 1)

    def test_student_view_other_parent(self):
        """
        other parent should have no access to a student
        """
        client = Client()
        user_john = User.objects.create_user(username='john',
                            email='jlennon@beatles.com',
                            password='glassonion')
        parent = Parent.objects.create(user=user_john, phone_number=111111111)
        student = mixer.blend('edziennik.Student', name='little_john', parent=parent)
        student2 = mixer.blend('edziennik.Student', name='myname')
        logged_in = self.client.login(username='john', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student2.id,)))
        self.assertContains(response, 'nie masz uprawnień', status_code=200)

    def test_student_view_admin(self):
        """
        admin should have access to student's grades and attendance
        """
        client = Client()
        student = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        group = mixer.blend('edziennik.Group')
        group.student.add(student, student2)
        grade1 = mixer.blend('edziennik.Grades', student=student, date_of_test=today, group=group)
        grade2 = mixer.blend('edziennik.Grades',
                             student=student, date_of_test=today, group=group)
        grade3 = mixer.blend('edziennik.Grades', student=student2, date_of_test=today, group=group)

        date_of_class = ClassDate.objects.create(date_of_class=today,
                                                lector=mixer.blend('edziennik.Lector'),
                                                group=group)
        date_of_class.student.add(student, student2)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))

        all_student_groups = list(response.context['student_groups'])
        first_group = all_student_groups[0]
        response_grade_list = first_group['grade_list']
        # student has grade1 and grade2
        self.assertEqual(len(response_grade_list), 2)

        response_attendance_table_content= first_group['attendance_table_content']
        # attendance was checked only once, today
        self.assertEqual(len(response_attendance_table_content), 1)

    def test_student_view_has_homework_admin(self):
        """
        should display '+' in attendance table
        """
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        
        student1 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1, name='first_group')
        group1.student.add(student1)
        date_of_class = ClassDate.objects.create(date_of_class=today,
                                                lector=lector1,
                                                group=group1)
        date_of_class.student.add(student1)
        date_of_class.has_homework.add(student1)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student1.id,)))

        all_student_groups = list(response.context['student_groups'])
        first_group = all_student_groups[0]
        response_sign = first_group['attendance_table_content'][0][2]

        self.assertEqual(len(all_student_groups), 1)
        present_sign = '<img src=%s>' % static('img/check_sign_icon_green.png')
        self.assertEqual(response_sign, present_sign)

    def test_student_view_absent_admin(self):
        """
        should display '-' in attendance table
        """
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        group=mixer.blend('edziennik.Group')
        student = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        group.student.add(student, student2)
        date_of_class = ClassDate.objects.create(date_of_class=today-timedelta(1),
                                                lector=lector1,
                                                group=group)
        date_of_class.student.add(student2)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))

        all_student_groups = list(response.context['student_groups'])
        first_group = all_student_groups[0]
        response_attendance_table_content= first_group['attendance_table_content']
        absent_sign = '<img src=%s>' % static('img/x-mark-red.png')
        self.assertEqual(response_attendance_table_content[0][2], absent_sign)

class TestGroupView(TestCase):
    def test_group_view_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(reverse('edziennik:group', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_group_view_for_staff(self):
        """
        should display a list of students in this group, but not others
        """
        client = Client()

        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group')
        group1.student.add(student1, student2)
        group2 = mixer.blend('edziennik.Group')
        group2.student.add(student3)
        grade1 = mixer.blend(
            'edziennik.Grades', student=student1, date_of_test=today, group=group1)
        grade2 = mixer.blend(
            'edziennik.Grades', student=student2, date_of_test=today, group=group1)
        grade3 = mixer.blend(
            'edziennik.Grades', student=student3, date_of_test=today, group=group2)
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')


        

        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:group', args=(group1.id,)))
        self.assertTrue(logged_in)

        self.assertEqual(response.status_code, 200)
        response_table_content= list(response.context['table_content'])

        # table_content[0] shows first row where two first items are fixed and then students
        self.assertEqual(len(response_table_content[0]), 2+2)


class TestShow_Group_GradesView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_show_group_grades_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:show_group_grades', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_show_group_grades_for_staff(self):
        """
        staff user should have access - status code 200,
        yesterday student1 got grade 1, student 2 got grade 2,
        today student 2 got grade 3, and student 3 got grade 4
        """
        client = Client()
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group')
        group1.student.add(student1, student2, student3)


        grade1 = Grades.objects.create(
            date_of_test=today-timedelta(days=1),
            score=1,
            student=student1,
            name='t',
            group=group1
        )

        grade2 = Grades.objects.create(
            date_of_test=today-timedelta(days=1),
            score=2,
            student=student2,
            name='t',
            group=group1
        )
        grade3 = Grades.objects.create(
            date_of_test=today,
            score=3,
            student=student2,
            name='t',
            group=group1
        )
        grade4 = Grades.objects.create(
            date_of_test=today,
            score=4,
            student=student3,
            name='t',
            group=group1
        )

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:show_group_grades', args=(group1.id,))
        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        table_content = response.context['table_content']
        # [['25/07/2019', 't', 1, 2, '-'], ['26/07/2019', 't', '-', 3, 4]]
        yesterday_row = table_content[0]
        today_row = table_content[1]
        # order of items in row: date, name, student1 score, s2 score, s3 score
        # s1 should have grade 1 yesterday
        self.assertEqual(yesterday_row[2], 1)

        # s2 should have grade 2 yesterday
        self.assertEqual(yesterday_row[3], 2)

        # s2 should have grade 3 today
        self.assertEqual(today_row[3], 3)

        # s3 should have grade 4 today
        self.assertEqual(today_row[4], 4)


class TestGroup_CheckView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_group_check_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:group_check', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_group_check_for_staff(self):
        """
        staff user should have access - status code 200,
        there are 3 students,
        2 of the 3 are in the same group,
        """
        client = Client()
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group')
        group1.student.add(student1, student2)

        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:group_check', args=(group1.id,))

        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        group = response.context['group']
        students = response.context['students']
        
        # should return group1
        self.assertEqual(group, group1)

        # there should be 2 students (student1, student2) in this group
        self.assertEqual(students.count(), 2)


class TestAttendance_CheckView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)
    def test_attendance_check_view_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:attendance_check', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_attendance_check_view_for_staff(self):
        """
        staff user should have access - status code 200
        """
        data = {
            'student': [1, 2],
            'class_subject': 'test_subject',
            'homework' : [1,]
        }
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        lector2 = mixer.blend('edziennik.Lector')
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1, student2, student3)
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:attendance_check', args=(group1.id,))
        expected_url = reverse('edziennik:group', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # one ClassDate object should be created
        assert ClassDate.objects.all().count() == 1

        # only lector1 sould have one hour
        assert lector1.classdate_set.all().count() == 1

        # lector2 should have no hours
        assert lector2.classdate_set.all().count() == 0

        # two of the three students should have attendance
        class_date = ClassDate.objects.first()
        assert class_date.student.all().count() == 2

        # one of the three students should have homework
        assert class_date.has_homework.all().count() == 1

    def test_attendance_check_view_for_staff_polish_characters(self):
        """
        polish characters in subject
        """
        data = {
            'student': [1,],
            'class_subject': 'Óweśź ąśćtęź',
            'homework': [1, ]
        }
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        student1 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1)
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:attendance_check', args=(group1.id,))
        expected_url = reverse('edziennik:group', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # one ClassDate object should be created
        assert ClassDate.objects.all().count() == 1

        # ClassDate subject should be: 'Óweśź ąśćtęź'
        self.assertEqual(
            ClassDate.objects.all().first().subject, 'Óweśź ąśćtęź')

    def test_attendance_check_view_for_staff_two_groups(self):
        """
        staff user should have access - status code 200
        student1 is in group 1 and group 2,
        student1 already has attendance today in group 2,
        attendance is checked in group 1
        """
        data = {
            'student': [1, 2],
            'class_subject': 'test_subject',
            'homework' : [1,]
        }
        client = Client()
        lector1 = mixer.blend('edziennik.Lector')
        lector2 = mixer.blend('edziennik.Lector')
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group2 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1, student2, student3)
        group2.student.add(student1)
        mixer.blend('edziennik.ClassDate',
                    date_of_class=today,
                    group=group2,
                    student=[1],
                    subject='test_subject')
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:attendance_check', args=(group1.id,))
        expected_url = reverse('edziennik:group', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # there should be two ClassDate objects
        assert ClassDate.objects.all().count() == 2

        # newly created ClassDate should have student1 and student2
        cd = ClassDate.objects.all().last()
        students = cd.student.all()
        self.assertTrue(students.filter(id=student1.id).exists())
        self.assertTrue(students.filter(id=student1.id).exists())



class TestAttendance_By_GroupView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_attendance_by_group_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:attendance_by_group', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_attendance_by_group_for_staff(self):
        """
        staff user should have access - status code 200,
        attendance was checked yesterday and today (should be 2 dates),
        yesterday only student1 present with homework,
        today there should student2 and student3 present and student1 absent,
        today student2 with and student3 without homework,
        """
        client = Client()
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group')
        group1.student.add(student1, student2, student3)
        c_date1 = mixer.blend('edziennik.ClassDate',
                              date_of_class=today - timedelta(days=1),
                              group=group1)
        c_date1.student.add(student1)
        c_date1.has_homework.add(student1)
        c_date2 = mixer.blend('edziennik.ClassDate',
                              date_of_class=today,
                              group=group1)
        c_date2.student.add(student2, student3)
        c_date2.has_homework.add(student2)

        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:attendance_by_group', args=(group1.id,))

        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        table_content = list(response.context['table_content'])
        # [['25/07/2019', 'testowy temat', '<img sr[159 chars]g>']...
        yesterday_row = table_content[0]
        today_row = table_content[1]
        # there should be two dates displayed (yesterdays and todays)
        self.assertEqual(len(table_content), 2)
        date1 = yesterday_row[0]
        date2= today_row[0]
        self.assertEqual(date1, (today-timedelta(days=1)).strftime("%d/%m/%Y"))
        self.assertEqual(date2, today.strftime("%d/%m/%Y"))

        # student1 should have attendance and homework yesterday, 2 and 3 should not
        """ attendance with homework == 'img/check_sign_icon_green.png'
            absence == 'img/x-mark-red.png'
            order of students in table head: 'date', 'subject', student1, s2, s3..
        """
        present_with_hw = '<img src=%s>' % static('img/check_sign_icon_green.png')
        absent_sign = '<img src=%s>' % static('img/x-mark-red.png')
        self.assertEqual(present_with_hw, yesterday_row[2])

        # student2 and student3 should not have absence yesterday
        self.assertEqual(absent_sign, yesterday_row[3])
        self.assertEqual(absent_sign, yesterday_row[4])

        # student2 and present today with homework
        self.assertEqual(present_with_hw, today_row[3])

        # student1 absent today
        self.assertEqual(absent_sign, today_row[2])

        # student3 present today but no homework
        present_with_no_hw = '<img src=%s>' % static(
            'img/green_on_red.png')
        self.assertEqual(present_with_no_hw, today_row[4])


class TestGroup_GradesView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_group_grades_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:group_grades', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_group_grades_for_staff(self):
        """
        staff user should have access - status code 200,
        there are 3 students,
        2 of the 3 are in the same group,
        """
        client = Client()
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group')
        group1.student.add(student1, student2)

        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:group_grades', args=(group1.id,))

        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        group = response.context['group']
        students = response.context['students']

        # should return group1
        self.assertEqual(group, group1)

        # there should be 2 students (student1, student2) in this group
        self.assertEqual(students.count(), 2)

class TestAdd_GradesView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_add_grades_view_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:add_grades', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_add_grades_view_for_staff_no_grades_today(self):
        """
        staff user should have access - status code 200
        """
        data = {
            's1 s1': 1,
            's2 s2': 2,
            'grade_name': 'test grade',
            'date_of_test': today
        }
        client = Client()
        group1 = mixer.blend('edziennik.Group')
        student1 = mixer.blend('edziennik.Student',
                               first_name='s1', last_name='s1')
        student2 = mixer.blend('edziennik.Student',
                               first_name='s2', last_name='s2')
        student3 = mixer.blend('edziennik.Student',
                               first_name='s3', last_name='s3')
        group1.student.add(student1, student2, student3)
        logged_in = self.client.login(
            username='admin', password='glassonion')
  
        url = reverse('edziennik:add_grades', args=(group1.id,))
        expected_url = reverse('edziennik:group', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # two Grade objects should be created
        assert Grades.objects.all().count() == 2

        # date of both grades should be today
        assert Grades.objects.filter(date_of_test=today).count() == 2

        # student1 should have grade 1
        grade = Grades.objects.get(student=student1)
        self.assertEqual(grade.score, 1)

        # student 2 should have grade 2
        grade2 = Grades.objects.get(student=student2)
        self.assertEqual(grade2.score, 2)

        # student 3 should have no grades
        self.assertFalse(Grades.objects.filter(student=student3).exists())


    def test_add_grades_view_for_staff_preexisting_grade_today_in_this_group(self):
        """
        staff user should have access - status code 200
        student already has today's grade with this name in this group
        should redirect to group_grades
        should generate message about duplicate grade
        """
        data = {
            's1 s1': 1,
            's2 s2': 2,
            'grade_name': 'test grade',
            'date_of_test': today
        }
        client = Client()
        group1 = mixer.blend('edziennik.Group')
        student1 = mixer.blend('edziennik.Student',
                               first_name='s1', last_name='s1')
        student2 = mixer.blend('edziennik.Student',
                               first_name='s2', last_name='s2')
        student3 = mixer.blend('edziennik.Student',
                               first_name='s3', last_name='s3')
        group1.student.add(student1, student2, student3)
        mixer.blend('edziennik.Grades',
            group=group1,
            date_of_test=today,
            student=student2,
            name='test grade',
            score=6)
        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:add_grades', args=(group1.id,))
        expected_url = reverse('edziennik:group_grades', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        # should redirect
        self.assertRedirects(response, expected_url,
                     status_code=302, target_status_code=200)

        # two Grade objects should exists (one new and one preexisting)
        assert Grades.objects.all().count() == 2

        # date of both grades should be today
        assert Grades.objects.filter(date_of_test=today).count() == 2

        # student1 should have grade 1
        grade = Grades.objects.get(student=student1)
        self.assertEqual(grade.score, 1)

        # student 2 should have grade 6, preexisting, and no other
        grade2 = Grades.objects.get(student=student2)
        self.assertEqual(grade2.score, 6)

        # student 3 should have no grades
        self.assertFalse(Grades.objects.filter(student=student3).exists())

        # should display message about preexisting grade
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        expectd_msg = "Ocena za %s  w dniu %s byla juz dodana uczniowi %s. Sprobuj jeszcze raz" % (
            'test grade', today, str(student2))
        self.assertEqual(all_messages[0].message, expectd_msg)

    def test_add_grades_view_for_staff_preexisting_grade_today_different_group(self):
        """
        staff user should have access - status code 200
        student already has a grade with this name today but in different group
        should proceed with adding grades in this group as normal
        """
        data = {
            's1 s1': 1,
            's2 s2': 2,
            'grade_name': 'test grade',
            'date_of_test': today
        }
        client = Client()
        group1 = mixer.blend('edziennik.Group')
        group2 = mixer.blend('edziennik.Group')
        student1 = mixer.blend('edziennik.Student',
                               first_name='s1', last_name='s1')
        student2 = mixer.blend('edziennik.Student',
                               first_name='s2', last_name='s2')
        student3 = mixer.blend('edziennik.Student',
                               first_name='s3', last_name='s3')
        group1.student.add(student1, student2, student3)
        group2.student.add(student1, student2, student3)
        mixer.blend('edziennik.Grades',
            group=group2,
            date_of_test=today,
            student=student1,
            name='test grade',
            score=6)
        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:add_grades', args=(group1.id,))
        expected_url = reverse('edziennik:group_grades', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
      
        # three Grade objects should exists (two new and one preexisting)
        assert Grades.objects.all().count() == 3

        # date of all grades should be today
        assert Grades.objects.filter(date_of_test=today).count() == 3

        # student1 should have grade 1 in group 1
        grade = Grades.objects.get(student=student1, group=group1)
        self.assertEqual(grade.score, 1)

        # student1 should have grade 6 in group 2
        grade = Grades.objects.get(student=student1, group=group2)
        self.assertEqual(grade.score, 6)

        # student 2 should have grade 2 in group 1
        grade2 = Grades.objects.get(student=student2)
        self.assertEqual(grade2.score, 2)

        # student 3 should have no grades
        self.assertFalse(Grades.objects.filter(student=student3).exists())

       
class TestAdd_QuizletView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_add_quizlet_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:add_quizlet', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_add_quizlet_for_staff(self):
        """
        staff user should have access - status code 200,
        there are 3 students,
        2 of the 3 are in the same group,
        """
        client = Client()
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group')
        group1.student.add(student1, student2)

        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:add_quizlet', args=(group1.id,))

        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        group = response.context['group']
        students = response.context['students']

        # should return group1
        self.assertEqual(group, group1)

        # there should be 2 students (student1, student2) in this group
        self.assertEqual(students.count(), 2)


class TestProcess_QuizletView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)

    def test_process_quizlet_view_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:process_quizlet', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_process_quizlet_view_for_staff_no_preexisting_quizlet(self):
        """
        staff user should have access - status code 200
        two groups with same students,
        quizlet True only in studetns in group1
        only students from group1 should get quizlet points
        """
        data = {
            'student': [1,2]
        }
        client = Client()
        group1 = mixer.blend('edziennik.Group')
        group2 = mixer.blend('edziennik.Group')
        student1 = mixer.blend('edziennik.Student',
                               first_name='s1', last_name='s1')
        student2 = mixer.blend('edziennik.Student',
                               first_name='s2', last_name='s2')
        student3 = mixer.blend('edziennik.Student',
                               first_name='s3', last_name='s3')
        group1.student.add(student1, student2, student3)
        group2.student.add(student1, student2, student3)
        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:process_quizlet', args=(group1.id,))
        expected_url = reverse('edziennik:name_home')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        # should redirect
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200)


        # student2 should have quizlet status True in group1
        self.assertTrue(Quizlet.objects.get(student=student1, group=group1).status)

        # student1 should have quizlet status False in group2
        self.assertFalse(Quizlet.objects.get(
            student=student1, group=group2).status)

        # student2 should have quizlet status True in group1
        self.assertTrue(Quizlet.objects.get(
            student=student2, group=group1).status)

        # student2 should have quizlet status False in group2
        self.assertFalse(Quizlet.objects.get(
            student=student2, group=group2).status)

        # student1 should have quizlet status False in group 1 and group2
        self.assertFalse(Quizlet.objects.get(
            student=student3, group=group1).status)
        self.assertFalse(Quizlet.objects.get(
            student=student3, group=group2).status)

        # should display success message
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        expectd_msg = "Punkty za quizlet w grupie %s dodane" % group1
        self.assertEqual(all_messages[0].message, expectd_msg)


class TestAdvanced_SettingsView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
        username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
        'john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)
    def test_advanced_settings_unauthorized(self):
        '''should return 404 error for unauthorized users'''
        client = Client()
        url = reverse('edziennik:advanced_settings')
        response = self.client.get(url, follow=True)
        # should give code 404 as follow is set to True
        assert response.status_code == 404
    
    def test_advanced_settings_non_admin(self):
        '''should return 404 error for non admin users'''
        client = Client()
        logged_in = self.client.login(
            username='john', password='johnpassword')
        url = reverse('edziennik:advanced_settings')
        response = self.client.get(url, follow=True)
        # should give code 404 as follow is set to True
        assert response.status_code == 404

    def test_advanced_settings_admin_first_time(self):
        '''should be accesible for admin user (status code: 200),
        should create one instance of Admin_Profile class,
        should use proper template (advanced_settings.html)'''
        client = Client()
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:advanced_settings')
        response = self.client.get(url, follow=True)

        # should give code 200 as follow is set to True
        assert response.status_code == 200
        # should use proper tempate
        self.assertEqual(
            response.templates[0].name, 'edziennik/advanced_settings.html')
        # there should be one instance when visited for the first time
        instances = len(Admin_Profile.objects.all())
        self.assertEqual(instances, 1)

    def test_advanced_settings_admin_again(self):
        '''should not create new instance of Admin_Profile class,
        should use proper template (advanced_settings.html)'''

        Admin_Profile.objects.create(
            user = User.objects.get(username='admin'),
            quizlet_username='testuser',
            quizlet_password='testpass'
        )
        client = Client()
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:advanced_settings')
        response = self.client.get(url, follow=True)

        # should use proper tempate
        self.assertEqual(
            response.templates[0].name, 'edziennik/advanced_settings.html')
        # there should be only one instance
        instances = len(Admin_Profile.objects.all())
        self.assertEqual(instances, 1)
        # instance properties should not change
        instance = Admin_Profile.objects.get(pk=1)
        self.assertEqual(instance.quizlet_username, 'testuser')
        self.assertEqual(instance.quizlet_password, 'testpass')

    def test_advanced_settings_admin_with_other_admin(self):
        '''should not create new instance of Admin_Profile class,
        should have access to instance previously created by another admin'''
        # another admin
        User.objects.create_superuser(
            username='admin2', email='jlennon@beatles.com', password='glassonion')
        # instance created by another user
        Admin_Profile.objects.create(
            user=User.objects.get(username='admin2'),
            quizlet_username='testuser',
            quizlet_password='testpass'
        )
        client = Client()
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:advanced_settings')
        response = self.client.get(url, follow=True)

        # there should be only one instance
        instances = len(Admin_Profile.objects.all())
        self.assertEqual(instances, 1)
        # instance properties set by another admin should not change
        old = Admin_Profile.objects.get(pk=1)
        self.assertEqual(old.quizlet_username, 'testuser')
        self.assertEqual(old.quizlet_password, 'testpass')

    def test_advanced_settings_admin_post(self):
        '''should not create new instance of Admin_Profile class,
        should update fields'''
        # instance created by GET call
        Admin_Profile.objects.create(
            user=User.objects.get(username='admin'),
        )
        client = Client()
        logged_in = self.client.login(
            username='admin', password='glassonion')
        url = reverse('edziennik:advanced_settings')

        data = {
            'quizlet_username': 'testuser',
            'quizlet_password': 'testpass'
        }
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        # should use proper tempate
        self.assertEqual(
            response.templates[0].name, 'edziennik/home_for_admin.html')

        # there should be only one instance
        instances = len(Admin_Profile.objects.all())
        self.assertEqual(instances, 1)
        # instance properties set by another admin should not change
        updated = Admin_Profile.objects.get(pk=1)
        self.assertEqual(updated.quizlet_username, 'testuser')
        self.assertEqual(updated.quizlet_password, 'testpass')
        all_messages = [msg for msg in get_messages(response.wsgi_request)]
        self.assertEqual(all_messages[0].tags, "success")
        self.assertEqual(all_messages[0].message, 'Ustawienia zachowane')
