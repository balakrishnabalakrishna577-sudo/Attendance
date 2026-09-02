"""
HOD views — dashboard, teachers, classes, subjects, assignments.
Students and attendance reports have been removed.
"""

import csv
import io
from datetime import date as dt_date
from django.shortcuts import render, redirect
from django.contrib import messages

from attendance.decorators import hod_required
from attendance.services import json_storage as db
from attendance.models import AcademicEvent, Meeting, TeacherWorkAssignment


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

@hod_required
def hod_dashboard(request):
    today = dt_date.today().isoformat()
    ctx = {
        'total_teachers':    len(db.get_all_teachers()),
        'total_classes':     len(db.get_all_classes()),
        'total_subjects':    len(db.get_all_subjects()),
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
        form_type = request.POST.get('form_type', 'manual')

        # ── CSV import ─────────────────────────────────────────
        if form_type == 'csv':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, 'Please select a CSV file.')
                return render(request, 'attendance/hod/teacher_form.html', {'action': 'Add'})
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File must be a .csv file.')
                return render(request, 'attendance/hod/teacher_form.html', {'action': 'Add'})
            try:
                decoded = csv_file.read().decode('utf-8-sig')
                reader  = csv.DictReader(io.StringIO(decoded))
                count, errors = 0, []
                for i, row in enumerate(reader, start=2):
                    name = row.get('name', '').strip()
                    if not name:
                        errors.append(f'Row {i}: name is required — skipped.')
                        continue
                    db.create_teacher_no_login(
                        name,
                        row.get('email', '').strip(),
                        row.get('phone', '').strip(),
                        row.get('department', '').strip(),
                    )
                    count += 1
                if count:
                    messages.success(request,
                        f'{count} teacher{"s" if count != 1 else ""} imported successfully.')
                for e in errors[:5]:
                    messages.warning(request, e)
            except Exception as exc:
                messages.error(request, f'CSV parse error: {exc}')
            return redirect('teacher_list')

        # ── Manual add ─────────────────────────────────────────
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

    is_import = request.GET.get('import') == '1'
    return render(request, 'attendance/hod/teacher_form.html',
                  {'action': 'Add', 'is_import': is_import})


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
    return render(request, 'attendance/hod/class_list.html',
                  {'classes': db.get_all_classes()})


@hod_required
def class_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        desc = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Class name is required.')
            return render(request, 'attendance/hod/class_form.html', {'action': 'Add'})
        db.create_class(name, desc)
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
        desc = request.POST.get('description', '').strip()
        if not name:
            messages.error(request, 'Class name is required.')
            return render(request, 'attendance/hod/class_form.html',
                          {'action': 'Edit', 'cls': cls})
        db.update_class(class_id, name, desc)
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
    return render(request, 'attendance/hod/subject_list.html',
                  {'subjects': db.get_all_subjects()})


@hod_required
def subject_add(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        desc = request.POST.get('description', '').strip()
        if not name or not code:
            messages.error(request, 'Name and code are required.')
            return render(request, 'attendance/hod/subject_form.html', {'action': 'Add'})
        db.create_subject(name, code, desc)
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
        desc = request.POST.get('description', '').strip()
        if not name or not code:
            messages.error(request, 'Name and code are required.')
            return render(request, 'attendance/hod/subject_form.html',
                          {'action': 'Edit', 'subject': subj})
        db.update_subject(subject_id, name, code, desc)
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
# Assignments (teacher → class → subject)
# ─────────────────────────────────────────────

@hod_required
def assignment_list(request):
    assignments = db.get_all_assignments()
    teachers = {t['id']: t for t in db.get_all_teachers()}
    classes  = {c['id']: c for c in db.get_all_classes()}
    subjects = {s['id']: s for s in db.get_all_subjects()}
    enriched = []
    for a in assignments:
        enriched.append({
            'id':           a['id'],
            'teacher':      teachers.get(a.get('teacher_id', ''), {}).get('name', 'Unknown'),
            'class_name':   classes.get(a.get('class_id', ''), {}).get('name', 'Unknown'),
            'subject':      subjects.get(a.get('subject_id', ''), {}).get('name', 'Unknown'),
            'subject_code': subjects.get(a.get('subject_id', ''), {}).get('code', ''),
        })
    return render(request, 'attendance/hod/assignment_list.html', {'assignments': enriched})


@hod_required
def assignment_add(request):
    teachers = db.get_all_teachers()
    classes  = db.get_all_classes()
    subjects = db.get_all_subjects()
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id', '').strip()
        class_id   = request.POST.get('class_id', '').strip()
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
    t = db.get_teacher(assignment.get('teacher_id', ''))
    c = db.get_class(assignment.get('class_id', ''))
    s = db.get_subject(assignment.get('subject_id', ''))
    label = f"{t['name'] if t else '?'} → {c['name'] if c else '?'} → {s['name'] if s else '?'}"
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': label, 'cancel_url': 'assignment_list'})



# ─────────────────────────────────────────────
# Subject CSV Import
# ─────────────────────────────────────────────

@hod_required
def subject_import(request):
    """Import subjects from CSV. Columns: name, code, description"""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('subject_list')
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File must be a .csv file.')
            return redirect('subject_list')
        try:
            decoded = csv_file.read().decode('utf-8-sig')
            reader  = csv.DictReader(io.StringIO(decoded))
            count, errors = 0, []
            for i, row in enumerate(reader, start=2):
                name = row.get('name', '').strip()
                code = row.get('code', '').strip()
                desc = row.get('description', '').strip()
                if not name or not code:
                    errors.append(f'Row {i}: name and code are required — skipped.')
                    continue
                db.create_subject(name, code, desc)
                count += 1
            if count:
                messages.success(request,
                    f'{count} subject{"s" if count != 1 else ""} imported successfully.')
            for e in errors[:5]:
                messages.warning(request, e)
        except Exception as exc:
            messages.error(request, f'CSV parse error: {exc}')
    return redirect('subject_list')
