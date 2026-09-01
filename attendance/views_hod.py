"""
HOD views — dashboard, teachers, classes, subjects, students,
assignments, attendance reports, CSV export.
"""

import csv
import io
from datetime import date as dt_date
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

from attendance.decorators import hod_required
from attendance.services import json_storage as db


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

from attendance.models import AcademicEvent, Meeting, TeacherWorkAssignment, TimetableSlot

@hod_required
def hod_dashboard(request):
    today = dt_date.today().isoformat()
    ctx = {
        'total_teachers':    len(db.get_all_teachers()),
        'total_classes':     len(db.get_all_classes()),
        'total_subjects':    len(db.get_all_subjects()),
        'total_students':    len(db.get_all_students()),
        'today_attendance':  db.get_today_attendance_count(today),
        'today':             today,
        'upcoming_events':   AcademicEvent.objects.filter(start_date__gte=today).count(),
        'upcoming_meetings': Meeting.objects.filter(meeting_date__gte=today).count(),
        'pending_work':      TeacherWorkAssignment.objects.filter(status='pending').count(),
    }
    return render(request, 'attendance/hod/dashboard.html', ctx)


# ─────────────────────────────────────────────
# Teachers
# ─────────────────────────────────────────────

@hod_required
def teacher_list(request):
    teachers = db.get_all_teachers()
    return render(request, 'attendance/hod/teacher_list.html', {'teachers': teachers})


@hod_required
def teacher_add(request):
    if request.method == 'POST':
        name       = request.POST.get('name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        department = request.POST.get('department', '').strip()

        if not name:
            messages.error(request, 'Teacher name is required.')
            return render(request, 'attendance/hod/teacher_form.html', {'action': 'Add'})

        db.create_teacher_no_login(name, email, phone, department)
        messages.success(request, f'Teacher {name} added successfully.')
        return redirect('teacher_list')

    return render(request, 'attendance/hod/teacher_form.html', {'action': 'Add'})


@hod_required
def teacher_edit(request, teacher_id):
    teacher = db.get_teacher(teacher_id)
    if not teacher:
        messages.error(request, 'Teacher not found.')
        return redirect('teacher_list')

    if request.method == 'POST':
        name       = request.POST.get('name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()
        department = request.POST.get('department', '').strip()

        if not name:
            messages.error(request, 'Name is required.')
            return render(request, 'attendance/hod/teacher_form.html',
                          {'action': 'Edit', 'teacher': teacher})

        db.update_teacher(teacher_id, name, email, phone, department)
        messages.success(request, 'Teacher updated successfully.')
        return redirect('teacher_list')

    return render(request, 'attendance/hod/teacher_form.html',
                  {'action': 'Edit', 'teacher': teacher})


@hod_required
def teacher_delete(request, teacher_id):
    teacher = db.get_teacher(teacher_id)
    if not teacher:
        messages.error(request, 'Teacher not found.')
        return redirect('teacher_list')
    if request.method == 'POST':
        db.delete_teacher(teacher_id)
        messages.success(request, f'Teacher {teacher["name"]} deleted.')
        return redirect('teacher_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': teacher['name'], 'cancel_url': 'teacher_list'})


# ─────────────────────────────────────────────
# Classes
# ─────────────────────────────────────────────

@hod_required
def class_list(request):
    classes = db.get_all_classes()
    return render(request, 'attendance/hod/class_list.html', {'classes': classes})


@hod_required
def class_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Class name is required.')
            return render(request, 'attendance/hod/class_form.html', {'action': 'Add'})
        db.create_class(name, description)
        messages.success(request, f'Class "{name}" added.')
        return redirect('class_list')
    return render(request, 'attendance/hod/class_form.html', {'action': 'Add'})


@hod_required
def class_edit(request, class_id):
    cls = db.get_class(class_id)
    if not cls:
        messages.error(request, 'Class not found.')
        return redirect('class_list')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Class name is required.')
            return render(request, 'attendance/hod/class_form.html',
                          {'action': 'Edit', 'cls': cls})
        db.update_class(class_id, name, description)
        messages.success(request, 'Class updated.')
        return redirect('class_list')
    return render(request, 'attendance/hod/class_form.html', {'action': 'Edit', 'cls': cls})


@hod_required
def class_delete(request, class_id):
    cls = db.get_class(class_id)
    if not cls:
        messages.error(request, 'Class not found.')
        return redirect('class_list')
    if request.method == 'POST':
        db.delete_class(class_id)
        messages.success(request, f'Class "{cls["name"]}" deleted.')
        return redirect('class_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': cls['name'], 'cancel_url': 'class_list'})


# ─────────────────────────────────────────────
# Subjects
# ─────────────────────────────────────────────

@hod_required
def subject_list(request):
    subjects = db.get_all_subjects()
    return render(request, 'attendance/hod/subject_list.html', {'subjects': subjects})


@hod_required
def subject_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        if not name or not code:
            messages.error(request, 'Name and code are required.')
            return render(request, 'attendance/hod/subject_form.html', {'action': 'Add'})
        db.create_subject(name, code, description)
        messages.success(request, f'Subject "{name}" added.')
        return redirect('subject_list')
    return render(request, 'attendance/hod/subject_form.html', {'action': 'Add'})


@hod_required
def subject_edit(request, subject_id):
    subj = db.get_subject(subject_id)
    if not subj:
        messages.error(request, 'Subject not found.')
        return redirect('subject_list')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        if not name or not code:
            messages.error(request, 'Name and code are required.')
            return render(request, 'attendance/hod/subject_form.html',
                          {'action': 'Edit', 'subject': subj})
        db.update_subject(subject_id, name, code, description)
        messages.success(request, 'Subject updated.')
        return redirect('subject_list')
    return render(request, 'attendance/hod/subject_form.html',
                  {'action': 'Edit', 'subject': subj})


@hod_required
def subject_delete(request, subject_id):
    subj = db.get_subject(subject_id)
    if not subj:
        messages.error(request, 'Subject not found.')
        return redirect('subject_list')
    if request.method == 'POST':
        db.delete_subject(subject_id)
        messages.success(request, f'Subject "{subj["name"]}" deleted.')
        return redirect('subject_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': subj['name'], 'cancel_url': 'subject_list'})


# ─────────────────────────────────────────────
# Students
# ─────────────────────────────────────────────

@hod_required
def student_list(request):
    students = db.get_all_students()
    classes = db.get_all_classes()
    class_map = {c['id']: c['name'] for c in classes}
    query = request.GET.get('q', '').strip().lower()
    filter_class = request.GET.get('class_id', '').strip()

    for s in students:
        s['class_name'] = class_map.get(s.get('class_id', ''), 'Unknown')

    if query:
        students = [s for s in students
                    if query in s['name'].lower() or query in s.get('roll_number', '').lower()]
    if filter_class:
        students = [s for s in students if s.get('class_id') == filter_class]

    return render(request, 'attendance/hod/student_list.html', {
        'students': students,
        'classes': classes,
        'query': query,
        'filter_class': filter_class,
    })


@hod_required
def student_add(request):
    classes = db.get_all_classes()
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number', '').strip()
        name = request.POST.get('name', '').strip()
        class_id = request.POST.get('class_id', '').strip()
        if not all([roll_number, name, class_id]):
            messages.error(request, 'All fields are required.')
            return render(request, 'attendance/hod/student_form.html',
                          {'action': 'Add', 'classes': classes})
        db.create_student(roll_number, name, class_id)
        messages.success(request, f'Student {name} added.')
        return redirect('student_list')
    return render(request, 'attendance/hod/student_form.html',
                  {'action': 'Add', 'classes': classes})


@hod_required
def student_edit(request, student_id):
    student = db.get_student(student_id)
    classes = db.get_all_classes()
    if not student:
        messages.error(request, 'Student not found.')
        return redirect('student_list')
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number', '').strip()
        name = request.POST.get('name', '').strip()
        class_id = request.POST.get('class_id', '').strip()
        if not all([roll_number, name, class_id]):
            messages.error(request, 'All fields are required.')
            return render(request, 'attendance/hod/student_form.html',
                          {'action': 'Edit', 'student': student, 'classes': classes})
        db.update_student(student_id, roll_number, name, class_id)
        messages.success(request, 'Student updated.')
        return redirect('student_list')
    return render(request, 'attendance/hod/student_form.html',
                  {'action': 'Edit', 'student': student, 'classes': classes})


@hod_required
def student_delete(request, student_id):
    student = db.get_student(student_id)
    if not student:
        messages.error(request, 'Student not found.')
        return redirect('student_list')
    if request.method == 'POST':
        db.delete_student(student_id)
        messages.success(request, f'Student {student["name"]} deleted.')
        return redirect('student_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': student['name'], 'cancel_url': 'student_list'})


@hod_required
def student_import(request):
    """Import students from CSV file."""
    classes = db.get_all_classes()
    if request.method == 'POST':
        class_id = request.POST.get('class_id', '').strip()
        csv_file = request.FILES.get('csv_file')

        if not class_id or not csv_file:
            messages.error(request, 'Class and CSV file are required.')
            return render(request, 'attendance/hod/student_import.html', {'classes': classes})

        if not db.get_class(class_id):
            messages.error(request, 'Invalid class selected.')
            return render(request, 'attendance/hod/student_import.html', {'classes': classes})

        try:
            decoded = csv_file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded))
            count = 0
            errors = []
            for i, row in enumerate(reader, start=2):
                roll = row.get('roll_number', '').strip()
                name = row.get('name', '').strip()
                if not roll or not name:
                    errors.append(f'Row {i}: roll_number and name are required.')
                    continue
                db.create_student(roll, name, class_id)
                count += 1
            if count:
                messages.success(request, f'{count} students imported successfully.')
            if errors:
                for e in errors[:5]:  # show first 5 errors
                    messages.warning(request, e)
        except Exception as exc:
            messages.error(request, f'CSV parse error: {exc}')

        return redirect('student_list')

    return render(request, 'attendance/hod/student_import.html', {'classes': classes})


# ─────────────────────────────────────────────
# Assignments
# ─────────────────────────────────────────────

@hod_required
def assignment_list(request):
    assignments = db.get_all_assignments()
    teachers = {t['id']: t for t in db.get_all_teachers()}
    classes = {c['id']: c for c in db.get_all_classes()}
    subjects = {s['id']: s for s in db.get_all_subjects()}

    enriched = []
    for a in assignments:
        enriched.append({
            'id': a['id'],
            'teacher': teachers.get(a.get('teacher_id', ''), {}).get('name', 'Unknown'),
            'class_name': classes.get(a.get('class_id', ''), {}).get('name', 'Unknown'),
            'subject': subjects.get(a.get('subject_id', ''), {}).get('name', 'Unknown'),
            'subject_code': subjects.get(a.get('subject_id', ''), {}).get('code', ''),
        })
    return render(request, 'attendance/hod/assignment_list.html', {'assignments': enriched})


@hod_required
def assignment_add(request):
    teachers = db.get_all_teachers()
    classes = db.get_all_classes()
    subjects = db.get_all_subjects()

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id', '').strip()
        class_id = request.POST.get('class_id', '').strip()
        subject_id = request.POST.get('subject_id', '').strip()

        if not all([teacher_id, class_id, subject_id]):
            messages.error(request, 'All fields are required.')
            return render(request, 'attendance/hod/assignment_form.html',
                          {'teachers': teachers, 'classes': classes, 'subjects': subjects})

        result = db.create_assignment(teacher_id, class_id, subject_id)
        if result is None:
            messages.warning(request, 'This assignment already exists.')
        else:
            messages.success(request, 'Assignment created successfully.')
        return redirect('assignment_list')

    return render(request, 'attendance/hod/assignment_form.html',
                  {'teachers': teachers, 'classes': classes, 'subjects': subjects})


@hod_required
def assignment_delete(request, assignment_id):
    assignment = db.get_assignment(assignment_id)
    if not assignment:
        messages.error(request, 'Assignment not found.')
        return redirect('assignment_list')
    if request.method == 'POST':
        db.delete_assignment(assignment_id)
        messages.success(request, 'Assignment removed.')
        return redirect('assignment_list')

    # Build label for confirmation page
    t = db.get_teacher(assignment.get('teacher_id', ''))
    c = db.get_class(assignment.get('class_id', ''))
    s = db.get_subject(assignment.get('subject_id', ''))
    label = f"{t['name'] if t else '?'} → {c['name'] if c else '?'} → {s['name'] if s else '?'}"
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': label, 'cancel_url': 'assignment_list'})


# ─────────────────────────────────────────────
# Attendance Reports (HOD)
# ─────────────────────────────────────────────

@hod_required
def attendance_report(request):
    teachers = db.get_all_teachers()
    classes = db.get_all_classes()
    subjects = db.get_all_subjects()
    students = db.get_all_students()

    # Build lookup maps
    teacher_map = {t['id']: t['name'] for t in teachers}
    class_map = {c['id']: c['name'] for c in classes}
    subject_map = {s['id']: s['name'] for s in subjects}
    student_map = {s['id']: s for s in students}

    # Filters from GET
    f_date = request.GET.get('date', '').strip()
    f_teacher = request.GET.get('teacher_id', '').strip()
    f_class = request.GET.get('class_id', '').strip()
    f_subject = request.GET.get('subject_id', '').strip()
    f_student = request.GET.get('student_id', '').strip()

    att_records = db.get_attendance_by_filters(
        date=f_date or None,
        teacher_id=f_teacher or None,
        class_id=f_class or None,
        subject_id=f_subject or None,
    )

    # Aggregate stats per student per subject
    stats = {}  # key: (student_id, class_id, subject_id)
    for att in att_records:
        cid = att.get('class_id')
        sid = att.get('subject_id')
        for rec in att.get('records', []):
            stid = rec.get('student_id')
            if f_student and stid != f_student:
                continue
            key = (stid, cid, sid)
            if key not in stats:
                stats[key] = {'present': 0, 'absent': 0,
                              'dates': set(), 'teacher_id': att.get('teacher_id')}
            stats[key]['dates'].add(att.get('date'))
            if rec.get('status') == 'Present':
                stats[key]['present'] += 1
            else:
                stats[key]['absent'] += 1

    report_rows = []
    for (stid, cid, sid), s in stats.items():
        student = student_map.get(stid, {})
        total = s['present'] + s['absent']
        pct = round((s['present'] / total) * 100, 1) if total else 0.0
        report_rows.append({
            'student_name': student.get('name', 'Unknown'),
            'roll_number': student.get('roll_number', '-'),
            'class_name': class_map.get(cid, 'Unknown'),
            'subject_name': subject_map.get(sid, 'Unknown'),
            'teacher_name': teacher_map.get(s['teacher_id'], 'Unknown'),
            'present': s['present'],
            'absent': s['absent'],
            'total': total,
            'percentage': pct,
            'student_id': stid,
            'class_id': cid,
            'subject_id': sid,
        })

    # Sort by class, student name
    report_rows.sort(key=lambda r: (r['class_name'], r['student_name']))

    # CSV export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Student Name', 'Roll Number', 'Class', 'Subject',
                         'Teacher', 'Present', 'Absent', 'Total', 'Attendance %'])
        for row in report_rows:
            writer.writerow([
                row['student_name'], row['roll_number'], row['class_name'],
                row['subject_name'], row['teacher_name'],
                row['present'], row['absent'], row['total'], row['percentage'],
            ])
        return response

    ctx = {
        'report_rows': report_rows,
        'teachers': teachers,
        'classes': classes,
        'subjects': subjects,
        'students': students,
        'f_date': f_date,
        'f_teacher': f_teacher,
        'f_class': f_class,
        'f_subject': f_subject,
        'f_student': f_student,
    }
    return render(request, 'attendance/hod/attendance_report.html', ctx)
