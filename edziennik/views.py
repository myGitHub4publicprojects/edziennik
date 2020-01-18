from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator

import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from django.templatetags.static import static

from edziennik.models import (Lector, Group, Parent, Student, ClassDate, Grades,
                              Admin_Profile, Quizlet, Homework, Initial_Import,
                              Initial_Import_Usage)
from .forms import AdminProfileForm, SignUpForm, ParentForm, StudentForm, HomeworkForm

from edziennik.utils import (admin_email, send_sms_twilio, generate_test_sms_msg,
                             create_unique_username, signup_email, import_students)

from .tasks import (quizlet_check_task,
    twilio_first_sms_status_check_task, twilio_second_sms_status_check_task, sms_test_task)


def index(request):
    '''displays either a login prompt or a button to check attendance, for logged in users'''
    if not request.user.is_authenticated:
        return render(request, 'edziennik/home_for_others.html')

    lector_users = [lector.user for lector in Lector.objects.all()]

    # home for lectors
    if request.user in lector_users:
        # show only groups associated with this lector
        lector = Lector.objects.get(user=request.user)
        context = {'groups': Group.objects.filter(lector=lector),
                   'all_groups': Group.objects.all()}
        return render(request, 'edziennik/home_for_lector.html', context)

    # home for admins
    if request.user.is_superuser:
        context = {'groups': Group.objects.all().order_by('name'),
                    'lectors': Lector.objects.all().order_by('user__last_name'), }
        lname = request.GET.get('lname')
        fname = request.GET.get('fname')
        if lname or fname:
            students = []
            results = Student.objects.all()
            if fname:
                results = results.filter(
                    first_name__icontains=fname)
            if lname:
                results = results.filter(
                    last_name__icontains=lname)
            for i in results:
                    s = {}
                    s['student'] = i
                    s['groups'] = Group.objects.filter(student=i)
                    students.append(s)
            context['students'] = students

        return render(request, 'edziennik/home_for_admin.html', context)

    # home for parents
    parent_users = [parent.user for parent in Parent.objects.all()]
    if request.user in parent_users:
        parent = Parent.objects.get(user=request.user)
        context = {
            'students': Student.objects.filter(parent=parent),
            'parent': parent,
        }
        return render(request, 'edziennik/home_for_parent.html', context)

    else:
        raise Http404

def lector(request, pk):
    '''displays lectors name and his groups'''
    if not request.user.is_superuser:
        raise Http404
    lector = get_object_or_404(Lector, pk=pk)
    lectors_groups = lector.group_set.all()
    # lectors hours
    today = datetime.date.today()
    # for dates between Sep and Dec
    if today.month in range(9,13):
        start_date = datetime.date(year=today.year, month=9, day=1)
        end_date = datetime.date(year=today.year + 1, month=8, day=30)
    # for dates between Jan and Aug
    else:
        start_date = datetime.date(year=today.year - 1, month=9, day=1)
        end_date = datetime.date(year=today.year, month=8, day=30)
    all_hours = ClassDate.objects.filter(lector=lector)
    hours_in_current_year = all_hours.filter(
        date_of_class__range=[start_date, end_date])
    hours_in_month = {}
    for i in hours_in_current_year:
        hours_in_month[
            str(i.date_of_class.month)+'.'+str(i.date_of_class.year)
            ] = hours_in_month.get(
                str(i.date_of_class.month)+'.'+str(i.date_of_class.year), 0) + 1

    hours_in_month_list = sorted(
        hours_in_month.items(), key=lambda i: (i[0][-4:], i[0].split('.')[0]))

    context = {
        'lector': lector,
        'lectors_groups': lectors_groups,
        'total_hours_year': len(hours_in_current_year),
        'hours_in_month_list': hours_in_month_list}

    return render(request, 'edziennik/lector.html', context)

def student(request, pk):
    '''displays info about a given student'''
    student = get_object_or_404(Student, pk = pk)
    parents = [parent.user for parent in Parent.objects.all()]
    groups = student.group_student.all()
    lectors = [group.lector.user for group in groups if group.lector]
    if not (request.user.is_superuser) and (request.user not in lectors) and not (
        request.user in parents):
        raise Http404
    student_groups = []
    for group in groups:
        grades = Grades.objects.filter(student=student, group=group)
        grade_list = [(g.date_of_test.strftime("%d/%m/%Y"), g.name, g.score) for g in grades]
        cd = ClassDate.objects.filter(group=group)
        homeworks = Homework.objects.filter(
        classdate__in=cd).order_by('-classdate__date_of_class')[:3]
        
        # students = group.student.all() # all students in this group
        all_classes = ClassDate.objects.filter(group=group).order_by('date_of_class') #all clases in this group
        # check students attendance and build an array
        attendence_table_header = ['data', 'temat', 'obecnosc']
        attendance_table_content = []
        for date in all_classes:
            date_string = date.date_of_class.strftime("%d/%m/%Y")
            subject = date.subject
            if student.student.filter(date_of_class=date.date_of_class):
                if  not student.has_homework.filter(date_of_class=date.date_of_class):
                    img_url = static('img/green_on_red.png')
                else:
                    img_url = static('img/check_sign_icon_green.png')
            else:
                img_url = static('img/x-mark-red.png')
                
            row = [date_string, subject, '<img src=%s>' % img_url]
            attendance_table_content.append(row)
        student_group = {
            'group': group,
            'grade_list': grade_list,
            'homeworks': homeworks,
            'attendence_table_header': attendence_table_header,
            'attendance_table_content': attendance_table_content,
        }
        student_groups.append(student_group)

    context = {
        'student': student,
        'student_groups': student_groups,
        'lectors': lectors
        }
    
    return render(request, 'edziennik/student.html', context)


class StudentList(ListView):
    model = Student
    def get_context_data(self, **kwargs):
        students = []
        for i in Student.objects.all():
            s = {}
            s['student'] = i
            s['groups'] = Group.objects.filter(student=i)
            students.append(s)
        context = super(StudentList, self).get_context_data(**kwargs)
        context['students'] = students
        return context


class ParentDetailView(DetailView):
    model=Parent

def group(request, pk):
    ''' enables to select an action for a group '''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    lector = group.lector
    students = group.student.all()
    cd = ClassDate.objects.filter(group=group)
    homeworks = Homework.objects.filter(classdate__in=cd).order_by('-classdate__date_of_class')
    context = {
        'group': group,
        'lector': lector,
        'students': students,
        'homeworks': homeworks
    }
    return render(request, 'edziennik/group.html', context)

def show_group_grades(request, pk):
    ''' displays grades in a group '''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    students = group.student.all()
    grades_in_this_group = Grades.objects.filter(student__in=students)

    dates_grades = []
    for grade in grades_in_this_group:
        if (grade.date_of_test, grade.name) not in dates_grades:
            dates_grades.append((grade.date_of_test, grade.name))

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
        'students': students,
        'group': group,
        'table_content': table_content,
    }
    return render(request, 'edziennik/show_group_grades.html', context)

def group_check(request, pk):
    ''' displays a group where attendance is checked'''
    if not request.user.is_authenticated:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    lector = group.lector
    # if not request.user.is_superuser and request.user != lector.user:
    #     raise Http404
    students = []
    for i in group.student.all():
        quizlet = Quizlet.objects.get(student=i, group=group).status
        students.append({'name': str(i), 'id': i.id, 'quizlet': quizlet})
    context = {
        'group': group,
        'students': students,
    }
    return render(request, 'edziennik/group_check.html', context)

def attendance_check(request, pk):
    ''' handles checked attendance of a group, adds one hour to a lector,
    lector can check attendance again in same group same day only if 'additional_hour'
    lector who checks gets an hour, if admin check group.lector gets an hour
    field is checked,
    and generates error message if attendance was checked earlier that day'''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    if not request.user.is_superuser:
        lector = Lector.objects.get(user=request.user)
    else:
        lector = group.lector

    # checks if attendance was checked today in this group, if yes, error,
    # if no 'additinal_hour' input
    additional_hour = request.POST.get('additional_hour')
    for i in ClassDate.objects.filter(group=group):
        if i.date_of_class == datetime.date.today() and additional_hour == None:
            context = {
            'error_message': """BYLA JUZ DZIS SPRAWDZANA OBECNOSC W TEJ GRUPIE. Jeśli chcesz jeszcze raz zaznaczyć obecność kliknij i zaznacz 'dodatkowa godzina'""",
            'group': group,
            }
            return render(request, 'edziennik/group_check.html', context)
   
    # process attendance of each student
    selected_student_list = request.POST.getlist('student') # wazne - getlist!!! - bierze liste wynikow a nie pojedynczy
    class_subject = request.POST.get('class_subject')
    class_date = ClassDate.objects.create(  date_of_class=datetime.datetime.today(),
                                            subject = class_subject,
                                            lector = lector,
                                            group=group)
    have_homework = request.POST.getlist('homework')
    for id in selected_student_list:
        student = Student.objects.get(id=id)
        class_date.student.add(student)
        # set quizlet status to False
        quizlet = Quizlet.objects.get(student=student, group=group)
        quizlet.status = False
        quizlet.save()
            
        if id in have_homework:
            class_date.has_homework.add(student)
        else:
            student_without_homework = Student.objects.get(id=id)
            admin_profile = Admin_Profile.objects.all().first()
            if admin_profile:
                if admin_profile.sms_when_no_homework:
                    if not admin_profile.sms_message_no_homework:
                        mail_title = 'Problem z wiadomością SMS Twilio'
                        mail_body = (
                            'Nie można było wysłać wiadomości SMS o braku zadanie domowego z powodu braku wzoru w ustawieniach.')
                        admin_email(mail_title, mail_body)
                    else:
                        parent = student_without_homework.parent
                        if student_without_homework.gender == 'M':
                            sex = 'male'
                        if student_without_homework.gender == 'F':
                            sex = 'female'
                        msg_pattern = admin_profile.sms_message_no_homework
                        message = generate_test_sms_msg(
                            sex, msg_pattern, student_without_homework.name)
                        print(message)
                        # send sms via twilio
                        # uncomment the line below to start using this service
                        # send_sms_twilio(parent, message)
                        # twilio_first_sms_status_check_task.apply_async(countdown=300)
                        # twilio_second_sms_status_check_task.apply_async(countdown=1200)

        
    # notify parents of absence
    absentees = group.student.all().exclude(id__in=selected_student_list)
    admin_profile = Admin_Profile.objects.all().first()
    if admin_profile:
        if admin_profile.sms_when_absent:
            if not admin_profile.sms_message_absence:
                mail_title = 'Problem z wiadomością SMS Twilio'
                mail_body = ('Nie można było wysłać wiadomości SMS o absencji z powodu braku wzoru w ustawieniach.')
                admin_email(mail_title, mail_body)
            else:
                for student in absentees:
                    parent = student.parent
                    if student.gender == 'M':
                        sex = 'male'
                    if student.gender == 'F':
                        sex = 'female'
                    msg_pattern = admin_profile.sms_message_absence
                    message = generate_test_sms_msg(
                        sex, msg_pattern, student.name)
                    print(message)
                    # send sms via twilio
                    # uncomment the line below to start using this service
                    # send_sms_twilio(parent, message)
                    # twilio_first_sms_status_check_task.apply_async(countdown=300)
                    # twilio_second_sms_status_check_task.apply_async(countdown=1200)

    messages.success(request, "Obecnosc w grupie %s sprawdzona" % group.name)
    # return redirect('edziennik:name_home')
    return redirect(reverse('edziennik:group', args=(group.id,)))

def attendance_by_group(request, group_id):
    ''' displays attendance results in a given group'''
    if not request.user.is_staff:
        raise Http404

    group = get_object_or_404(Group, pk=group_id)
    lector = group.lector
    # if not request.user.is_superuser and request.user != lector.user:
    #     raise Http404
    students = group.student.all()
    table_content = []
    classes_in_group = ClassDate.objects.filter(group=group).order_by('date_of_class')

    for i in classes_in_group:
        row = [i.date_of_class.strftime("%d/%m/%Y"), i.subject]
        for s in students:
            if s in i.student.all():
                if s.has_homework.filter(date_of_class=i.date_of_class):
                    img_url = static('img/check_sign_icon_green.png')
                else:
                    img_url = static('img/green_on_red.png')
            else:
                img_url = static('img/x-mark-red.png')
            row.append('<img src=%s>' % img_url)
        table_content.append(row)


    context = {
        'group': group,
        'students': students,
        'table_content': table_content,
        }
    return render(request, 'edziennik/attendance_by_group.html', context)

def group_grades(request, group_id):
    ''' displays a list of students in a given group,
    lector can input name of test and grades for each student'''
    if not request.user.is_staff:
        raise Http404

    group = get_object_or_404(Group, pk=group_id)
    lector = group.lector
    # if not request.user.is_superuser and request.user != lector.user:
    #     raise Http404
    students = group.student.all()
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
    students = group.student.all()
    date_of_test = request.POST.get('date_of_test') or datetime.datetime.today()
    grade_name = request.POST.get('grade_name')
    for student in students:
        if request.POST.get(str(student)):
            todays_grades = Grades.objects.filter(student=student, group=group)
            # make sure grade with this name in this goup is not already added
            if todays_grades.filter(name=grade_name, date_of_test=date_of_test):
                messages.error(request, "Ocena za %s  w dniu %s byla juz dodana uczniowi %s. Sprobuj jeszcze raz" % (grade_name, date_of_test, str(student)))
                return redirect('edziennik:group_grades', group_id=pk)
            # add grade
            Grades.objects.create(
                name=grade_name,
                date_of_test=date_of_test,
                student = student,
                score=request.POST.get(str(student)),
                group=group
                )

    messages.success(request, "Oceny w grupie %s dodane" % group.name)
    return redirect(reverse('edziennik:group', args=(group.id,)))

def add_quizlet(request, pk):
    '''enables selecting students that should get rewards for quizlet activity'''
    if not request.user.is_superuser:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    students = group.student.all()
    context = {
        'group': group,
        'students': students,
        }
    return render(request, 'edziennik/add_quizlet.html', context)

def process_quizlet(request, pk):
    if not request.user.is_superuser:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    students = request.POST.getlist('student')
    for student in students:
        student_object = Student.objects.get(id=student)
        quizlet = Quizlet.objects.get(student=student_object, group=group)
        quizlet.status = True
        quizlet.save()

    messages.success(request, "Punkty za quizlet w grupie %s dodane" % group)
    return redirect('edziennik:name_home')


def advanced_settings(request):
    '''displays admin user advanced settings (Admin_Profile class),
    enables updating details'''
    if not request.user.is_superuser:
        raise Http404
    if request.method == 'GET':
        obj, created = Admin_Profile.objects.get_or_create(
            pk=1,
            defaults={'user':request.user},
        )
        # display newly created or previous object in form
        form = AdminProfileForm(instance=obj)
        context = {'form': form}
        return render(request, 'edziennik/advanced_settings.html', context)

    if request.method == 'POST':
        profile = Admin_Profile.objects.get(pk=1)
        form = AdminProfileForm(request.POST, instance = profile)
        if form.is_valid():
            form.save()

            messages.success(request, "Ustawienia zachowane")
            return redirect(reverse('edziennik:name_home'))


def quizlet_test_email(request):
    '''Accepts ajax call with quizlet username, password and school
    admin email. Make call to check quizlet and return success or error'''
    username = request.POST.get('username', None)
    password = request.POST.get('password', None)
    admin_email = request.POST.get('adminEmail', None)

    data = {}
    # rougly validate email address
    if not '@' in admin_email or not '.' in admin_email:
        data['result'] = 'Invalid_email'
        return JsonResponse(data)

    # run quizlet check and send email to an admin
    quizlet_check_task(username, password, admin_email)
    print(username, password, admin_email)
    data['result'] = 'Success!'
    return JsonResponse(data)

def sms_test(request):
    '''Accepts ajax call with Twilio credentials, absence and no homework messages
    Makes call to send sms and return success or error'''
    twilio_account_sid = request.POST.get('account_sid', None)
    twilio_auth_token = request.POST.get('auth_token', None)
    messaging_service_sid = request.POST.get('messaging_service_sid', None)
    msg_no_homework = request.POST.get('message_no_homework', None)
    msg_absence = request.POST.get('message_absence', None)
    test_tel = '+48' + str(request.POST.get('test_tel', None))

    male_no_homework = generate_test_sms_msg(
        'male', msg_no_homework, 'Jan Kowalski')
    female_no_homework = generate_test_sms_msg(
        'female', msg_no_homework, 'Ola Kowalska')
    male_absence = generate_test_sms_msg(
        'male', msg_absence, 'Jan Kowalski')
    female_absence = generate_test_sms_msg(
        'female', msg_absence, 'Jan Kowalski')
    

    

    # send sms and check delivery status
    for msg in [male_no_homework, female_no_homework, male_absence, female_absence]:
        # sms_test_task(twilio_account_sid, twilio_auth_token, messaging_service_sid, test_tel, msg)
        print(msg)

    data = {'result': 'Success!'}
    return JsonResponse(data)

def message_test(request):
    '''Accepts ajax call with a user input message and return processed messages
    in two versions: male and female with a test student name'''
    msg = request.POST.get('msg', None)
    print(msg)
    male_msg = generate_test_sms_msg('male', msg, 'Jan Kowalski')
    female_msg = generate_test_sms_msg('female', msg, 'Ola Kowalska')
    data = {'male_msg': male_msg,
            'female_msg': female_msg}
    return JsonResponse(data)

def signup(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST, prefix="user")
        parent_form = ParentForm(request.POST)
        student_form = StudentForm(request.POST, prefix="student")
        if user_form.is_valid() and parent_form.is_valid() and student_form.is_valid():
            # create user
            fname = user_form.cleaned_data['first_name']
            lname = user_form.cleaned_data['last_name']
            password = User.objects.make_random_password(length=8)
            user = User.objects.create(
                first_name=fname,
                last_name=lname,
                email=user_form.cleaned_data['email'],
                username=create_unique_username(fname, lname),
            )
            user.set_password(password)
            user.save()
            # create parent
            parent = parent_form.save(commit=False)
            parent.user = user
            parent.save()

            # create student
            student = student_form.save(commit=False)
            student.group = Group.objects.all().first()
            student.parent = parent
            student.save()

            # email to parent with login details (url, username, pass)
            signup_email(parent, student, password)
            
            # login parent and redirect to home page
            login(request, user)
            return redirect('edziennik:name_home')

        else:
            context = {
                'user_form': user_form,
                'parent_form': parent_form,
                'student_form': student_form,
            }

    else:
        context = {
            'user_form': SignUpForm(prefix="user"),
            'parent_form': ParentForm(),
            'student_form': StudentForm(prefix="student"),
        }

    return render(request, 'edziennik/signup.html', context)


def duplicate_check(request):
	if request.GET.get('email'):
		email = request.GET.get('email')
		user = User.objects.filter(email=email)
		if user:
			return HttpResponse('present')
		return HttpResponse('absent')


def add_homework(request, pk):
    '''add homework to a ClassDate object with todays date,
    display error message if:
    trying to add second homework for this group,
    trying to add homework without attendance check this day'''
    if not request.user.is_staff:
        raise Http404
    group = get_object_or_404(Group, pk=pk)
    today_cd = ClassDate.objects.filter(
            group=group,
            date_of_class=datetime.datetime.now().date())

    # prevent homework if attendance not checked today
    if not today_cd.exists():
        messages.error(request, "Nie była sprawdzona obecność dziś")
        return redirect(reverse('edziennik:group', args=(group.id,)))

    # prevent homework if one homework already exists for this classdate
    if today_cd.last().homework_set.all().exists():
        messages.error(request, "Już dodany homework do ostatniej lekcji")
        return redirect(reverse('edziennik:group', args=(group.id,)))

    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            homework = form.save(commit=False)
            homework.classdate = today_cd.last()
            homework.save()

            messages.success(request, "Zadanie domowe dodane")
            return redirect(reverse('edziennik:group', args=(group.id,)))

    form = HomeworkForm()
    context = {'form': form, 'group': group}
    return render(request, 'edziennik/add_homework.html', context)


class OnlySuperuserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class Initial_Import_Create(OnlySuperuserMixin, CreateView):
    model = Initial_Import
    fields = ['file']


class Initial_Import_Detail(OnlySuperuserMixin, DetailView):
    model = Initial_Import

    def post(self, request, *args, **kwargs):
        f = request.POST['initial_import_file']
        ii = Initial_Import.objects.get(id=f)
        f_usage = import_students(ii)
        errors = f_usage.initial_import_usage_errors_set.all().count()
        print('errors: ', errors)
        if errors:
            messages.add_message(
                self.request, messages.ERROR, 
                'WYSTĄPIŁY BŁĘDY - DANE NIE ZOSTAŁY ZAIMPORTOWANE')
        else:
            messages.add_message(
                self.request, messages.SUCCESS, 'Import zakończony pomyślnie')
        return redirect(reverse(
            'edziennik:initial_import_usage_detail', args=(f_usage.id,)))


class Initial_Import_List(OnlySuperuserMixin, ListView):
    model = Initial_Import


class Initial_Import_Usage_Detail(OnlySuperuserMixin, DetailView):
    model = Initial_Import_Usage
