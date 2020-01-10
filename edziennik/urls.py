from django.urls import path
from django.contrib.auth.decorators import login_required

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
    path('student_list/',
         login_required(views.StudentList.as_view()), name='student_list'),
    path('<int:pk>/parent_datail/',
         login_required(views.ParentDetailView.as_view()), name='parent_datail'),
    path('<int:pk>/group/', views.group, name='group'),
    path('<int:pk>/add_quizlet/', views.add_quizlet, name='add_quizlet'),
    path('<int:pk>/process_quizlet/',
         views.process_quizlet, name='process_quizlet'),
    path('<int:pk>/show_group_grades/',
         views.show_group_grades, name='show_group_grades'),
    path('advanced_settings/',
         views.advanced_settings, name='advanced_settings'),
    path('quizlet_test_email/',
         views.quizlet_test_email, name='quizlet_test_email'),
    path('sms_test/', views.sms_test, name='sms_test'),
    path('message_test/', views.message_test,
         name='message_test'),
    path('signup/', views.signup,
         name='signup'),
    path('duplicate_check/', views.duplicate_check,
         name='duplicate_check'),
    path('<int:pk>/add_homework/', views.add_homework, name='add_homework'),
    path('initial_import_create/',
         views.Initial_Import_Create.as_view(), name='initial_import_create'),
    path('<int:pk>/initial_import_detail/',
         views.Initial_Import_Detail.as_view(), name='initial_import_detail'),
#     path('initial_import_list/', views.Initial_Import_List.as_view(),
#          name='initial_import_list'),

    path('<int:pk>/initial_import_usage_detail/',
         views.Initial_Import_Usage_Detail.as_view(), name='initial_import_usage_detail'),

]
