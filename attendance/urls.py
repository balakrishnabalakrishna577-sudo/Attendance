"""
URL configuration for the attendance app.
"""

from django.urls import path
from attendance import views_auth, views_hod, views_teacher, views_extra

urlpatterns = [

    # ── Auth ─────────────────────────────────────────────
    path('login/',     views_auth.login_view,       name='login'),
    path('logout/',    views_auth.logout_view,       name='logout'),
    path('dashboard/', views_auth.dashboard_router,  name='dashboard'),

    # ── HOD ──────────────────────────────────────────────
    path('hod/dashboard/', views_hod.hod_dashboard, name='hod_dashboard'),

    # Teachers
    path('hod/teachers/',                              views_hod.teacher_list,   name='teacher_list'),
    path('hod/teachers/add/',                          views_hod.teacher_add,    name='teacher_add'),
    path('hod/teachers/<str:teacher_id>/edit/',        views_hod.teacher_edit,   name='teacher_edit'),
    path('hod/teachers/<str:teacher_id>/delete/',      views_hod.teacher_delete, name='teacher_delete'),
    path('hod/teachers/<str:teacher_id>/profile/',     views_extra.teacher_profile, name='teacher_profile'),

    # Classes
    path('hod/classes/',                               views_hod.class_list,    name='class_list'),
    path('hod/classes/add/',                           views_hod.class_add,     name='class_add'),
    path('hod/classes/<str:class_id>/edit/',           views_hod.class_edit,    name='class_edit'),
    path('hod/classes/<str:class_id>/delete/',         views_hod.class_delete,  name='class_delete'),

    # Subjects
    path('hod/subjects/',                              views_hod.subject_list,   name='subject_list'),
    path('hod/subjects/add/',                          views_hod.subject_add,    name='subject_add'),
    path('hod/subjects/<str:subject_id>/edit/',        views_hod.subject_edit,   name='subject_edit'),
    path('hod/subjects/<str:subject_id>/delete/',      views_hod.subject_delete, name='subject_delete'),

    # Students
    path('hod/students/',                              views_hod.student_list,   name='student_list'),
    path('hod/students/add/',                          views_hod.student_add,    name='student_add'),
    path('hod/students/import/',                       views_hod.student_import, name='student_import'),
    path('hod/students/<str:student_id>/edit/',        views_hod.student_edit,   name='student_edit'),
    path('hod/students/<str:student_id>/delete/',      views_hod.student_delete, name='student_delete'),

    # Assignments (teacher→class→subject)
    path('hod/assignments/',                               views_hod.assignment_list,   name='assignment_list'),
    path('hod/assignments/add/',                           views_hod.assignment_add,    name='assignment_add'),
    path('hod/assignments/<str:assignment_id>/delete/',    views_hod.assignment_delete, name='assignment_delete'),

    # Attendance Reports
    path('hod/reports/', views_hod.attendance_report, name='attendance_report'),

    # ── Academic Events ───────────────────────────────────
    path('hod/events/',                         views_extra.event_list,   name='event_list'),
    path('hod/events/add/',                     views_extra.event_add,    name='event_add'),
    path('hod/events/<int:pk>/edit/',           views_extra.event_edit,   name='event_edit'),
    path('hod/events/<int:pk>/delete/',         views_extra.event_delete, name='event_delete'),

    # ── Meetings ──────────────────────────────────────────
    path('hod/meetings/',                       views_extra.meeting_list,   name='meeting_list'),
    path('hod/meetings/add/',                   views_extra.meeting_add,    name='meeting_add'),
    path('hod/meetings/<int:pk>/edit/',         views_extra.meeting_edit,   name='meeting_edit'),
    path('hod/meetings/<int:pk>/delete/',       views_extra.meeting_delete, name='meeting_delete'),

    # ── Teacher Work Assignments ──────────────────────────
    path('hod/work/',                           views_extra.work_assignment_list,   name='work_assignment_list'),
    path('hod/work/add/',                       views_extra.work_assignment_add,    name='work_assignment_add'),
    path('hod/work/<int:pk>/edit/',             views_extra.work_assignment_edit,   name='work_assignment_edit'),
    path('hod/work/<int:pk>/delete/',           views_extra.work_assignment_delete, name='work_assignment_delete'),

    # ── Timetable (HOD) ───────────────────────────────────
    path('hod/timetable/',                              views_extra.timetable_sections,   name='timetable_sections'),
    path('hod/timetable/<str:class_id>/',               views_extra.timetable_view,       name='timetable_view'),
    path('hod/timetable/<str:class_id>/add/',           views_extra.timetable_slot_add,   name='timetable_slot_add'),
    path('hod/timetable/slot/<int:pk>/edit/',           views_extra.timetable_slot_edit,  name='timetable_slot_edit'),
    path('hod/timetable/slot/<int:pk>/delete/',         views_extra.timetable_slot_delete,name='timetable_slot_delete'),

    # ── Teacher ───────────────────────────────────────────
    path('teacher/dashboard/',   views_teacher.teacher_dashboard,      name='teacher_dashboard'),
    path('teacher/attendance/<str:class_id>/<str:subject_id>/',
                                 views_teacher.mark_attendance,         name='mark_attendance'),
    path('teacher/records/',     views_teacher.my_attendance_records,   name='my_attendance_records'),
    path('teacher/records/<str:att_id>/',
                                 views_teacher.attendance_detail,       name='attendance_detail'),

    # Teacher — new features
    path('teacher/events/',      views_extra.teacher_events,            name='teacher_events'),
    path('teacher/meetings/',    views_extra.teacher_meetings,          name='teacher_meetings'),
    path('teacher/work/',        views_extra.teacher_work_assignments,  name='teacher_work_assignments'),
    path('teacher/timetable/',   views_extra.teacher_timetable,         name='teacher_timetable'),
]
