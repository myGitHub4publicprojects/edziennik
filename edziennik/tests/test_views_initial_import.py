# -*- coding: utf-8 -*-
import io
import os
import shutil
import tempfile

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
import pytest
from datetime import date, datetime, timedelta
from django.templatetags.static import static
from freezegun import freeze_time
from edziennik.models import (Lector, Group, Parent, Student, ClassDate, Grades,
                              Admin_Profile, Quizlet, Initial_Import, Initial_Import_Usage,
                              Initial_Import_Usage_Errors)
pytestmark = pytest.mark.django_db
today = datetime.today().date()

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
