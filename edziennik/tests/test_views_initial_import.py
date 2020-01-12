# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

from django.conf import settings
from django.core.files import File
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
                              Admin_Profile, Quizlet, Initial_Import)
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
