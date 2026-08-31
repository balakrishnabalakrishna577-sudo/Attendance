"""
Teacher views — dashboard, attendance marking, and personal attendance records.
All requests are verified against server-side assignments (no frontend-only hiding).
"""

import json
from datetime import date as dt_date
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages

from attendance.decorators import teacher_required
from attendance.services import json_storage as db


def _get_teacher_id(request) -> str:
    return request.session.get('teacher_id', '')


def _enrich_assignments(assignments: list) -> list:
    """Add class_name and subject_name to assignment dicts."""
    class_map = {c['id']: c for c in db.get_all_classes()}
    subject_map = {s['id']: s for s in db.get_all_subjects()}
    enriched = []
    for a in assignments:
        cls = class_map.get(a.get('class_id', ''), {})
        subj = subject_map.get(a.get('subject_id', ''), {})
        enriched.append({
            **a,
            'class_name': cls.get('name', 'Unknown'),
            'subject_name': subj.get('name', 'Unknown'),
            'subject_code': subj.get('code', ''),
        })
    return enriched


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

@teacher_required
def teacher_dashboard(request):
    teacher_id = _get_teacher_id(request)
    teacher = db.get_teacher(teacher_id)
    if not teacher:
        messages.error(request, 'Teacher profile not found.')
        return redirect('logout')

    assignments = _enrich_assignments(db.get_teacher_assignments(teacher_id))
    today = dt_date.today().isoformat()

    # Today's attendance count for this teacher
    today_att = db.get_attendance_by_filters(date=today, teacher_id=teacher_id)
    today_count = sum(len(a.get('records', [])) for a in today_att)

    # Overall attendance percentage across all assigned classes
    all_att = db.get_attendance_by_filters(teacher_id=teacher_id)
    total_present = 0
    total_records = 0
    for att in all_att:
        for rec in att.get('records', []):
            total_records += 1
            if rec.get('status') == 'Present':
                total_present += 1
    overall_pct = round((total_present / total_records) * 100, 1) if total_records else 0.0

    ctx = {
        'teacher': teacher,
        'assignments': assignments,
        'today': today,
        'today_count': today_count,
        'overall_pct': overall_pct,
        'total_records': total_records,
    }
    return render(request, 'attendance/teacher/dashboard.html', ctx)


# ─────────────────────────────────────────────
# Mark / Edit Attendance
# ─────────────────────────────────────────────

@teacher_required
def mark_attendance(request, class_id, subject_id):
    """
    Show attendance form for a specific class+subject.
    Server-side check: teacher must have an assignment for this pair.
    """
    teacher_id = _get_teacher_id(request)

    # ── ACCESS CONTROL ──────────────────────────────────────
    if not db.teacher_has_assignment(teacher_id, class_id, subject_id):
        return HttpResponseForbidden(
            '<h2>403 Forbidden</h2>'
            '<p>You are not assigned to this class or subject.</p>'
            '<a href="/teacher/dashboard/">Go back</a>'
        )
    # ────────────────────────────────────────────────────────

    cls = db.get_class(class_id)
    subject = db.get_subject(subject_id)
    students = db.get_students_by_class(class_id)
    students.sort(key=lambda s: s.get('roll_number', ''))

    today = dt_date.today().isoformat()
    selected_date = request.GET.get('date', today) or today

    # Check if attendance already exists for this date
    existing = db.find_existing_attendance(selected_date, teacher_id, class_id, subject_id)
    existing_map = {}
    if existing:
        for rec in existing.get('records', []):
            existing_map[rec['student_id']] = rec['status']

    if request.method == 'POST':
        selected_date = request.POST.get('date', today)
        records = []
        for student in students:
            status = request.POST.get(f'status_{student["id"]}', 'Absent')
            if status not in ('Present', 'Absent'):
                status = 'Absent'
            records.append({'student_id': student['id'], 'status': status})

        db.save_attendance(selected_date, teacher_id, class_id, subject_id, records)
        messages.success(request,
                         f'Attendance saved for {cls["name"]} — {subject["name"]} on {selected_date}.')
        return redirect('teacher_dashboard')

    ctx = {
        'cls': cls,
        'subject': subject,
        'students': students,
        'selected_date': selected_date,
        'existing_map': existing_map,
        'existing_map_json': json.dumps(existing_map),
        'is_edit': bool(existing),
        'today': today,
    }
    return render(request, 'attendance/teacher/mark_attendance.html', ctx)


# ─────────────────────────────────────────────
# My Attendance Records
# ─────────────────────────────────────────────

@teacher_required
def my_attendance_records(request):
    """Teacher views their own submitted attendance records."""
    teacher_id = _get_teacher_id(request)
    teacher = db.get_teacher(teacher_id)

    class_map = {c['id']: c['name'] for c in db.get_all_classes()}
    subject_map = {s['id']: s['name'] for s in db.get_all_subjects()}
    student_map = {s['id']: s for s in db.get_all_students()}

    # Filters
    f_class = request.GET.get('class_id', '').strip()
    f_subject = request.GET.get('subject_id', '').strip()
    f_date = request.GET.get('date', '').strip()

    records = db.get_attendance_by_filters(
        teacher_id=teacher_id,
        class_id=f_class or None,
        subject_id=f_subject or None,
        date=f_date or None,
    )

    enriched = []
    for att in records:
        present = sum(1 for r in att.get('records', []) if r.get('status') == 'Present')
        absent = len(att.get('records', [])) - present
        enriched.append({
            **att,
            'class_name': class_map.get(att.get('class_id', ''), 'Unknown'),
            'subject_name': subject_map.get(att.get('subject_id', ''), 'Unknown'),
            'present_count': present,
            'absent_count': absent,
            'total': len(att.get('records', [])),
        })

    enriched.sort(key=lambda r: r.get('date', ''), reverse=True)

    # Get only this teacher's assigned classes/subjects for filters
    assignments = _enrich_assignments(db.get_teacher_assignments(teacher_id))
    assigned_classes = {a['class_id']: a['class_name'] for a in assignments}
    assigned_subjects = {a['subject_id']: a['subject_name'] for a in assignments}

    ctx = {
        'teacher': teacher,
        'records': enriched,
        'assigned_classes': assigned_classes,
        'assigned_subjects': assigned_subjects,
        'f_class': f_class,
        'f_subject': f_subject,
        'f_date': f_date,
    }
    return render(request, 'attendance/teacher/my_records.html', ctx)


# ─────────────────────────────────────────────
# Attendance Detail (single session)
# ─────────────────────────────────────────────

@teacher_required
def attendance_detail(request, att_id):
    """View detailed student list for one attendance session."""
    teacher_id = _get_teacher_id(request)
    att = db.get_attendance_record(att_id)

    if not att:
        messages.error(request, 'Attendance record not found.')
        return redirect('my_attendance_records')

    # ── ACCESS CONTROL ──────────────────────────────────────
    if att.get('teacher_id') != teacher_id:
        return HttpResponseForbidden(
            '<h2>403 Forbidden</h2>'
            '<p>You cannot view another teacher\'s attendance records.</p>'
            '<a href="/teacher/dashboard/">Go back</a>'
        )
    # ────────────────────────────────────────────────────────

    student_map = {s['id']: s for s in db.get_all_students()}
    cls = db.get_class(att.get('class_id', ''))
    subject = db.get_subject(att.get('subject_id', ''))

    detail_records = []
    for rec in att.get('records', []):
        st = student_map.get(rec['student_id'], {})
        detail_records.append({
            'roll_number': st.get('roll_number', '-'),
            'name': st.get('name', 'Unknown'),
            'status': rec.get('status', 'Absent'),
        })
    detail_records.sort(key=lambda r: r['roll_number'])

    ctx = {
        'att': att,
        'cls': cls,
        'subject': subject,
        'detail_records': detail_records,
    }
    return render(request, 'attendance/teacher/attendance_detail.html', ctx)
