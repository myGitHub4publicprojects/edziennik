# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib import auth
from mixer.backend.django import mixer
import pytest
from datetime import datetime, timedelta
from django.contrib.staticfiles.templatetags.staticfiles import static
from edziennik.models import Lector, Group, Parent, Student, ClassDate
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
        should redirect to student view
        """
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        parent = mixer.blend('edziennik.Parent', user=user_john)
        student = mixer.blend('edziennik.Student', parent=parent)
        logged_in = self.client.login(username='john', password='glassonion')
        
        response = self.client.get(reverse('edziennik:name_home'))
    
        self.assertTrue(logged_in)
        expected_url = reverse('edziennik:student', args=(student.id,))
        self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

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
    def test_lector_view_for_not_admin(self):
        """
        non admin user should not have access - status code 404
        """
        client = Client()
        user_john = User.objects.create_user(username='john',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        lector = Lector.objects.create(user=user_john)
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
        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        response = self.client.get(reverse('edziennik:lector', args=(lector.id,)))
        self.assertTrue(logged_in)

        self.assertEqual(response.status_code, 200)
        response_lector_groups= list(response.context['lectors_groups'])
        self.assertEqual(len(response_lector_groups), 2)


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
        student = mixer.blend('edziennik.Student', name='little_john', parent=parent)
        logged_in = self.client.login(username='john', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))
        self.assertContains(response, 'little_john', status_code=200)

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
        grade1 = mixer.blend('edziennik.Grades', student=student, date_of_test=today)
        grade2 = mixer.blend('edziennik.Grades', student=student, date_of_test=today)
        grade3 = mixer.blend('edziennik.Grades', student=student2, date_of_test=today)

        date_of_class = ClassDate.objects.create(date_of_class=today)
        date_of_class.student.add(student, student2)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))
        response_grade_list= list(response.context['grade_list'])
        # student has grade1 and grade2
        self.assertEqual(len(response_grade_list), 2)

        response_attendance_table_content= list(response.context['attendance_table_content'])
        # attendance was checked only once, today
        self.assertEqual(len(response_attendance_table_content), 1)

    def test_student_view_has_homework_admin(self):
        """
        should display '+' in attendance table
        """
        client = Client()

        student = mixer.blend('edziennik.Student')
        date_of_class = ClassDate.objects.create(date_of_class=today)
        date_of_class.student.add(student)
        date_of_class.has_homework.add(student)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))

        response_attendance_table_content= list(response.context['attendance_table_content'])
        present_sign = '<img src=%s>' % static('img/check_sign_icon_green.png')
        self.assertEqual(response_attendance_table_content[0][2], present_sign)

    def test_student_view_absent_admin(self):
        """
        should display '-' in attendance table
        """
        client = Client()
        group=mixer.blend('edziennik.Group')
        student = mixer.blend('edziennik.Student', group=group)
        student2 = mixer.blend('edziennik.Student', group=group)
        date_of_class = ClassDate.objects.create(date_of_class=today-timedelta(1))
        date_of_class.student.add(student2)

        user_admin = User.objects.create_superuser(username='admin',
                                 email='jlennon@beatles.com',
                                 password='glassonion')
        logged_in = self.client.login(username='admin', password='glassonion')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('edziennik:student', args=(student.id,)))

        response_attendance_table_content= list(response.context['attendance_table_content'])
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
        group1 = mixer.blend('edziennik.Group')
        group2 = mixer.blend('edziennik.Group')
        student1 = mixer.blend('edziennik.Student', group=group1)
        student2 = mixer.blend('edziennik.Student', group=group1)
        student3 = mixer.blend('edziennik.Student', group=group2)

        grade1 = mixer.blend('edziennik.Grades', student=student1, date_of_test=today)
        grade2 = mixer.blend('edziennik.Grades', student=student2, date_of_test=today)
        grade3 = mixer.blend('edziennik.Grades', student=student3, date_of_test=today)
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


class TestAttendance_CheckView(TestCase):
    def setUp(self):
        User.objects.create_superuser(
            username='admin', email='jlennon@beatles.com', password='glassonion')

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
        group1 = mixer.blend('edziennik.Group', lector = lector1)
        student1 = mixer.blend('edziennik.Student', group=group1)
        student2 = mixer.blend('edziennik.Student', group=group1)
        student3 = mixer.blend('edziennik.Student', group=group1)
        logged_in = self.client.login(username='admin', password='glassonion')
        url = reverse('edziennik:attendance_check', args=(group1.id,))

        expected_url = reverse('edziennik:group', args=(group1.id,))
        response = self.client.post(url, data, follow=True)
        # should give code 200 as follow is set to True
        assert response.status_code == 200

        # one ClassDate object should be created
        assert len(ClassDate.objects.all()) == 1

        # only lector1 sould have one hour
        assert len(lector1.classdate_set.all()) == 1

        # lector2 should have no hours
        assert len(lector2.classdate_set.all()) == 0

        # two of the three students should have attendance
        class_date = ClassDate.objects.first()
        assert len(class_date.student.all()) == 2

        # one of the three students should have homework
        assert len(class_date.has_homework.all()) == 1



    # def test_logged_in(self):
    #     self.client.login(username='john', password='glassonion')
    #     data = {'fname': 'Adam',
    #             'lname': 'Atkins',
    #             'bday': '2000-01-01',
    #             'usrtel': 1,
    #             'location': 'some_location',
    #             'left_ha': 'model1_family1_brand1',
    #             'right_ha': 'model2_family2_brand2',
    #             'left_purchase_date': '1999-01-01',
    #             'right_purchase_date': '1999-01-02',
    #             'left_NFZ_new': '2001-01-01',
    #             'right_NFZ_new': '2001-01-01',
    #             'left_NFZ_confirmed_date': '2001-01-01',
    #             'right_NFZ_confirmed_date': '2002-02-02',
    #             'left_pcpr_ha': 'model3_f3_b3',
    #             'right_pcpr_ha': 'b4_f4_m4',
    #             'left_PCPR_date': '2003-01-01',
    #             'right_PCPR_date': '2004-01-01',
    #             'note': 'p1_note',
    #             }
    #     url = reverse('crm:store')
    #     # id of new patient should be 1
    #     expected_url = reverse('crm:edit', args=(1,))
    #     response = self.client.post(url, data, follow=True)
    #     # should give code 200 as follow is set to True
    #     assert response.status_code == 200
    #     self.assertRedirects(response, expected_url,
    #                          status_code=302, target_status_code=200)
    #     self.assertEqual(len(Patient.objects.all()), 1)
    #     self.assertEqual(len(NFZ_New.objects.all()), 2)
    #     self.assertEqual(len(NFZ_Confirmed.objects.all()), 2)
    #     self.assertEqual(len(PCPR_Estimate.objects.all()), 2)
    #     self.assertEqual(len(Hearing_Aid.objects.all()), 2)
    #     self.assertEqual(len(Reminder.objects.all()), 6)
