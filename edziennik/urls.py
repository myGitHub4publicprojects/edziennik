from django.conf.urls import patterns, url

from edziennik import views

app_name = 'edziennik'
urlpatterns = [
    url(r'^$', views.index, name='name_home'),
    url(r'^sprawdz$', views.select_group, name='name_sprawdz'),
    url(r'^select_group_for_grades$', views.select_group_for_grades, name='select_group_for_grades'),
    url(r'^attendance$', views.attendance, name='name_attendance'),
    url(r'^(?P<group_id>\d+)/group_check$', views.group_check, name='name_group_check'),
    url(r'^(?P<group_id>\d+)/group_grades$', views.group_grades, name='group_grades'),
    url(r'^(?P<groupp_id>\d+)/attendance_check$', views.attendance_check, name='name_attendance_check'),
    url(r'^(?P<groupp_id>\d+)/add_grades$', views.add_grades, name='add_grades'),
    url(r'^(?P<group_id>\d+)/attendance_by_group$', views.attendance_by_group, name='name_attendance_by_group'),
    url(r'^(?P<question_id>\d+)/lektor$', views.lektor, name='name_lektor'),
    url(r'^(?P<question_id>\d+)/student/$', views.student, name='name_student'),
    url(r'^(?P<question_id>\d+)/group/$', views.group, name='name_group'),
]
