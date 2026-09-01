"""
Extra views: Academic Events, Meetings, Teacher Work Assignments, Timetable.
HOD views are decorated with @hod_required.
Teacher views are decorated with @teacher_required.
"""

import json
from datetime import date as dt_date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from attendance.decorators import hod_required, teacher_required
from attendance.services import json_storage as db
from attendance.models import (
    AcademicEvent, Meeting, TeacherWorkAssignment, TimetableSlot
)


# ══════════════════════════════════════════════════════════
# ── ACADEMIC EVENTS ────────────────────────────────────────
# ══════════════════════════════════════════════════════════

@hod_required
def event_list(request):
    programme = request.GET.get('programme', '')
    year      = request.GET.get('year', '')
    next_year = request.GET.get('next_year', '')
    etype     = request.GET.get('event_type', '')

    events = AcademicEvent.objects.all()
    if programme:
        events = events.filter(Q(programme=programme) | Q(programme='BOTH'))
    if year:
        events = events.filter(academic_year=year)
    if next_year == '1':
        events = events.filter(is_next_year=True)
    if etype:
        events = events.filter(event_type=etype)

    # Distinct years in DB for filter dropdown
    years = AcademicEvent.objects.values_list('academic_year', flat=True).distinct().order_by('academic_year')

    ctx = {
        'events': events,
        'years': years,
        'f_programme': programme,
        'f_year': year,
        'f_next_year': next_year,
        'f_etype': etype,
        'programme_choices': AcademicEvent._meta.get_field('programme').choices,
        'event_type_choices': AcademicEvent._meta.get_field('event_type').choices,
    }
    return render(request, 'attendance/hod/event_list.html', ctx)


@hod_required
def event_add(request):
    if request.method == 'POST':
        title         = request.POST.get('title', '').strip()
        description   = request.POST.get('description', '').strip()
        event_type    = request.POST.get('event_type', 'academic')
        programme     = request.POST.get('programme', 'BOTH')
        start_date    = request.POST.get('start_date', '').strip()
        end_date      = request.POST.get('end_date', '').strip() or None
        academic_year = request.POST.get('academic_year', '').strip()
        is_next_year  = request.POST.get('is_next_year') == '1'

        if not all([title, start_date, academic_year]):
            messages.error(request, 'Title, start date and academic year are required.')
            return render(request, 'attendance/hod/event_form.html', _event_ctx())

        AcademicEvent.objects.create(
            title=title, description=description, event_type=event_type,
            programme=programme, start_date=start_date, end_date=end_date,
            academic_year=academic_year, is_next_year=is_next_year,
        )
        messages.success(request, f'Event "{title}" added.')
        return redirect('event_list')

    return render(request, 'attendance/hod/event_form.html', _event_ctx())


@hod_required
def event_edit(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    if request.method == 'POST':
        event.title         = request.POST.get('title', '').strip()
        event.description   = request.POST.get('description', '').strip()
        event.event_type    = request.POST.get('event_type', 'academic')
        event.programme     = request.POST.get('programme', 'BOTH')
        event.start_date    = request.POST.get('start_date')
        event.end_date      = request.POST.get('end_date') or None
        event.academic_year = request.POST.get('academic_year', '').strip()
        event.is_next_year  = request.POST.get('is_next_year') == '1'

        if not all([event.title, event.start_date, event.academic_year]):
            messages.error(request, 'Title, start date and academic year are required.')
            return render(request, 'attendance/hod/event_form.html', _event_ctx(event))

        event.save()
        messages.success(request, 'Event updated.')
        return redirect('event_list')

    return render(request, 'attendance/hod/event_form.html', _event_ctx(event))


@hod_required
def event_delete(request, pk):
    event = get_object_or_404(AcademicEvent, pk=pk)
    if request.method == 'POST':
        name = event.title
        event.delete()
        messages.success(request, f'Event "{name}" deleted.')
        return redirect('event_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': event.title, 'cancel_url': 'event_list'})


def _event_ctx(event=None):
    return {
        'event': event,
        'programme_choices': AcademicEvent._meta.get_field('programme').choices,
        'event_type_choices': AcademicEvent._meta.get_field('event_type').choices,
        'today': dt_date.today().isoformat(),
    }


# ══════════════════════════════════════════════════════════
# ── MEETINGS ───────────────────────────────────────────────
# ══════════════════════════════════════════════════════════

@hod_required
def meeting_list(request):
    f_programme = request.GET.get('programme', '')
    f_type      = request.GET.get('meeting_type', '')
    f_upcoming  = request.GET.get('upcoming', '')

    meetings = Meeting.objects.all()
    if f_programme:
        meetings = meetings.filter(Q(programme=f_programme) | Q(programme='BOTH'))
    if f_type:
        meetings = meetings.filter(meeting_type=f_type)
    if f_upcoming == '1':
        meetings = meetings.filter(meeting_date__gte=dt_date.today())

    ctx = {
        'meetings': meetings,
        'f_programme': f_programme,
        'f_type': f_type,
        'f_upcoming': f_upcoming,
        'programme_choices': Meeting._meta.get_field('programme').choices,
        'meeting_type_choices': Meeting._meta.get_field('meeting_type').choices,
    }
    return render(request, 'attendance/hod/meeting_list.html', ctx)


@hod_required
def meeting_add(request):
    teachers = db.get_all_teachers()
    if request.method == 'POST':
        title        = request.POST.get('title', '').strip()
        description  = request.POST.get('description', '').strip()
        meeting_type = request.POST.get('meeting_type', 'staff')
        meeting_date = request.POST.get('meeting_date', '').strip()
        meeting_time = request.POST.get('meeting_time', '').strip()
        venue        = request.POST.get('venue', '').strip()
        programme    = request.POST.get('programme', 'BOTH')
        invited      = ','.join(request.POST.getlist('invited_teachers'))

        if not all([title, meeting_date, meeting_time]):
            messages.error(request, 'Title, date and time are required.')
            return render(request, 'attendance/hod/meeting_form.html',
                          {'teachers': teachers, **_meeting_ctx()})

        Meeting.objects.create(
            title=title, description=description, meeting_type=meeting_type,
            meeting_date=meeting_date, meeting_time=meeting_time,
            venue=venue, programme=programme, invited_teachers=invited,
        )
        messages.success(request, f'Meeting "{title}" scheduled.')
        return redirect('meeting_list')

    return render(request, 'attendance/hod/meeting_form.html',
                  {'teachers': teachers, **_meeting_ctx()})


@hod_required
def meeting_edit(request, pk):
    meeting  = get_object_or_404(Meeting, pk=pk)
    teachers = db.get_all_teachers()
    invited_list = meeting.invited_teachers.split(',') if meeting.invited_teachers else []

    if request.method == 'POST':
        meeting.title        = request.POST.get('title', '').strip()
        meeting.description  = request.POST.get('description', '').strip()
        meeting.meeting_type = request.POST.get('meeting_type', 'staff')
        meeting.meeting_date = request.POST.get('meeting_date')
        meeting.meeting_time = request.POST.get('meeting_time')
        meeting.venue        = request.POST.get('venue', '').strip()
        meeting.programme    = request.POST.get('programme', 'BOTH')
        meeting.invited_teachers = ','.join(request.POST.getlist('invited_teachers'))

        if not all([meeting.title, meeting.meeting_date, meeting.meeting_time]):
            messages.error(request, 'Title, date and time are required.')
            return render(request, 'attendance/hod/meeting_form.html',
                          {'teachers': teachers, 'meeting': meeting,
                           'invited_list': invited_list, **_meeting_ctx()})
        meeting.save()
        messages.success(request, 'Meeting updated.')
        return redirect('meeting_list')

    return render(request, 'attendance/hod/meeting_form.html',
                  {'teachers': teachers, 'meeting': meeting,
                   'invited_list': invited_list, **_meeting_ctx()})


@hod_required
def meeting_delete(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    if request.method == 'POST':
        name = meeting.title
        meeting.delete()
        messages.success(request, f'Meeting "{name}" deleted.')
        return redirect('meeting_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': meeting.title, 'cancel_url': 'meeting_list'})


def _meeting_ctx():
    return {
        'programme_choices': Meeting._meta.get_field('programme').choices,
        'meeting_type_choices': Meeting._meta.get_field('meeting_type').choices,
        'today': dt_date.today().isoformat(),
    }


# ══════════════════════════════════════════════════════════
# ── TEACHER WORK ASSIGNMENTS ───────────────────────────────
# ══════════════════════════════════════════════════════════

@hod_required
def work_assignment_list(request):
    f_teacher  = request.GET.get('teacher_id', '')
    f_status   = request.GET.get('status', '')
    f_priority = request.GET.get('priority', '')

    works = TeacherWorkAssignment.objects.all()
    if f_teacher:
        works = works.filter(teacher_id=f_teacher)
    if f_status:
        works = works.filter(status=f_status)
    if f_priority:
        works = works.filter(priority=f_priority)

    teachers = db.get_all_teachers()
    ctx = {
        'works': works,
        'teachers': teachers,
        'f_teacher': f_teacher,
        'f_status': f_status,
        'f_priority': f_priority,
        'status_choices': TeacherWorkAssignment._meta.get_field('status').choices,
        'priority_choices': TeacherWorkAssignment._meta.get_field('priority').choices,
    }
    return render(request, 'attendance/hod/work_assignment_list.html', ctx)


@hod_required
def work_assignment_add(request):
    teachers = db.get_all_teachers()
    if request.method == 'POST':
        teacher_id    = request.POST.get('teacher_id', '').strip()
        title         = request.POST.get('title', '').strip()
        description   = request.POST.get('description', '').strip()
        assigned_date = request.POST.get('assigned_date', '').strip()
        due_date      = request.POST.get('due_date', '').strip() or None
        priority      = request.POST.get('priority', 'medium')
        status        = request.POST.get('status', 'pending')
        remarks       = request.POST.get('remarks', '').strip()

        if not all([teacher_id, title, assigned_date]):
            messages.error(request, 'Teacher, title and assigned date are required.')
            return render(request, 'attendance/hod/work_assignment_form.html',
                          _work_ctx(teachers))

        teacher = db.get_teacher(teacher_id)
        teacher_name = teacher['name'] if teacher else teacher_id

        TeacherWorkAssignment.objects.create(
            teacher_id=teacher_id, teacher_name=teacher_name,
            title=title, description=description,
            assigned_date=assigned_date, due_date=due_date,
            priority=priority, status=status, remarks=remarks,
        )
        messages.success(request, f'Work assignment "{title}" assigned to {teacher_name}.')
        return redirect('work_assignment_list')

    return render(request, 'attendance/hod/work_assignment_form.html', _work_ctx(teachers))


@hod_required
def work_assignment_edit(request, pk):
    work     = get_object_or_404(TeacherWorkAssignment, pk=pk)
    teachers = db.get_all_teachers()

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id', '').strip()
        teacher    = db.get_teacher(teacher_id)

        work.teacher_id    = teacher_id
        work.teacher_name  = teacher['name'] if teacher else teacher_id
        work.title         = request.POST.get('title', '').strip()
        work.description   = request.POST.get('description', '').strip()
        work.assigned_date = request.POST.get('assigned_date')
        work.due_date      = request.POST.get('due_date') or None
        work.priority      = request.POST.get('priority', 'medium')
        work.status        = request.POST.get('status', 'pending')
        work.remarks       = request.POST.get('remarks', '').strip()

        if not all([work.teacher_id, work.title, work.assigned_date]):
            messages.error(request, 'Teacher, title and assigned date are required.')
            return render(request, 'attendance/hod/work_assignment_form.html',
                          {**_work_ctx(teachers), 'work': work})

        work.save()
        messages.success(request, 'Work assignment updated.')
        return redirect('work_assignment_list')

    return render(request, 'attendance/hod/work_assignment_form.html',
                  {**_work_ctx(teachers), 'work': work})


@hod_required
def work_assignment_delete(request, pk):
    work = get_object_or_404(TeacherWorkAssignment, pk=pk)
    if request.method == 'POST':
        name = work.title
        work.delete()
        messages.success(request, f'Work assignment "{name}" deleted.')
        return redirect('work_assignment_list')
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': work.title, 'cancel_url': 'work_assignment_list'})


@hod_required
def teacher_profile(request, teacher_id):
    """HOD view: full profile of one teacher — assignments, work tasks, timetable."""
    teacher = db.get_teacher(teacher_id)
    if not teacher:
        messages.error(request, 'Teacher not found.')
        return redirect('teacher_list')

    # JSON-based data
    assignments = db.get_teacher_assignments(teacher_id)
    class_map   = {c['id']: c for c in db.get_all_classes()}
    subject_map = {s['id']: s for s in db.get_all_subjects()}
    for a in assignments:
        a['class_name']   = class_map.get(a.get('class_id'), {}).get('name', '?')
        a['subject_name'] = subject_map.get(a.get('subject_id'), {}).get('name', '?')
        a['subject_code'] = subject_map.get(a.get('subject_id'), {}).get('code', '')

    # SQLite-based data
    works = TeacherWorkAssignment.objects.filter(teacher_id=teacher_id).order_by('-assigned_date')
    timetable = TimetableSlot.objects.filter(teacher_id=teacher_id).order_by('day', 'hour')

    # Attendance summary from JSON
    all_att = db.get_attendance_by_filters(teacher_id=teacher_id)
    total_sessions = len(all_att)
    total_students_marked = sum(len(a.get('records', [])) for a in all_att)

    ctx = {
        'teacher': teacher,
        'assignments': assignments,
        'works': works,
        'timetable': timetable,
        'total_sessions': total_sessions,
        'total_students_marked': total_students_marked,
        'status_choices': dict(TeacherWorkAssignment._meta.get_field('status').choices),
        'priority_choices': dict(TeacherWorkAssignment._meta.get_field('priority').choices),
    }
    return render(request, 'attendance/hod/teacher_profile.html', ctx)


def _work_ctx(teachers):
    return {
        'teachers': teachers,
        'status_choices': TeacherWorkAssignment._meta.get_field('status').choices,
        'priority_choices': TeacherWorkAssignment._meta.get_field('priority').choices,
        'today': dt_date.today().isoformat(),
    }


# ══════════════════════════════════════════════════════════
# ── TIMETABLE — HOD ────────────────────────────────────────
# ══════════════════════════════════════════════════════════

@hod_required
def timetable_sections(request):
    """Show all sections (classes). Click one to see its timetable."""
    classes = db.get_all_classes()
    # Count slots per class
    slot_counts = {}
    for cls in classes:
        slot_counts[cls['id']] = TimetableSlot.objects.filter(class_id=cls['id']).count()

    ctx = {
        'classes': classes,
        'slot_counts': slot_counts,
        'slot_counts_json': json.dumps(slot_counts),
    }
    return render(request, 'attendance/hod/timetable_sections.html', ctx)


@hod_required
def timetable_view(request, class_id):
    """Display timetable grid for one section."""
    cls = db.get_class(class_id)
    if not cls:
        messages.error(request, 'Class not found.')
        return redirect('timetable_sections')

    year = request.GET.get('year', '2025-26')
    slots = TimetableSlot.objects.filter(class_id=class_id, academic_year=year)

    # Build grid: {day: {hour: slot}}
    days  = [d[0] for d in TimetableSlot._meta.get_field('day').choices]
    hours = [h[0] for h in TimetableSlot._meta.get_field('hour').choices]
    grid  = {day: {hour: None for hour in hours} for day in days}
    for slot in slots:
        grid[slot.day][slot.hour] = slot

    # Distinct years for filter
    years = TimetableSlot.objects.values_list('academic_year', flat=True).distinct()

    ctx = {
        'cls': cls,
        'grid': grid,
        'days': days,
        'hours': hours,
        'slots': slots,
        'year': year,
        'years': years,
    }
    return render(request, 'attendance/hod/timetable_view.html', ctx)


@hod_required
def timetable_slot_add(request, class_id):
    cls = db.get_class(class_id)
    if not cls:
        messages.error(request, 'Class not found.')
        return redirect('timetable_sections')

    teachers = db.get_all_teachers()
    subjects = db.get_all_subjects()

    if request.method == 'POST':
        teacher_id   = request.POST.get('teacher_id', '').strip()
        subject_id   = request.POST.get('subject_id', '').strip()
        day          = request.POST.get('day', '').strip()
        hour         = request.POST.get('hour', '').strip()
        start_time   = request.POST.get('start_time', '').strip() or None
        end_time     = request.POST.get('end_time', '').strip() or None
        room         = request.POST.get('room', '').strip()
        academic_year = request.POST.get('academic_year', '2025-26').strip()

        if not all([teacher_id, subject_id, day, hour]):
            messages.error(request, 'Teacher, subject, day and hour are required.')
            return render(request, 'attendance/hod/timetable_slot_form.html',
                          _slot_ctx(cls, teachers, subjects))

        teacher = db.get_teacher(teacher_id)
        subject = db.get_subject(subject_id)

        # Check duplicate
        if TimetableSlot.objects.filter(
                class_id=class_id, day=day, hour=hour, academic_year=academic_year).exists():
            messages.error(request, f'{day} — Hour {hour} is already assigned for this class.')
            return render(request, 'attendance/hod/timetable_slot_form.html',
                          _slot_ctx(cls, teachers, subjects))

        TimetableSlot.objects.create(
            class_id=class_id, class_name=cls['name'],
            teacher_id=teacher_id, teacher_name=teacher['name'] if teacher else teacher_id,
            subject_id=subject_id, subject_name=subject['name'] if subject else subject_id,
            day=day, hour=hour,
            start_time=start_time, end_time=end_time,
            room=room, academic_year=academic_year,
        )
        messages.success(request, f'Slot added: {day} — Hour {hour}.')
        return redirect('timetable_view', class_id=class_id)

    return render(request, 'attendance/hod/timetable_slot_form.html',
                  _slot_ctx(cls, teachers, subjects))


@hod_required
def timetable_slot_edit(request, pk):
    slot     = get_object_or_404(TimetableSlot, pk=pk)
    cls      = db.get_class(slot.class_id)
    teachers = db.get_all_teachers()
    subjects = db.get_all_subjects()

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id', '').strip()
        subject_id = request.POST.get('subject_id', '').strip()
        teacher    = db.get_teacher(teacher_id)
        subject    = db.get_subject(subject_id)

        slot.teacher_id   = teacher_id
        slot.teacher_name = teacher['name'] if teacher else teacher_id
        slot.subject_id   = subject_id
        slot.subject_name = subject['name'] if subject else subject_id
        slot.day          = request.POST.get('day', slot.day)
        slot.hour         = request.POST.get('hour', slot.hour)
        slot.start_time   = request.POST.get('start_time') or None
        slot.end_time     = request.POST.get('end_time') or None
        slot.room         = request.POST.get('room', '').strip()
        slot.academic_year = request.POST.get('academic_year', '2025-26').strip()
        slot.save()
        messages.success(request, 'Slot updated.')
        return redirect('timetable_view', class_id=slot.class_id)

    return render(request, 'attendance/hod/timetable_slot_form.html',
                  {**_slot_ctx(cls, teachers, subjects), 'slot': slot})


@hod_required
def timetable_slot_delete(request, pk):
    slot = get_object_or_404(TimetableSlot, pk=pk)
    class_id = slot.class_id
    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Slot removed.')
        return redirect('timetable_view', class_id=class_id)
    return render(request, 'attendance/hod/confirm_delete.html',
                  {'item': f'{slot.day} Hour {slot.hour} — {slot.subject_name}',
                   'cancel_url': None,
                   'back_url': f'/hod/timetable/{class_id}/'})


def _slot_ctx(cls, teachers, subjects):
    return {
        'cls': cls,
        'teachers': teachers,
        'subjects': subjects,
        'day_choices': TimetableSlot._meta.get_field('day').choices,
        'hour_choices': TimetableSlot._meta.get_field('hour').choices,
    }


# ══════════════════════════════════════════════════════════
# ── TEACHER VIEWS ──────────────────────────────────────────
# ══════════════════════════════════════════════════════════

@teacher_required
def teacher_events(request):
    """Teacher views academic events relevant to their programme."""
    today = dt_date.today()
    events = AcademicEvent.objects.filter(
        start_date__gte=today
    ).order_by('start_date')

    past = AcademicEvent.objects.filter(
        start_date__lt=today
    ).order_by('-start_date')[:20]

    ctx = {'events': events, 'past': past, 'today': today}
    return render(request, 'attendance/teacher/events.html', ctx)


@teacher_required
def teacher_meetings(request):
    """Teacher views meetings they are invited to (or all if no invite list)."""
    teacher_id = request.session.get('teacher_id', '')
    today = dt_date.today()

    upcoming = Meeting.objects.filter(meeting_date__gte=today).order_by('meeting_date', 'meeting_time')
    past     = Meeting.objects.filter(meeting_date__lt=today).order_by('-meeting_date')[:10]

    # Filter to meetings this teacher is invited to (or all-teachers meetings)
    def is_invited(m):
        if not m.invited_teachers:
            return True   # blank = all teachers
        return teacher_id in m.invited_teachers.split(',')

    upcoming = [m for m in upcoming if is_invited(m)]
    past     = [m for m in past if is_invited(m)]

    ctx = {'upcoming': upcoming, 'past': past, 'today': today}
    return render(request, 'attendance/teacher/meetings.html', ctx)


@teacher_required
def teacher_work_assignments(request):
    """Teacher views their own work assignments."""
    teacher_id = request.session.get('teacher_id', '')
    works = TeacherWorkAssignment.objects.filter(
        teacher_id=teacher_id
    ).order_by('-assigned_date')

    f_status = request.GET.get('status', '')
    if f_status:
        works = works.filter(status=f_status)

    ctx = {
        'works': works,
        'f_status': f_status,
        'status_choices': TeacherWorkAssignment._meta.get_field('status').choices,
        'priority_choices': dict(TeacherWorkAssignment._meta.get_field('priority').choices),
    }
    return render(request, 'attendance/teacher/work_assignments.html', ctx)


@teacher_required
def teacher_timetable(request):
    """Teacher views their own timetable slots."""
    teacher_id = request.session.get('teacher_id', '')
    year = request.GET.get('year', '2025-26')

    slots  = TimetableSlot.objects.filter(teacher_id=teacher_id, academic_year=year)
    days   = [d[0] for d in TimetableSlot._meta.get_field('day').choices]
    hours  = [h[0] for h in TimetableSlot._meta.get_field('hour').choices]

    # Grid per class-section
    # Group by class
    class_ids = slots.values_list('class_id', flat=True).distinct()
    grids = {}
    for cid in class_ids:
        grid = {day: {hour: None for hour in hours} for day in days}
        for slot in slots.filter(class_id=cid):
            grid[slot.day][slot.hour] = slot
        grids[cid] = {
            'class_name': slots.filter(class_id=cid).first().class_name,
            'grid': grid,
        }

    years = TimetableSlot.objects.filter(
        teacher_id=teacher_id).values_list('academic_year', flat=True).distinct()

    ctx = {
        'grids': grids,
        'days': days,
        'hours': hours,
        'year': year,
        'years': years,
        'slots': slots,
    }
    return render(request, 'attendance/teacher/timetable.html', ctx)
