# -*- coding: utf-8 -*-
import io
import os
import shutil
import tempfile
import pytest
from datetime import date, datetime, timedelta

from django.conf import settings
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.messages import get_messages
from mixer.backend.django import mixer

from django.templatetags.static import static
from freezegun import freeze_time
from edziennik.models import (Lector, Group, Parent, Student, ClassDate, Grades,
                              Admin_Profile, Quizlet, Initial_Import, Initial_Import_Usage,
                              Initial_Import_Usage_Errors)
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

    def test_home_view_for_admin_2_parents(self):
        """there are 2 parents"""
        mixer.blend('edziennik.Parent')
        mixer.blend('edziennik.Parent')
        user_admin = User.objects.create_superuser(username='admin',
                                                   email='jlennon@beatles.com',
                                                   password='glassonion')
        self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:name_home'))
        response_parents = response.context['recent_parents']
        self.assertEqual(len(response_parents), 2)

    
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


# LECTOR

class Test_Lector_Create(TestCase):
    def setUp(self):
        User.objects.create_superuser(
        username='admin', email='jlennon@beatles.com', password='glassonion')

    def test_for_non_admin(self):
        """non admin user should not have access - status code 403"""
        client = Client()
        response = self.client.get(reverse('edziennik:lector_create'))
        self.assertEqual(response.status_code, 403)

    def test_no_preexisting_lectors(self):
        """no preexisting lectors, correct data, should create one Lector instance"""
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:lector_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # should create 1 Lector
        self.assertEqual(Lector.objects.all().count(), 1)
        # parent should have initial_password
        self.assertEqual(len(Lector.objects.all().first().initial_password), 8)

        # should create 1 User with first name 'Adam', last name 'Nowak' and proper email
        self.assertEqual(User.objects.all().count(), 2)  # 1 admin and 1 new
        new_user = User.objects.all().last()
        self.assertEqual(new_user.first_name, 'Adam')
        self.assertEqual(new_user.last_name, 'Nowak')
        self.assertEqual(new_user.email, 'adam@gmail.com')

        # lector.user should be staff
        self.assertTrue(new_user.is_staff)

    def test_email_taken(self):
        """1 preexisting lector, email already taken, should not create Lector instance"""
        u = User.objects.create(username='al', email='adam@gmail.com', password='testpass')
        mixer.blend('edziennik.Lector', user=u)
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:lector_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response 'errors' should indicate phone
        self.assertContains(response, 'email')

        # should not create Lector, 1 Lector aleready exists
        self.assertEqual(Lector.objects.all().count(), 1)


    def test_no_email(self):
        """1 preexisting lector, no email given, should create 1 Lector instance,
        should generate fake email"""
        u = User.objects.create(
            username='al', email='adam@gmail.com', password='testpass')
        mixer.blend('edziennik.Lector', user=u)
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:lector_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # should create 1 Lector, 1 Lector aleready exists
        self.assertEqual(Lector.objects.all().count(), 2)

        # new Lector should have a fake, unique email
        self.assertIn('@test.test', Lector.objects.all().last().user.email)


class Test_Lector_Update(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')

    def test_for_non_admin(self):
        """non admin user should not have access - status code 403"""
        client = Client()
        response = self.client.get(reverse('edziennik:lector_update', args=(1,)))
        self.assertEqual(response.status_code, 403)

    def test_admin(self):
        """1 preexisting lector, correct data, should update Lector instance"""
        u = User.objects.create(
            username='al', email='ffff@gmail.com', password='testpass')
        mixer.blend('edziennik.Lector', user=u)
        data = {
            'first_name': 'adam',
            'last_name': 'nowak',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:lector_update', args=(1,))
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # should update but not create
        self.assertEqual(Lector.objects.all().count(), 1)

        # should create 1 User with first name 'Adam', last name 'Nowak' and proper email
        self.assertEqual(User.objects.all().count(), 2)  # 1 admin and 1 new
        new_user = User.objects.all().last()
        self.assertEqual(new_user.first_name, 'Adam') # should capitalize first name
        self.assertEqual(new_user.last_name, 'Nowak') # should capitalize last name
        self.assertEqual(new_user.email, 'adam@gmail.com')


class Test_Lector_List(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')

    def test_for_non_admin(self):
        """non admin user should not have access - status code 403"""
        client = Client()
        response = self.client.get(reverse('edziennik:lector_list'))
        self.assertEqual(response.status_code, 403)

    def test_admin(self):
        # should contain details of two lectors
        l1 = mixer.blend('edziennik.Lector')
        l2 = mixer.blend('edziennik.Lector')
        client = Client()
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:lector_list'))
        self.assertTrue(logged_in)

        self.assertEqual(response.status_code, 200)

        response_lectors= response.context['object_list']
        # lector l1 should be in response_lectors
        self.assertTrue(response_lectors.filter(id=l1.id).exists())
        # lector l2 should be in response_lectors
        self.assertTrue(response_lectors.filter(id=l2.id).exists())
        # there should be 2 Lectors in response_lectors
        self.assertEqual(response_lectors.count(), 2)


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
        self.client.login(username='admin', password='glassonion')
        response = self.client.get(
            reverse('edziennik:lector', args=(lector1.id,)))
        expeced_hours = [
            ('10.2017', 1), ('11.2017', 2), ('1.2018', 17), ('2.2018', 1) ]
        self.assertEqual(
            response.context['hours_in_month_list'], expeced_hours)

    def test_lector_add_groups(self):
        '''when new group ids are posted, the lector should be assigned to groups'''
        u = User.objects.create_user(
            username='lect', email='sdrj@adl.com', password='aksdfneina')
        l = mixer.blend('edziennik.Lector', user=u)
        g1 = mixer.blend('edziennik.Group', lector=l)
        g2 = mixer.blend('edziennik.Group')
        g3 = mixer.blend('edziennik.Group')

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:lector', args=(g1.id,))
        data = {'newGroups': [g2.id, g3.id]}
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        self.assertEqual(response.status_code, 200)
        # lector l should be now linked to the group g1
        g1.refresh_from_db()
        self.assertEqual(g1.lector, l)
        # lector l should be now linked to the group g2
        g2.refresh_from_db()
        self.assertEqual(g2.lector, l)
        # lector l should be now linked to the group g3
        g3.refresh_from_db()
        self.assertEqual(g3.lector, l)

    def test_lector_remove_groups(self):
        '''when del group ids are posted, the lector should be removed from the groups'''
        u = User.objects.create_user(
            username='lect', email='sdrj@adl.com', password='aksdfneina')
        l = mixer.blend('edziennik.Lector', user=u)
        g1 = mixer.blend('edziennik.Group', lector=l)
        g2 = mixer.blend('edziennik.Group', lector=l)
        g3 = mixer.blend('edziennik.Group', lector=l)

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:lector', args=(g1.id,))
        data = {'delGroups': [g2.id, g3.id]}
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        self.assertEqual(response.status_code, 200)
        # lector l should be now linked to the group g1
        g1.refresh_from_db()
        self.assertEqual(g1.lector, l)
        # lector l should not be linked to the group g2
        g2.refresh_from_db()
        self.assertFalse(g2.lector)
        # lector l should not be linked to the group g3
        g3.refresh_from_db()
        self.assertFalse(g3.lector)


# STUDENT

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
        a parent should have access to his student,
        parent should see grades and homework (last 3 in each group)
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
        student2 = mixer.blend('edziennik.Student')
        lector = mixer.blend('edziennik.Lector')
        g1 = mixer.blend('edziennik.Group', lector=lector)
        g1.student.add(student, student2)
        g2 = mixer.blend('edziennik.Group', lector=lector)
        g2.student.add(student, student2)
        grade1 = mixer.blend('edziennik.Grades',
                             date_of_test=today - timedelta(days=1),
                             score=1,
                             group=g1,
                             student=student)
        grade2 = mixer.blend('edziennik.Grades',
                             date_of_test=today,
                             score=2,
                             group=g2,
                             student=student)
        cd1 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=1),
                    group=g1)
        cd2 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today,
                    group=g2)
        cd3 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=2),
                    group=g2)
        cd4 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=3),
                    group=g2)
        cd5 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=4),
                    group=g2)
        homework_yesterday_g1 = 'Test homework, g1, yesterday'
        homework_today_g2 = 'Test homework, g2, today'
        homework_2_g2 = 'Test homework, g2, 2days'
        homework_3_g2 = 'Test homework, g2, 3days'
        homework_4_g2 = 'Test homework, g2, 4days'
        mixer.blend('edziennik.Homework',
                    classdate = cd1,
                    message=homework_yesterday_g1
        )
        mixer.blend('edziennik.Homework',
                    classdate = cd3,
                    message=homework_2_g2
        )
        mixer.blend('edziennik.Homework',
                    classdate = cd4,
                    message=homework_3_g2
        )
        mixer.blend('edziennik.Homework',
                    classdate = cd5,
                    message=homework_4_g2
        )
        mixer.blend('edziennik.Homework',
                            classdate=cd2,
                            message=homework_today_g2
                            )
        logged_in = self.client.login(username='john', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))
        self.assertEqual(response.context['student'].id, 1)

        # should see grades - yesterday, in group g1, student got 1, today in g2 - 2
        for i in response.context['student_groups']:
            if i['group']==g1:
                response_group1 = i
            if i['group']==g2:
                response_group2 = i
        g1_response_score = response_group1['grade_list'][0][2]
        # in group g1 yesterday score should be 1:
        self.assertEqual(g1_response_score, 1)

        g2_response_score = response_group2['grade_list'][0][2]
        # in group g2 yesterday score should be 2:
        self.assertEqual(g2_response_score, 2)

        # should see homeworks (at most last 3 in each group)
        g1_response_homeworks = response_group1['homeworks']
        # there should be 1 homework in g1, text: 'Test homework, g1, yesterday'
        self.assertEqual(g1_response_homeworks.count(), 1)
        self.assertEqual(g1_response_homeworks.first().message,
                         'Test homework, g1, yesterday')
        # there should be 3 visible homeworks out of total 4 in g2
        g2_response_homeworks = response_group2['homeworks']
        self.assertEqual(g2_response_homeworks.count(), 3)

        # there should be homework added today with message:
        # 'Test homework, g2, today', this homework should be first
        self.assertEqual(g2_response_homeworks.first().message,
                         'Test homework, g2, today')



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
        lector = mixer.blend('edziennik.Lector')
        group = mixer.blend('edziennik.Group', lector=lector)
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
        Client()
        lector1 = mixer.blend('edziennik.Lector')
        group = mixer.blend('edziennik.Group', lector=lector1)
        student = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        group.student.add(student, student2)
        date_of_class = ClassDate.objects.create(date_of_class=today-timedelta(1),
                                                lector=lector1,
                                                group=group)
        date_of_class.student.add(student2)

        User.objects.create_superuser(username='admin',
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


class Test_Student_Create_View(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')

    def test_student_create_view_for_non_admin(self):
        """
        non admin should not have access - status code 403 Forbidden - PermissionDenied
        """
        client = Client()
        response = self.client.get(
            reverse('edziennik:student_create'), follow=True)
        self.assertEqual(response.status_code, 403)

    def test_student_create_admin(self):
        """Student should be created and bound to correct Parent"""
        mixer.blend('edziennik.Parent')
        p2 = mixer.blend('edziennik.Parent')
        mixer.blend('edziennik.Parent')
        url = reverse('edziennik:student_create')
        data = {
            'parent': p2.id,
            'first_name': 'Adam',
            'last_name': 'NowaćĄŁ',
            'gender': 'M'
        }
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.post(url, data, follow=True)
        self.assertTrue(logged_in)
        self.assertEqual(response.status_code, 200)

        # should create one Student instance
        self.assertEqual(Student.objects.all().count(), 1)
        # Students parent should be p2
        s = Student.objects.all().first()
        self.assertEqual(s.parent, p2)


# PARENT

class Test_Parent_Create(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')

    def test_for_non_admin(self):
        """non admin user should not have access - status code 403"""
        client = Client()
        response = self.client.get(reverse('edziennik:parent_create'))
        self.assertEqual(response.status_code, 403)

    def test_no_preexisting_parents(self):
        """no preexisting parents, correct data, should create one Parent instance"""
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:parent_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # should create 1 Parent
        self.assertEqual(Parent.objects.all().count(), 1)
        # parent should have initial_password
        self.assertEqual(len(Parent.objects.all().first().initial_password), 8)

        # should create 1 User with first name 'Adam', last name 'Nowak' and proper email
        self.assertEqual(User.objects.all().count(), 2)  # 1 admin and 1 new
        new_user = User.objects.all().last()
        self.assertEqual(new_user.first_name, 'Adam')
        self.assertEqual(new_user.last_name, 'Nowak')
        self.assertEqual(new_user.email, 'adam@gmail.com')

    def test_email_taken(self):
        """1 preexisting parent, email already taken, should not create Parent instance"""
        mixer.blend('edziennik.Parent', email='adam@gmail.com')
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:parent_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)

    def test_phone_taken(self):
        """1 preexisting parent, phone number already taken, should not create Parent instance"""
        mixer.blend('edziennik.Parent', phone_number=123123123)
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:parent_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response 'errors' should indicate phone
        self.assertContains(response, 'phone_number')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)

    def test_phone_and_email_taken(self):
        """1 preexisting parent, phone number and email already taken,
        should not create Parent instance"""
        mixer.blend('edziennik.Parent', phone_number=123123123,
                    email='adam@gmail.com')
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:parent_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response 'errors' should indicate phone
        self.assertContains(response, 'phone_number')
        # response 'errors' should indicate email
        self.assertContains(response, 'email')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)

    def test_no_email(self):
        """1 preexisting parent, no email given, should create 1 Parent instance,
        should generate fake email"""
        mixer.blend('edziennik.Parent')
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'phone_number': '123123123',
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:parent_create')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # should create 1 Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 2)

        # new Parent should have a fake, unique email
        self.assertIn('@test.test', Parent.objects.all().last().email)

    def test_no_phone(self):
        """1 preexisting parent, no phone number given,
        should not create Parent instance"""
        mixer.blend('edziennik.Parent')
        data = {
            'first_name': 'Adam',
            'last_name': 'Nowak',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response 'errors' should indicate phone
        self.assertContains(response, 'phone_number')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)


class Test_Create_Parent_Ajax(TestCase):
    def setUp(self):
        User.objects.create_superuser(
        username='admin', email='jlennon@beatles.com', password='glassonion')
        
    def test_for_non_admin(self):
        """non admin user should not have access - status code 404"""
        client = Client()
        response = self.client.get(reverse('edziennik:create_parent_ajax'))
        self.assertEqual(response.status_code, 404)

    def test_no_preexisting_parents(self):
        """no preexisting parents, correct data, should create one Parent instance"""
        data = {
            'parent_first_name': 'Adam',
            'parent_last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }
        
        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        self.assertContains(response, 'Success!')

        # should create 1 Parent
        self.assertEqual(Parent.objects.all().count(), 1)
        # parent should have initial_password
        self.assertEqual(len(Parent.objects.all().first().initial_password), 8)

        # should create 1 User with first name 'Adam', last name 'Nowak' and proper email
        self.assertEqual(User.objects.all().count(), 2) # 1 admin and 1 new
        new_user = User.objects.all().last()
        self.assertEqual(new_user.first_name, 'Adam')
        self.assertEqual(new_user.last_name, 'Nowak')
        self.assertEqual(new_user.email, 'adam@gmail.com')

    def test_email_taken(self):
        """1 preexisting parent, email already taken, should not create Parent instance,
        should return 'Error' in response result"""
        mixer.blend('edziennik.Parent', email='adam@gmail.com')
        data = {
            'parent_first_name': 'Adam',
            'parent_last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response result should be 'Error'
        self.assertContains(response, 'Error')
        # response 'errors' should indicate email
        self.assertContains(response, 'email')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)

    def test_phone_taken(self):
        """1 preexisting parent, phone number already taken, should not create Parent instance,
        should return 'Error' in response result"""
        mixer.blend('edziennik.Parent', phone_number=123123123)
        data = {
            'parent_first_name': 'Adam',
            'parent_last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response result should be 'Error'
        self.assertContains(response, 'Error')
        # response 'errors' should indicate phone
        self.assertContains(response, 'phone_number')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)

    def test_phone_and_email_taken(self):
        """1 preexisting parent, phone number and email already taken, should not create Parent instance,
        should return 'Error' in response result"""
        mixer.blend('edziennik.Parent', phone_number=123123123, email='adam@gmail.com')
        data = {
            'parent_first_name': 'Adam',
            'parent_last_name': 'Nowak',
            'phone_number': '123123123',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response result should be 'Error'
        self.assertContains(response, 'Error')
        # response 'errors' should indicate phone
        self.assertContains(response, 'phone_number')
        # response 'errors' should indicate email
        self.assertContains(response, 'email')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)

    def test_no_email(self):
        """1 preexisting parent, no email given, should create 1 Parent instance,
        should return 'Success!' in response result, should generate fake email"""
        mixer.blend('edziennik.Parent')
        data = {
            'parent_first_name': 'Adam',
            'parent_last_name': 'Nowak',
            'phone_number': '123123123',
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response result should be 'Success!'
        self.assertContains(response, 'Success!')

        # should create 1 Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 2)

        # new Parent should have a fake, unique email
        self.assertIn('@test.test', Parent.objects.all().last().email)

    def test_no_phone(self):
        """1 preexisting parent, no phone number given, should not create Parent instance,
        should return 'Error' in response result"""
        mixer.blend('edziennik.Parent')
        data = {
            'parent_first_name': 'Adam',
            'parent_last_name': 'Nowak',
            'email': 'adam@gmail.com'
        }

        logged_in = self.client.login(
            username='admin', password='glassonion')

        url = reverse('edziennik:create_parent_ajax')
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # response result should be 'Success!'
        self.assertContains(response, 'Error')
        # response 'errors' should indicate phone
        self.assertContains(response, 'phone_number')

        # should not create Parent, 1 Parent aleready exists
        self.assertEqual(Parent.objects.all().count(), 1)


class TestGroupView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
        username='admin', email='jlennon@beatles.com', password='glassonion')

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
        should display a list of students in this group, but not others,
        should display all homeworks in this group in reverse chronological order
        """
        client = Client()
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        lector = mixer.blend('edziennik.Lector')
        g1 = mixer.blend('edziennik.Group', lector=lector)
        g1.student.add(student1, student2)
        g2 = mixer.blend('edziennik.Group', lector=lector)
        g2.student.add(student3)

        cd1 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=1),
                    group=g2)
        cd2 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today,
                    group=g1)
        cd3 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=2),
                    group=g1)
        cd4 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=3),
                    group=g1)
        cd5 = mixer.blend('edziennik.ClassDate',
                    date_of_class=today-timedelta(days=4),
                    group=g1)
        homework_yesterday_g2 = 'Test homework, g2, yesterday'
        homework_today_g1 = 'Test homework, g1, today'
        homework_2_g1 = 'Test homework, g1, 2days'
        homework_3_g1 = 'Test homework, g1, 3days'
        homework_4_g1 = 'Test homework, g1, 4days'
        mixer.blend('edziennik.Homework',
                    classdate = cd1,
                    message=homework_yesterday_g2
        )
        mixer.blend('edziennik.Homework',
                    classdate = cd3,
                    message=homework_2_g1
        )
        mixer.blend('edziennik.Homework',
                    classdate = cd4,
                    message=homework_3_g1
        )
        mixer.blend('edziennik.Homework',
                    classdate = cd5,
                    message=homework_4_g1
        )
        mixer.blend('edziennik.Homework',
                    classdate=cd2,
                    message=homework_today_g1
                            )

        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:group', args=(g1.id,)))
        self.assertTrue(logged_in)

        self.assertEqual(response.status_code, 200)

        response_students= response.context['students']
        # student1 should be in response_students
        self.assertTrue(response_students.filter(id=student1.id).exists())

        # student2 should be in response_students
        self.assertTrue(response_students.filter(id=student2.id).exists())

        # student3 should not be in response_students
        self.assertFalse(response_students.filter(
            id=student3.id).exists())

        # there should be 4 homeworks in g1 (and one in g2 - not displayed here)
        h_in_g1 = response.context['homeworks']
        self.assertEqual(h_in_g1.count(), 4)

        # first homework should be from today
        self.assertEqual(h_in_g1.first().classdate.date_of_class, today)


    def test_group_lector_change(self):
        '''when new lector id is posted, new lector should be assigned to a group'''
        l1 = mixer.blend('edziennik.Lector')
        l2 = mixer.blend('edziennik.Lector')
        g = mixer.blend('edziennik.Group', lector=l1)
        
        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:group', args=(g.id,))
        data = {'newLectorId': l2.id}
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        self.assertEqual(response.status_code, 200)
        # lector l2 should be now linked to the group
        g.refresh_from_db()
        self.assertEqual(g.lector, l2)

    def test_group_add_student(self):
        '''when new student id is posted, new student should be assigned to a group'''
        s1 = mixer.blend('edziennik.Student')
        s2 = mixer.blend('edziennik.Student')
        s3 = mixer.blend('edziennik.Student')
        g = mixer.blend('edziennik.Group')
        g.student.add(s1)

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:group', args=(g.id,))
        data = {'newStudentId': [s2.id, s3.id]}
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        self.assertEqual(response.status_code, 200)
        g.refresh_from_db()
        # student s1 should still be linked to the group
        self.assertIn(s1, g.student.all())
        # student s2 should be now linked to the group
        self.assertIn(s2, g.student.all())
        # student s3 should be now linked to the group
        self.assertIn(s3, g.student.all())

    def test_group_remove_student(self):
        '''when student id is posted, student should be removed from the group'''
        s1 = mixer.blend('edziennik.Student')
        s2 = mixer.blend('edziennik.Student')
        s3 = mixer.blend('edziennik.Student')
        g = mixer.blend('edziennik.Group')
        g.student.add(s1, s2, s3)

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:group', args=(g.id,))
        data = {'delStudentId': [s2.id, s3.id]}
        response = self.client.post(url, data, follow=True)

        print('test lll: ', [s2.id, s3.id])
        # should give code 200 as follow is set to True
        self.assertEqual(response.status_code, 200)
        g.refresh_from_db()
        # student s1 should still be linked to the group
        self.assertIn(s1, g.student.all())
        # student s2 should not be linked to the group
        self.assertNotIn(s2, g.student.all())
        # student s3 should not be linked to the group
        self.assertNotIn(s3, g.student.all())


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
        lector = mixer.blend('edziennik.Lector')
        group1 = mixer.blend('edziennik.Group', lector=lector)
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
        self.assertEqual(len(students), 2)


class TestAttendance_CheckView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        User.objects.create_user(
            username='john', email='lennon@thebeatles.com', password='johnpassword', is_staff=True)
        User.objects.create_user(
            username='ben', email='ben@thebeatles.com', password='benpassword', is_staff=True)
    def test_attendance_check_view_for_non_staff(self):
        """
        non staff user should not have access - status code 404
        """
        client = Client()
        group = mixer.blend('edziennik.Group')
        response = self.client.get(
            reverse('edziennik:attendance_check', args=(group.id,)))
        self.assertEqual(response.status_code, 404)

    def test_attendance_check_view_for_staff_lector_checks(self):
        """
        staff user should have access - status code 200,
        there are two lectors,
        group lector checks attendance, he should get an hour
        """
        data = {
            'student': [1, 2],
            'class_subject': 'test_subject',
            'homework' : [1,]
        }
        client = Client()
        lector1 = Lector.objects.create(user=User.objects.get(username='john'))
        lector2 = Lector.objects.create(user=User.objects.get(username='ben'))
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1, student2, student3)
        logged_in = self.client.login(
            username='john', password='johnpassword')
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

    def test_attendance_check_view_for_staff_substitution(self):
        """
        staff user should have access - status code 200
        there are two lectors,
        other lector checks attendance (substitution)
        lector who checks should get an hour
        """
        data = {
            'student': [1, 2],
            'class_subject': 'test_subject',
            'homework' : [1,]
        }
        client = Client()
        lector1 = Lector.objects.create(user=User.objects.get(username='john'))
        lector2 = Lector.objects.create(user=User.objects.get(username='ben'))
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1, student2, student3)

        logged_in = self.client.login(
            username='ben', password='benpassword')
        self.assertTrue(logged_in)

        url = reverse('edziennik:attendance_check', args=(group1.id,))
        expected_url = reverse('edziennik:group', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # one ClassDate object should be created
        assert ClassDate.objects.all().count() == 1

        # lector1 sould have no hour
        assert lector1.classdate_set.all().count() == 0

        # lector2 should get one hour
        assert lector2.classdate_set.all().count() == 1

        # two of the three students should have attendance
        class_date = ClassDate.objects.first()
        assert class_date.student.all().count() == 2

        # one of the three students should have homework
        assert class_date.has_homework.all().count() == 1


    def test_attendance_check_view_for_staff_admin_checks(self):
        """
        staff user should have access - status code 200,
        group.lector should get an hour when admin checks
        """
        data = {
            'student': [1, 2],
            'class_subject': 'test_subject',
            'homework' : [1,]
        }
        client = Client()
        lector1 = Lector.objects.create(user=User.objects.get(username='john'))
        lector2 = Lector.objects.create(user=User.objects.get(username='ben'))
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


    def test_attendance_check_view_for_staff_no_students(self):
        """
        staff user should have access - status code 200
        there are no students present,
        ClassDate should be created,
        lector1 should get 1 hour
        """
        data = {
            'student': [],
            'class_subject': 'test_subject',
            'homework': []
        }
        client = Client()
        lector1 = Lector.objects.create(user=User.objects.get(username='john'))
        lector2 = Lector.objects.create(user=User.objects.get(username='ben'))
        student1 = mixer.blend('edziennik.Student')
        student2 = mixer.blend('edziennik.Student')
        student3 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1, student2, student3)
        logged_in = self.client.login(
            username='john', password='johnpassword')
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

        # no students should have attendance
        class_date = ClassDate.objects.first()
        assert class_date.student.all().count() == 0


    def test_attendance_check_view_for_staff_error_msg(self):
        """
        staff user should have access - status code 200
        should not allow to check attendance twice in the same day in same group,
        without special 'additional_hour' input
        """
        data = {
            'student': [1,],
            'class_subject': 'test_subject',
            'homework': [1,],
            # 'additional_hour': None
        }
        client = Client()
        lector1 = Lector.objects.create(user=User.objects.get(username='john'))
        student1 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1)
        mixer.blend('edziennik.ClassDate', date_of_class=today, group=group1)
        logged_in = self.client.login(
            username='john', password='johnpassword')
        url = reverse('edziennik:attendance_check', args=(group1.id,))
        expected_url = reverse('edziennik:group_check', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # no ClassDate object should be created, one preexisting
        assert ClassDate.objects.all().count() == 1

        # lector1 sould get no hours
        assert lector1.classdate_set.all().count() == 0

        # should display message about preexisting classdate
        msg = response.context['error_message']
        expectd_msg = """BYLA JUZ DZIS SPRAWDZANA OBECNOSC W TEJ GRUPIE. Jeśli chcesz jeszcze raz zaznaczyć obecność kliknij i zaznacz 'dodatkowa godzina'"""
        self.assertEqual(msg, expectd_msg)


    def test_attendance_check_view_for_staff_twice_same_day(self):
        """
        staff user should have access - status code 200
        should allow to check attendance twice in the same day in same group,
        with special 'additional_hour' input
        lector should get additional hour
        """
        data = {
            'student': [1,],
            'class_subject': 'test_subject',
            'homework': [1,],
            'additional_hour': 'on'
        }
        client = Client()
        lector1 = Lector.objects.create(user=User.objects.get(username='john'))
        student1 = mixer.blend('edziennik.Student')
        group1 = mixer.blend('edziennik.Group', lector=lector1)
        group1.student.add(student1)
        cd = mixer.blend('edziennik.ClassDate',
            date_of_class=today,
            group=group1,
            lector=lector1)
        cd.student.add(student1)
        logged_in = self.client.login(
            username='john', password='johnpassword')
        url = reverse('edziennik:attendance_check', args=(group1.id,))
        expected_url = reverse('edziennik:group', args=(group1.id,))

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # two ClassDate objects should be present
        assert ClassDate.objects.all().count() == 2

        # lector1 sould have two hours
        assert lector1.classdate_set.all().count() == 2

        # student 1 should have attendance in 2 lessons
        self.assertEqual(ClassDate.objects.filter(student=student1).count(), 2)


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
        lector = mixer.blend('edziennik.Lector')
        group1 = mixer.blend('edziennik.Group', lector=lector)
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
        lector = mixer.blend('edziennik.Lector')
        group1 = mixer.blend('edziennik.Group', lector=lector)
        group2 = mixer.blend('edziennik.Group', lector=lector)
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



class Test_Initial_Import_Create(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        self.test_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_dir

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_anonymous(self):
        '''should redirect to login'''
        url = reverse('edziennik:initial_import_create')
        expected_url = reverse('auth_login') + '?next=/initial_import_create/'
        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200)

    def test_upload_students(self):
        '''1 student, no preexisting'''
        test_file = os.getcwd() + '/edziennik/tests/test_files/test_1student.xlsx'
        f = open(test_file, 'rb')
        file = File(f)

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:initial_import_create')
        expected_url = reverse(
            'edziennik:initial_import_detail', args=(1,))
        data = {
            'file': file,
        }

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200)
        # should create one instance of Initial_Import class
        self.assertEqual(Initial_Import.objects.all().count(), 1)


def make_initial_import_obj(file_name):
    '''file_name - .xlsx file, creates Initial_Import instance'''
    path = os.getcwd() + '/edziennik/tests/test_files/' + file_name
    with open(path, 'rb') as f:
        fF = InMemoryUploadedFile(io.BytesIO(f.read()), 'fileobj',
                                  'name.xlsx', 'application/xlsx',
                                  os.path.getsize(path), None)
        return Initial_Import.objects.create(file=fF)


class Test_Initial_Import_UsageCreate(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')
        self.test_dir = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_dir

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def test_anonymous(self):
        '''should redirect to login'''
        url = reverse('edziennik:initial_import_detail', args=(1,))
        expected_url = reverse('auth_login') + \
            '?next=/1/initial_import_detail/'
        response = self.client.post(url, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200)

    def test_import_1_s(self):
        '''1 student, no preexisting'''
        make_initial_import_obj('test_1student.xlsx')

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:initial_import_detail', args=(1,))
        expected_url = reverse(
            'edziennik:initial_import_usage_detail', args=(1,))
        data = {
            'initial_import_file': '1',
        }

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200)
        # should create one instance of Initial_Import_Usage class
        self.assertEqual(Initial_Import_Usage.objects.all().count(), 1)
        # should create 1 Student
        self.assertEqual(Student.objects.all().count(), 1)
        # should create 1 Parent
        self.assertEqual(Parent.objects.all().count(), 1)
        # should create 1 Group
        self.assertEqual(Group.objects.all().count(), 1)
        # should display success message
        # msg = response.context['success_message']
        msg = list(response.context['messages'])[0].message
        expectd_msg = 'Import zakończony pomyślnie'
        self.assertEqual(msg, expectd_msg)

    def test_import_2_s_error(self):
        '''2 students in file, error'''
        make_initial_import_obj('test_2students_1e_invalid_email.xlsx')

        self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:initial_import_detail', args=(1,))
        expected_url = reverse(
            'edziennik:initial_import_usage_detail', args=(1,))
        data = {
            'initial_import_file': '1',
        }

        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200
        self.assertRedirects(response, expected_url,
                             status_code=302, target_status_code=200)
        # should create one instance of Initial_Import_Usage class
        self.assertEqual(Initial_Import_Usage.objects.all().count(), 1)
        # should create 1 Initial_Import_Usage_Error
        self.assertEqual(Initial_Import_Usage_Errors.objects.all().count(), 1)
        # should not create a Student
        self.assertEqual(Student.objects.all().count(), 0)
        # should not create a Parent
        self.assertEqual(Parent.objects.all().count(), 0)
        # should not create a Group
        self.assertEqual(Group.objects.all().count(), 0)
        # should display success message
        # msg = response.context['success_message']
        msg = list(response.context['messages'])[0].message
        expectd_msg = 'WYSTĄPIŁY BŁĘDY - DANE NIE ZOSTAŁY ZAIMPORTOWANE'
        self.assertEqual(msg, expectd_msg)
