from django.contrib import admin

from edziennik.models import Lektor, Group, Student, ClassDate, Grades

admin.site.register(Lektor)
admin.site.register(Group)
admin.site.register(Student)
admin.site.register(ClassDate)
admin.site.register(Grades)
