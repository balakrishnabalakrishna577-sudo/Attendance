"""
URL configuration for the attendance app.
All routes are namespaced under this single file.
"""

from django.urls import path
from attendance import views_auth, views_hod, views_teacher

urlpatterns = [

    # ── Auth ─────────────────────────────────────────────
    path('login/',    views_auth.login_view,      name='login'),
    path('logout/',   views_auth.logout_view,     name='logout'),
    path('dashboard/', views_auth.dashboard_router, name='dashboard'),

    # ── HOD ──────────────────────────────────────────────
    path('hod/dashboard/', views_hod.hod_dashboard, name='hod_dashboard'),

    # Teachers
    path('hod/teachers/',                     views_hod.teacher_list,   name='teacher_list'),
    path('hod/teachers/add/',                 views_hod.teacher_add,    name='teacher_add'),
    path('hod/teachers/<str:teacher_id>/edit/',   views_hod.teacher_edit,   name='teacher_edit'),
    path('hod/teachers/<str:teacher_id>/delete/', views_hod.teacher_delete, name='teacher_delete'),

    # Classes
    path('hod/classes/',                      views_hod.class_list,   name='class_list'),
    path('hod/classes/add/',                  views_hod.class_add,    name='class_add'),
    path('hod/classes/<str:class_id>/edit/',  views_hod.class_edit,   name='class_edit'),
    path('hod/classes/<str:class_id>/delete/', views_hod.class_delete, name='class_delete'),

    # Subjects
    path('hod/subjects/',                        views_hod.subject_list,   name='subject_list'),
    path('hod/subjects/add/',                    views_hod.subject_add,    name='subject_add'),
    path('hod/subjects/<str:subject_id>/edit/',  views_hod.subject_edit,   name='subject_edit'),
    path('hod/subjects/<str:subject_id>/delete/', views_hod.subject_delete, name='subject_delete'),

    # Students
    path('hod/students/',                        views_hod.student_list,   name='student_list'),
    path('hod/students/add/',                    views_hod.student_add,    name='student_add'),
    path('hod/students/import/',                 views_hod.student_import, name='student_import'),
    path('hod/students/<str:student_id>/edit/',  views_hod.student_edit,   name='student_edit'),
    path('hod/students/<str:student_id>/delete/', views_hod.student_delete, name='student_delete'),

    # Assignments
    path('hod/assignments/',                         views_hod.assignment_list,   name='assignment_list'),
    path('hod/assignments/add/',                     views_hod.assignment_add,    name='assignment_add'),
    path('hod/assignments/<str:assignment_id>/delete/', views_hod.assignment_delete, name='assignment_delete'),

    # Attendance Reports
    path('hod/reports/', views_hod.attendance_report, name='attendance_report'),

    # ── Teacher ──────────────────────────────────────────
    path('teacher/dashboard/', views_teacher.teacher_dashboard, name='teacher_dashboard'),

    path('teacher/attendance/<str:class_id>/<str:subject_id>/',
         views_teacher.mark_attendance, name='mark_attendance'),

    path('teacher/records/', views_teacher.my_attendance_records, name='my_attendance_records'),

    path('teacher/records/<str:att_id>/',
         views_teacher.attendance_detail, name='attendance_detail'),
]
