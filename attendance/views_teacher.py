"""
Teacher views — dashboard only.
Students, attendance marking, and attendance records have been removed.
"""

from datetime import date as dt_date
from django.shortcuts import render, redirect
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


@teacher_required
def teacher_dashboard(request):
    teacher_id = _get_teacher_id(request)
    teacher = db.get_teacher(teacher_id)
    if not teacher:
        messages.error(request, 'Teacher profile not found.')
        return redirect('logout')

    assignments = _enrich_assignments(db.get_teacher_assignments(teacher_id))

    ctx = {
        'teacher': teacher,
        'assignments': assignments,
        'today': dt_date.today().isoformat(),
    }
    return render(request, 'attendance/teacher/dashboard.html', ctx)
