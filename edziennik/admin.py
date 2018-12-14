from django.contrib import admin

from edziennik.models import Lector, Group, Student, ClassDate, Grades, Parent, SMS

admin.site.register(Lector)
admin.site.register(Group)
admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(ClassDate)
admin.site.register(Grades)
admin.site.register(SMS)