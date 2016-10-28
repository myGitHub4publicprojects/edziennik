from django.db import models

class Lektor(models.Model):
    lektor_name = models.CharField(max_length=200)


    def __str__(self):              
        return self.lektor_name

class Group(models.Model):
    group_name = models.CharField(max_length=200)
    prowadzacy_lektor = models.ForeignKey(Lektor)
    def __str__(self):              
        return self.group_name

class Student(models.Model):
    student_name = models.CharField(max_length=200)
    przynaleznosc_grupy = models.ForeignKey(Group)

    def __str__(self):              
        return self.student_name

class ClassDate(models.Model):
    date_of_class = models.DateTimeField()
    subject = models.CharField(max_length=200, default = 'testowy temat')
    student = models.ForeignKey(Student)
    
    def __str__(self):
        return str(self.date_of_class)
# ClassDate.objects.get(id=1).date_of_class.strftime("%d/%m/%Y")

class Grades(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    date_of_test = models.DateField(null=True, blank=True)
    name = models.CharField(max_length = 200) # what is the grade for
    student = models.ForeignKey(Student)
    score = models.PositiveSmallIntegerField()
    def __str__(self):
        return str(self.name)