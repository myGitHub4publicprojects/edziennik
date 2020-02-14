from django.contrib import admin

from edziennik.models import (Lector, Group, Student, ClassDate, Grades, Parent,
                              SMS, Quizlet, Homework, Initial_Import, Initial_Import_Usage,
                              Initial_Import_Usage_Errors)

admin.site.register(Lector)
admin.site.register(Group)
admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(ClassDate)
admin.site.register(Grades)
admin.site.register(SMS)
admin.site.register(Quizlet)
admin.site.register(Homework)
admin.site.register(Initial_Import)
admin.site.register(Initial_Import_Usage)
admin.site.register(Initial_Import_Usage_Errors)
