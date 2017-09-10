from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from edziennik.models import Lector, Group, Parent, Student, ClassDate, Grades
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static

from edziennik.utils import student_absence


def index(request):
    '''displays either a login prompt or a button to check attendance, for logged in users'''
    if not request.user.is_authenticated():
        return render(request, 'edziennik/home_for_others.html')

    group_list = Group.objects.all()
    lectors = Lector.objects.all()
    if request.user.is_superuser:
        context = {
            'group_list': group_list,
            'lectors': lectors,
        }
        return render(request, 'edziennik/home_for_admin.html', context)
    if request.user in [lector.user for lector in lectors]:
        return render(request, 'edziennik/home_for_lector.html', {'group_list': group_list})
    else:
        raise Http404

def lector(request, pk):
    '''displays lectors name and his groups'''
    if not request.user.is_superuser:
        raise Http404
    lector = get_object_or_404(Lector, pk=pk)
    lectors_groups = lector.group_set.all()
    return render(request, 'edziennik/lector.html', {'lector': lector, 'lectors_groups': lectors_groups})

def student(request, pk):
    '''displays info about a given student'''
    student = get_object_or_404(Student, pk = pk)
    lector = student.group.lector
    group = student.group
    grades = Grades.objects.filter(student=student)
    grade_list = [(g.date_of_test.strftime("%d/%m/%Y"), g.name, g.score) for g in grades]
    
    students = Student.objects.filter(group=group) # all students in this group
    all_classes = ClassDate.objects.filter(student__in=students).distinct().order_by('date_of_class') #all clases in this group
    # check students attendance and build an array
    attendence_table_header = ['data', 'obecnosc']
    attendance_table_content = []
    for date in all_classes:
        if student.student.filter(date_of_class=date.date_of_class):
            attendance_table_content.append((date.date_of_class.strftime("%d/%m/%Y"), '+'))
        else:
            attendance_table_content.append((date.date_of_class.strftime("%d/%m/%Y"), '-'))

    context = {
        'student': student,
        'lector': lector,
        'group': group,
        'grade_list': grade_list,
        'attendence_table_header': attendence_table_header,
        'attendance_table_content': attendance_table_content,
        }
    return render(request, 'edziennik/student.html', context)

def group(request, pk):
    ''' displays a list of students and their scores for each grade '''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    lector = group.lector
    students = Student.objects.filter(group=group)
    grades_in_this_group = Grades.objects.filter(student__in=students)

    dates_grades = []
    for grade in grades_in_this_group:
        if (grade.date_of_test, grade.name) not in dates_grades:
            dates_grades.append((grade.date_of_test, grade.name))

    table_header = ['data', 'za co'] + list(students)
    table_content = []
    for grade in dates_grades:
        grade_date_name_score = [grade[0].strftime("%d/%m/%Y"), grade[1]]
        for student in students:
            item = grades_in_this_group.filter(student=student, date_of_test=grade[0], name=grade[1]).first()
            if item:
                grade_date_name_score.append(item.score)
            else:
                grade_date_name_score.append('-')
        table_content.append(grade_date_name_score)

    context = {
        'group': group,
        'lector': lector,
        'table_header': table_header,
        'table_content': table_content,
    }
    return render(request, 'edziennik/group.html', context)

def select_group_for_attendance(request):
    '''select group to check attendance, only groups assigned to a given teacher are returned'''
    if not request.user.is_staff:
        raise Http404
    lector = Lector.objects.get(user=request.user)
    groups = Group.objects.filter(lector=lector)

    return render(request, 'edziennik/select_group_for_attendance.html', {'groups': groups})

def group_check(request, pk):
    ''' displays a group where attendance is checked'''
    if not request.user.is_authenticated():
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    students = Student.objects.filter(group=group)
    context = {
        'group': group,
        'students': students,
    }
    return render(request, 'edziennik/group_check.html', context)

def attendance_check(request, pk):
    ''' handles checked attendance of a group
    and generates error message if attendance was checked earlier that day'''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)

    # checks if attendance was checked today in this group, if yes, error
    for i in ClassDate.objects.filter(student__in=group.student_set.all()):
        if i.date_of_class == datetime.date.today():
            context = {
            'error_message': "BYLA JUZ DZIS SPRAWDZANA OBECNOSC W TEJ GRUPIE",
            'group': group,
            }
            return render(request, 'edziennik/group_check.html', context)
   
    # process attendance of each student
    selected_student_list = request.POST.getlist('student') # wazne - getlist!!! - bierze liste wynikow a nie pojedynczy
    class_subject = request.POST.get('class_subject')
    class_date = ClassDate.objects.create(  date_of_class=datetime.datetime.today(),
                                            subject = class_subject)
    have_homework = request.POST.getlist('homework')
    for id in selected_student_list:
        class_date.student.add(Student.objects.get(id=id))
        if id in have_homework:
            class_date.has_homework.add(Student.objects.get(id=id))
        # else:
        #     student_without_homework = Student.objects.get(id=id)
        #     student_without_homework.no_homework += 1
        #     if student_without_homework.no_homework > 1:
        #         email admin
        #         student_without_homework.no_homework = 0
        
    # notify parents of absence
    absentees = group.student_set.exclude(id__in=selected_student_list)
    for student in absentees:
        student_absence(student)

    print(selected_student_list)
    print(have_homework)
    messages.success(request, "Obecnosc w grupie %s sprawdzona" % group.name)
    return redirect('edziennik:name_home')

def attendance_by_group(request, group_id):
    ''' displays attendance results in a given group'''
    if not request.user.is_staff:
        raise Http404

    group = get_object_or_404(Group, pk=group_id)
    students = group.student_set.all()
    table_header = ['data', 'temat'] + list(students)
    table_content = []
    classes_in_group = ClassDate.objects.filter(student__in=students).distinct().order_by('date_of_class')
    for i in classes_in_group:
        row = [i.date_of_class.strftime("%d/%m/%Y"), i.subject]
        for s in students:
            if s in i.student.all():
                img_url = static('img/check_sign_icon_green.png')
            else:
                img_url = static('img/x-mark-red.png')
            row.append('<img src=%s>' % img_url)
        table_content.append(row)

    context = {
        'group': group,
        'table_header': table_header,
        'table_content': table_content,
        }
    return render(request, 'edziennik/attendance_by_group.html', context)

def select_group_for_grades(request):
    '''select group to add grades, only groups assigned to a given teacher are returned'''
    if not request.user.is_staff:
        raise Http404
    lector = Lector.objects.get(user=request.user)
    groups = Group.objects.filter(lector=lector)

    return render(request, 'edziennik/select_group_grades.html', {'groups': groups})

def group_grades(request, group_id):
    ''' displays a list of students in a given group,
    lector can input name of test and grades for each student'''
    if not request.user.is_staff:
        raise Http404

    group = get_object_or_404(Group, pk=group_id)
    students = Student.objects.filter(group=group)
    context = {
        'group': group,
        'students': students,
        }
    return render(request, 'edziennik/group_grades.html', context)

def add_grades(request, pk):
    ''' handles grades for each student in the group'''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    students = Student.objects.filter(group=group)
    date_of_test = request.POST.get('date_of_test') or datetime.datetime.today()
    grade_name = request.POST.get('grade_name')
    for student in students:
        if request.POST.get(student.name):
            todays_grades = Grades.objects.filter(student=student)
            # make sure grade with this name is not already added
            if todays_grades.filter(name=grade_name, date_of_test=date_of_test):
                messages.error(request, "Ocena za %s  w dniu %s byla juz dodana uczniowi %s. Sprobuj jeszcze raz" % (grade_name, date_of_test, student.name))
                return redirect('edziennik:group_grades', group_id=pk)
            # add grade
            instance = Grades.objects.create(
                name=grade_name,
                date_of_test=date_of_test,
                student = student,
                score = request.POST.get(student.name)
                )

    messages.success(request, "Oceny w grupie %s dodane" % group.name)
    return redirect('edziennik:name_home')