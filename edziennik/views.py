from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from edziennik.models import Lektor, Group, Student, ClassDate, Grades
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse

def index(request):
    '''displays either a login prompt or a button to check attendance, for logged in users'''
    username = None
    if request.user.is_authenticated():
        username = request.user.username
    print username
    lektor_list = Lektor.objects.order_by('-lektor_name')[:5]
    group_list = Group.objects.all()
    student_list = Student.objects.all()
    dzisiejsza_data = datetime.datetime.now()
    template = loader.get_template('edziennik/home.html')
    context = RequestContext(request, {
        'username': username,
        'lektor_list': lektor_list,
        'group_list': group_list,
        'student_list': student_list,
        'dzisiejsza_data': dzisiejsza_data
    })
    return HttpResponse(template.render(context))

def lektor(request, question_id):
    if not request.user.is_staff:
        raise Http404
    lek = get_object_or_404(Lektor, pk=question_id)
    groups = Group.objects.all()
    current_group_list = [group for group in groups if lek == group.prowadzacy_lektor]
    return render(request, 'edziennik/lektor.html', {'lek': lek, 'current_group_list': current_group_list})

def student(request, question_id):
    print(request.user.id)
    student = Student.objects.get(id = question_id)
    lektor = student.przynaleznosc_grupy.prowadzacy_lektor
    group = student.przynaleznosc_grupy
    grades = Grades.objects.filter(student=student)
    grade_list = [(g.date_of_test, g.name, g.score) for g in grades]
    context = {'student': student, 'lektor': lektor, 'group': group, 'grade_list': grade_list}
    return render(request, 'edziennik/student.html', context)

def group(request, question_id):
    ''' displays a list of students and their scores for each grade '''
    if not request.user.is_staff:
        raise Http404
    groupp = Group.objects.get(id=question_id)
    lektor = groupp.prowadzacy_lektor
    students_list = [student for student in Student.objects.all() if student.przynaleznosc_grupy == groupp]
    all_dates_and_grades = []

    for student in students_list:
        student_date_and_grade = [(student.id, student.student_name)]
        grades = student.grades_set.all()
        for grade in grades:
            student_date_and_grade.append((grade.date_of_test, grade.name, grade.score)) 
            if (grade.date_of_test, grade.name) not in all_dates_and_grades:
                all_dates_and_grades.append((grade.date_of_test, grade.name))
    main_list2 = [['grades'] + [i[1] for i in all_dates_and_grades]] + [['dates'] + [i[0] for i in all_dates_and_grades]]

    # fill spaces when student has no grade in a day that others got grades
    for student in students_list:
        grades = student.grades_set.all()
        simple_student_grades2 = [(i.date_of_test, i.name) for i in grades]
        student_grades2 = [(i.date_of_test, i.name, i.score) for i in grades]
        for i in all_dates_and_grades:
            if i not in simple_student_grades2:
                position = all_dates_and_grades.index(i)
                student_grades2.insert(position, (i)+(None,))
        only_name_and_scores = [(student.student_name, student.id)]
        for i in student_grades2:
            only_name_and_scores.append(i[2])
        main_list2 += [only_name_and_scores]

    new = zip(*main_list2)

    template = loader.get_template('edziennik/grupa.html')
    context = RequestContext(request, {
        'main_list2': main_list2,
        'new': new,
        'groupp': groupp,
        'lektor': lektor,
        'students_list': students_list,
    })
    return HttpResponse(template.render(context))

def select_group(request):
    '''select group to check attendance, only groups assigned to a given teacher are returned'''
    if not request.user.is_staff:
        raise Http404
    date_today = datetime.datetime.today().strftime("%d/%m/%Y")
    groups = Group.objects.all()
    group_list = [g for g in groups if g.prowadzacy_lektor.lektor_name == request.user.username]
    template = loader.get_template('edziennik/select_group.html')
    context = RequestContext(request, {
        'date_today': date_today,
        'group_list': group_list
    })
    return HttpResponse(template.render(context))

def group_check(request, group_id):
    ''' displays a group where attendance is checked'''
    if not request.user.is_staff:
        raise Http404
    groupp = Group.objects.get(id=group_id)
    students_list = [student for student in Student.objects.all() if student.przynaleznosc_grupy == groupp]
    template = loader.get_template('edziennik/group_check.html')
    context = RequestContext(request, {
        'groupp': groupp,
        'students_list': students_list,
        'dzisiejsza_data': datetime.datetime.today().strftime("%d/%m/%Y")
    })
    return HttpResponse(template.render(context))

def attendance_check(request, groupp_id):
    ''' handles checked attendance of a group and generates error message if attendance was checked earlier that day'''
    if not request.user.is_staff:
        raise Http404

    p = get_object_or_404(Group, pk=groupp_id)
    # checks if attendance was checked today in this group, if yes, error
    for i in ClassDate.objects.all():
        if i.student in Group.objects.get(id = groupp_id).student_set.all() and i.date_of_class.date() == datetime.date.today():
            print i.student

            return render(request, 'edziennik/group_check.html', {
            'error_message': "BYLA JUZ DZIS SPRAWDZANA OBECNOSC W TEJ GRUPIE",
            'groupp': p,
            'dzisiejsza_data': datetime.datetime.today().strftime("%d/%m/%Y")
        })
    # process attendance of each student
    selected_student_list = request.POST.getlist('student')
    class_subject = request.POST.get('class_subject')
    print class_subject
    # wazne - getlist!!! - bierze liste wynikow a nie pojedynczy
    selected_students = [Student.objects.get(id = student) for student in selected_student_list]
    for student in selected_students:
        x = ClassDate(date_of_class = datetime.datetime.today(), student = Student.objects.get(id = student.id), subject = class_subject)
        x.save()

    messages.success(request, "Obecnosc w grupie %s sprawdzona" % p.group_name)
    return redirect('edziennik:name_home')


def attendance(request):
    ''' attendance results'''
    if not request.user.is_staff:
        raise Http404

    students = Student.objects.all()
    dates = ClassDate.objects.all()
    output = {}
    for student in students:
        output[student.student_name] = []
        for date in dates:
            if date.student == student:
                output[student.student_name] += [date.date_of_class.strftime("%d/%m/%Y")]
        
    output = output.items()
    
    template = loader.get_template('edziennik/attendance.html')
    context = RequestContext(request, {
        'output': output
    })
    return HttpResponse(template.render(context))

def attendance_by_group(request, group_id):
    ''' attendance results in a given group, after checkin attendance you are redirected here'''
    if not request.user.is_staff:
        raise Http404

    dates = ClassDate.objects.all()

    group = Group.objects.get(id=group_id)
    students = [student for student in Student.objects.all() if student.przynaleznosc_grupy == group]
    output = {}
    all_dates = []
    all_subjects = []
    for student in students:
        output[str(student.student_name)] = []
        for date in dates:
            if date.student == student and date.date_of_class.strftime("%d/%m/%Y") not in output[student.student_name]:
                output[student.student_name] += [date.date_of_class.strftime("%d/%m/%Y")]
                if date.date_of_class.strftime("%d/%m/%Y") not in all_dates:
                    all_dates += [date.date_of_class.strftime("%d/%m/%Y")]
                    all_subjects += [date.subject]
        
    output = output.items()
    output2 = []
    for i in output:
        i[1].insert(0, i[0])
        output2 += [i[1]]  
    output2 = [['data/student'] + all_dates]  + output2 
    for x, y in output:
        for i in all_dates:
            if i not in y:
                y.insert(all_dates.index(i)+1, 'absent')
    all_subjects = ['tematy:'] + all_subjects


    x = output2[:1] + [all_subjects] + output2[1:]
    new = [[] for i in range(len(x[0]))]
    for i in range(len(x)):
        for y in range(len(x[i])):
            new[y].append(x[i][y])     

    template = loader.get_template('edziennik/attendance_by_group.html')
    context = RequestContext(request, {
        'output': output,
        'output2': output2,
        'group': group,
        'all_dates': all_dates,
        'all_subjects': all_subjects,
        'x': x,
        'new': new
    })
    return HttpResponse(template.render(context))

def select_group_for_grades(request):
    '''select group to add grades, only groups assigned to a given teacher are returned'''
    if not request.user.is_staff:
        raise Http404

    date_today = datetime.datetime.today().strftime("%d/%m/%Y")
    groups = Group.objects.all()
    group_list = [g for g in groups if g.prowadzacy_lektor.lektor_name == request.user.username]
    template = loader.get_template('edziennik/select_group_grades.html')
    context = RequestContext(request, {
        'date_today': date_today,
        'group_list': group_list
    })
    return HttpResponse(template.render(context))

def group_grades(request, group_id):
    ''' displays a list of students in a given group and user can input name of test and grades for each student'''
    if not request.user.is_staff:
        raise Http404

    groupp = Group.objects.get(id=group_id)
    students_list = [student for student in Student.objects.all() if student.przynaleznosc_grupy == groupp]
    template = loader.get_template('edziennik/group_grades.html')
    context = RequestContext(request, {
        'groupp': groupp,
        'students_list': students_list,
        'dzisiejsza_data': datetime.datetime.today().strftime("%d/%m/%Y")
    })
    return HttpResponse(template.render(context))

def add_grades(request, groupp_id):
    ''' handles grades for each student in the group'''
    if not request.user.is_staff:
        raise Http404

    p = get_object_or_404(Group, pk=groupp_id)
    students_list = [student for student in Student.objects.all() if student.przynaleznosc_grupy == p]
    date_of_test = request.POST.get('date_of_test') or datetime.datetime.now().date()
    print 'req date: ', request.POST.get('date_of_test')
    print 'dt: ', datetime.datetime.now().date()
    name = request.POST.get('grade_name')
    for student in students_list:
        if request.POST.get(student.student_name):
            # make sure grade with this name is not already added
            student_grades_that_day = [g.name for g in student.grades_set.all() if str(g.date_of_test) == str(date_of_test)]
            for i in student.grades_set.all():
                print 'str(g.date_of_test.date())', str(i.date_of_test)
            if name in student_grades_that_day:
                messages.error(request, "Ocena za %s  w dniu %s byla juz dodana uczniowi %s. Sprobuj jeszcze raz" % (name, date_of_test, student.student_name))
                return redirect('edziennik:group_grades', group_id=p.id)
            x = Grades(date_of_test = date_of_test, name = name, student = student, score = request.POST.get(student.student_name))
            x.save()

   
    messages.success(request, "Oceny w grupie %s dodane" % p.group_name)
    return redirect('edziennik:name_home')