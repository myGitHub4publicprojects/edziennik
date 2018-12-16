# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings

class Lector(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    def __str__(self):              
        return self.user.username

class Group(models.Model):
    name = models.CharField(max_length=200)
    lector = models.ForeignKey(Lector, on_delete=models.CASCADE)

    def __str__(self):              
        return self.name

class Parent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    phone_number = models.IntegerField()

    def __str__(self):              
        return self.user.username

class Student(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    quizlet = models.BooleanField(default=False) # give student reward for activity on quizlet
    # quizlet_username = models.CharField(max_length=30, blank=True)

    def __str__(self):              
        return self.name.encode("utf-8")

class ClassDate(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_class = models.DateField()
    subject = models.CharField(max_length=200, default = 'testowy temat')
    student = models.ManyToManyField(Student, related_name="student")
    has_homework = models.ManyToManyField(Student, related_name="has_homework")
    lector = models.ForeignKey(Lector, default=1, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.date_of_class)

class Grades(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_test = models.DateField(null=True, blank=True)
    name = models.CharField(max_length = 200) # what is the grade for
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.name)

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
    delivered = models.BooleanField(default=False)
    checked_once = models.BooleanField(default=False)
    checked_twice = models.BooleanField(default=False)
    twilio_message_sid = models.CharField(max_length=120, null=True, blank=True)
    twilio_message_status = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_message_id = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_status = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_error_code = models.CharField(max_length=120, null=True, blank=True)
    smsapipl_error_message = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.service + self.addressee.username + str(self.timestamp)

# class AdminNote(models.Model):
#     timestamp = models.DateTimeField(auto_now_add=True)
#     published = models.DateField(auto_now=False, auto_now_add=False)
#     body = models.TextField(max_length=1600)
#     student = models.ManyToManyField(Student)
#     group = models.ManyToManyField(Group)
