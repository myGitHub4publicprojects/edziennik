from django.conf.urls import patterns, url

from edziennik import views

app_name = 'edziennik'
urlpatterns = [
    url(r'^$', views.index, name='name_home'),
    url(r'^select_group_for_grades$', views.select_group_for_grades, name='select_group_for_grades'),
    url(r'^(?P<pk>\d+)/group_check$', views.group_check, name='name_group_check'),
    url(r'^(?P<group_id>\d+)/group_grades$', views.group_grades, name='group_grades'),
    url(r'^(?P<pk>\d+)/attendance_check$', views.attendance_check, name='name_attendance_check'),
    url(r'^(?P<pk>\d+)/add_grades$', views.add_grades, name='add_grades'),
    url(r'^(?P<group_id>\d+)/attendance_by_group$', views.attendance_by_group, name='name_attendance_by_group'),
    url(r'^(?P<pk>\d+)/lektor$', views.lector, name='name_lektor'),
    url(r'^(?P<pk>\d+)/student/$', views.student, name='name_student'),
    url(r'^(?P<pk>\d+)/group/$', views.group, name='name_group'),
    url(r'^(?P<pk>\d+)/add_quizlet/$', views.add_quizlet, name='add_quizlet'),
    url(r'^process_quizlet/$', views.process_quizlet, name='process_quizlet'),
    url(r'^(?P<pk>\d+)/show_group_grades$', views.show_group_grades, name='show_group_grades'),

]
