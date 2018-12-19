# from django.conf.urls import patterns, url
from django.urls import path

from edziennik import views

app_name = 'edziennik'

urlpatterns = [
    path('', views.index, name='name_home'),
    path('<int:pk>/group_check/', views.group_check, name='group_check'),
    path('<int:group_id>/group_grades/', views.group_grades, name='group_grades'),
    path('<int:pk>/attendance_check/', views.attendance_check, name='attendance_check'),
    path('<int:pk>/add_grades/', views.add_grades, name='add_grades'),
    path('<int:group_id>/attendance_by_group/',
         views.attendance_by_group, name='attendance_by_group'),
    path('<int:pk>/lektor/', views.lector, name='lector'),
    path('<int:pk>/student/', views.student, name='student'),
    path('<int:pk>/group/', views.group, name='group'),
    path('<int:pk>/add_quizlet/', views.add_quizlet, name='add_quizlet'),
    path('process_quizlet/', views.process_quizlet, name='process_quizlet'),
    path('<int:pk>/show_group_grades/',
         views.show_group_grades, name='show_group_grades'),
    path('advanced_settings/',
         views.advanced_settings, name='advanced_settings'),
]
