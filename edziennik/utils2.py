from edziennik.models import Lector, Group, Parent, Student, ClassDate, Grades
import datetime


def generate_weekly_admin_report():
    ''' genereates raport for last week '''
    today = datetime.date.today()
    title = 'Attendance and grades report'
    class_dates = ClassDate.objects.filter(date_of_class__gte=today-datetime.timedelta(7))
    output = 'Attendance has not been checked this week\n'
    if class_dates:
        output = ''
    for class_date in class_dates:
        students = class_date.student.all()
        group = students.first().group
        date = class_date.date_of_class
        head = 'On %s\nin group: %s\n' % (str(date), group.name)
        f = 'the following students were present:'
        s = ''.join(['\n' + s.name for s in students])
        end = '\n--------------------------------\n'
        section = head + f + s + end
        output += section

    grades = Grades.objects.filter(timestamp__date__gte=today-datetime.timedelta(7))
    output2 = 'No grades have been given last week'
    if grades:
        output2 = '\n' + 'Last week the following grades were given:\n'
    for g in grades:
        date = g.timestamp.date()
        student = g.student
        group = student.group.name
        name = g.name
        score = g.score
        g_str = ' '.join([str(date), 'group:', group, 'student:', student.name,
                         'for:', name, 'score:', str(score), '\n'])
        output2 += g_str

    body = output  + output2
    return (title, body)