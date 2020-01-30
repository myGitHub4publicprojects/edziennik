# -*- coding: utf-8 -*-
import os

from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator

from .validators import xlsx_only


class Initial_Import(models.Model):
	'''xlsx file containing students, parents and group data to populate db'''
	file = models.FileField(upload_to='initial_import_files/', validators=[xlsx_only])
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def filename(self):
		return os.path.basename(self.file.name)

	def get_absolute_url(self):
		return reverse('edziennik:initial_import_detail', kwargs={'pk': self.pk})

	def __unicode__(self):
		return self.filename() + ' ' + str(self.uploaded_at)


class Initial_Import_Usage(models.Model):
    '''when was the uploaded file used what was produced'''
    initial_import = models.ForeignKey(
        Initial_Import, on_delete=models.CASCADE)
    used = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('edziennik:initial_import_usage_detail', kwargs={'pk': self.pk})


class Initial_Import_Usage_Errors(models.Model):
    initial_import_usage = models.ForeignKey(
    	Initial_Import_Usage, on_delete=models.CASCADE)
    error_log = models.TextField()
    row_number = models.IntegerField()
    line = models.TextField()

class Lector(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):              
        return self.user.username


class Parent(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    # phone_number - 9 digits, no spaces, no other characters
    phone_number = models.IntegerField(
        unique=True,
    	validators=[MinValueValidator(100000000),MaxValueValidator(999999999)],
        verbose_name='Nr telefonu')
    email = models.EmailField(unique=True)
    # address
    street = models.CharField(max_length=120, null=True, blank=True)
    house_number = models.CharField(max_length=6, null=True, blank=True)
    apartment_number = models.CharField(max_length=6, null=True, blank=True)
    city = models.CharField(max_length=120, null=True, blank=True)
    zip_code = models.CharField(max_length=6, null=True, blank=True)
    iiu = models.ForeignKey(
        Initial_Import_Usage, on_delete=models.CASCADE, blank=True, null=True)
    initial_password = models.CharField(max_length=120)

    def get_absolute_url(self):
        return reverse('edziennik:parent_datail', kwargs={'pk': self.pk})

    def __str__(self):              
        return ' '.join([self.user.last_name,
                        self.user.first_name,
                        self.user.username,
                        str(self.phone_number)])

class Student(models.Model):
    first_name = models.CharField(
    	max_length=100, verbose_name='Imię ucznia')
    last_name = models.CharField(
        max_length=100, verbose_name='Nazwisko ucznia')
    date_of_birth = models.DateField(
        verbose_name='Data urodzenia', null=True, blank=True)
    school = models.CharField(max_length=100, null=True, blank=True)
    class_in_school = models.CharField(max_length=100, null=True, blank=True)
    language_of_interest = models.CharField(max_length=100, default='English')
    language_at_school = models.BooleanField(null=True, blank=True)
    experience = models.CharField(max_length=200, null=True, blank=True)
    book = models.CharField(max_length=200, null=True, blank=True)
    avaliability = models.CharField(max_length=400, null=True, blank=True)
    other_classes = models.CharField(max_length=200, null=True, blank=True)
    focus = models.CharField(max_length=200, null=True, blank=True)
    recruitment_note = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
    	Parent, on_delete=models.CASCADE, verbose_name='Rodzic')
    GENDER_CHOICES = (
        ('M', 'męska'),
        ('F', 'żeńska'),
        )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, verbose_name='Płeć ucznia')
    # quizlet = models.BooleanField(default=False) # give student reward for activity on quizlet
    quizlet_username = models.CharField(max_length=30, blank=True)
    iiu = models.ForeignKey(
    	Initial_Import_Usage, on_delete=models.CASCADE, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('edziennik:student', kwargs={'pk': self.pk})

    def __str__(self):              
        return self.first_name + ' ' + self.last_name


class Group(models.Model):
    name = models.CharField(max_length=200)
    lector = models.ForeignKey(
    	Lector, on_delete=models.CASCADE, blank=True, null=True)
    student = models.ManyToManyField(Student, related_name="group_student", blank=True)
    quizlet_group_url = models.URLField(blank=True)
    iiu = models.ForeignKey(
    	Initial_Import_Usage, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name


class ClassDate(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_class = models.DateField()
    subject = models.CharField(max_length=200, default = 'testowy temat')
    student = models.ManyToManyField(Student, related_name="student")
    has_homework = models.ManyToManyField(Student, related_name="has_homework")
    lector = models.ForeignKey(Lector, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.date_of_class)


class Homework(models.Model):
    classdate = models.ForeignKey(ClassDate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=200, verbose_name='Treść zadania')

    def __str__(self):
        return str(self.message)


class Grades(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_test = models.DateField(null=True, blank=True)
    name = models.CharField(max_length = 200) # what is the grade for
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

class Quizlet(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class SMS(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    SERVICE_CHOICES = (
        ('smsapipl', 'smsapipl'),
        ('twilio', 'twilio'),
        )
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    message = models.TextField(max_length=1600)
    addressee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    delivered = models.BooleanField()
    checked_once = models.BooleanField()
    checked_twice = models.BooleanField()
    twilio_message_sid = models.CharField(max_length=120, null=True, blank=True)
    twilio_message_status = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_message_id = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_status = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_error_code = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_error_message = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.service + self.addressee.username + str(self.timestamp)


class Admin_Profile(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quizlet_username = models.CharField(max_length=30, blank=True)
    quizlet_password = models.CharField(max_length=30, blank=True)
    check_quizlet_automatically = models.BooleanField(default=False)
    twilio_account_sid = models.CharField(max_length=40, blank=True)
    twilio_auth_token = models.CharField(max_length=40, blank=True)
    twilio_messaging_service_sid = models.CharField(max_length=40, blank=True)
    sms_when_absent = models.BooleanField(default=False)
    sms_when_no_homework = models.BooleanField(default=False)
    sms_message_absence = models.CharField(max_length=300, blank=True)
    sms_message_no_homework = models.CharField(max_length=400, blank=True)
    school_admin_email = models.EmailField(
        max_length=70, null=True, blank=True)
    send_email_weekly_attendance_report = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


def student_added_to_group(sender, ** kwargs):
    if kwargs['action'] == 'post_add':
        group = kwargs['instance']
        students_ids = kwargs['pk_set']
        students = Student.objects.filter(id__in=students_ids)
        for s in students:
            # prevent duplicates
            if not Quizlet.objects.filter(group=group, student=s).exists():
                # create quizlet object
                Quizlet.objects.create(group=group,student=s)

m2m_changed.connect(student_added_to_group, sender=Group.student.through)


def add_email_to_user(sender, instance, **kwargs):
    user = instance.user
    user.email = instance.email
    user.save()

post_save.connect(add_email_to_user, sender=Parent)
