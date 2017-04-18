from django.db import models
from django.conf import settings

class Lector(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):              
        return self.user.username

class Group(models.Model):
    name = models.CharField(max_length=200)
    lector = models.ForeignKey(Lector)

    def __str__(self):              
        return self.name

class Parent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    phone_number = models.IntegerField()

    def __str__(self):              
        return self.user.username

class Student(models.Model):
    name = models.CharField(max_length=200)
    group = models.ForeignKey(Group)
    parent = models.ForeignKey(Parent)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

    def __str__(self):              
        return self.name

class ClassDate(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_class = models.DateField()
    subject = models.CharField(max_length=200, default = 'testowy temat')
    student = models.ManyToManyField(Student)
    
    def __str__(self):
        return str(self.date_of_class)

class Grades(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_test = models.DateField(null=True, blank=True)
    name = models.CharField(max_length = 200) # what is the grade for
    student = models.ForeignKey(Student)
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
    addressee = models.ForeignKey(settings.AUTH_USER_MODEL)
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
