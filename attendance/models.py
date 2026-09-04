"""
Django ORM models for features that need persistent storage across deploys.
Auth / teachers / classes still use JSON files (json_storage.py).
"""

from django.db import models


PROGRAMME_CHOICES = [
    ('UG', 'UG (Under Graduate)'),
    ('PG', 'PG (Post Graduate)'),
    ('BOTH', 'Both UG & PG'),
]

EVENT_TYPE_CHOICES = [
    ('academic', 'Academic'),
    ('exam', 'Exam / Test'),
    ('holiday', 'Holiday'),
    ('cultural', 'Cultural'),
    ('sports', 'Sports'),
    ('other', 'Other'),
]

MEETING_TYPE_CHOICES = [
    ('staff', 'Staff Meeting'),
    ('parent', 'Parent–Teacher Meeting'),
    ('department', 'Department Meeting'),
    ('other', 'Other'),
]

DAY_CHOICES = [
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
]

HOUR_CHOICES = [
    ('1', '1st Hour  (9:00–10:00 AM)'),
    ('2', '2nd Hour  (10:00–11:00 AM)'),
    ('3', '3rd Hour  (11:15 AM–12:15 PM)'),
    ('4', '4th Hour  (12:15–1:15 PM)'),
    ('5', '5th Hour  (2:00–3:00 PM)'),
    ('6', '6th Hour  (3:00–4:00 PM)'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
]

# ── Document categories ────────────────────────────────
DOC_CATEGORY_CHOICES = [
    ('circular',     'Circular'),
    ('notice',       'Notice'),
    ('minutes',      'Meeting Minutes'),
    ('report',       'Report'),
    ('policy',       'Policy'),
    ('syllabus',     'Syllabus'),
    ('result',       'Result'),
    ('other',        'Other'),
]


class AcademicEvent(models.Model):
    """Academic calendar events — HOD adds, visible to all teachers."""
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type  = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='academic')
    programme   = models.CharField(max_length=10, choices=PROGRAMME_CHOICES, default='BOTH')
    start_date  = models.DateField()
    end_date    = models.DateField(null=True, blank=True)
    academic_year = models.CharField(max_length=20, help_text='e.g. 2025-26')
    is_next_year  = models.BooleanField(default=False, help_text='Plan for next academic year')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return f"{self.title} ({self.programme}) — {self.start_date}"

    @property
    def duration_days(self):
        if self.end_date and self.end_date != self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 1


class Meeting(models.Model):
    """HOD schedules meetings — teachers can view."""
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='staff')
    meeting_date = models.DateField()
    meeting_time = models.TimeField()
    venue        = models.CharField(max_length=200, blank=True)
    programme    = models.CharField(max_length=10, choices=PROGRAMME_CHOICES, default='BOTH')
    # Comma-separated teacher IDs from JSON store; blank = all teachers
    invited_teachers = models.TextField(blank=True,
                                        help_text='Leave blank = all teachers')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['meeting_date', 'meeting_time']

    def __str__(self):
        return f"{self.title} on {self.meeting_date}"


class TeacherWorkAssignment(models.Model):
    """HOD assigns a task / work to a specific teacher."""
    teacher_id   = models.CharField(max_length=50,
                                    help_text='Teacher ID from teachers.json')
    teacher_name = models.CharField(max_length=200)   # denormalised for display
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    assigned_date = models.DateField()
    due_date      = models.DateField(null=True, blank=True)
    priority      = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks       = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-assigned_date', 'teacher_name']

    def __str__(self):
        return f"{self.title} → {self.teacher_name}"


class TimetableSlot(models.Model):
    """
    One slot in the timetable.
    HOD creates slots per section (class_id from JSON).
    Teachers see their own slots.
    """
    # References to JSON store — stored as char IDs
    class_id     = models.CharField(max_length=50)
    class_name   = models.CharField(max_length=200)   # denormalised
    teacher_id   = models.CharField(max_length=50)
    teacher_name = models.CharField(max_length=200)   # denormalised
    subject_id   = models.CharField(max_length=50)
    subject_name = models.CharField(max_length=200)   # denormalised

    day          = models.CharField(max_length=15, choices=DAY_CHOICES)
    hour         = models.CharField(max_length=5, choices=HOUR_CHOICES)
    start_time   = models.TimeField(null=True, blank=True)
    end_time     = models.TimeField(null=True, blank=True)
    room         = models.CharField(max_length=100, blank=True)
    academic_year = models.CharField(max_length=20, blank=True, default='2025-26')

    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['class_name', 'day', 'hour']
        unique_together = [['class_id', 'day', 'hour', 'academic_year']]

    def __str__(self):
        return f"{self.class_name} | {self.day} | {self.hour}hr | {self.subject_name}"


class OfficialDocument(models.Model):
    """Official documents uploaded by the HOD."""
    title       = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    category    = models.CharField(max_length=20,
                                   choices=DOC_CATEGORY_CHOICES,
                                   default='other')
    file        = models.FileField(upload_to='official_docs/')
    file_name   = models.CharField(max_length=300, blank=True)
    file_size   = models.PositiveIntegerField(default=0,
                                              help_text='Size in bytes')
    uploaded_by = models.CharField(max_length=200, default='HOD')
    academic_year = models.CharField(max_length=20, blank=True,
                                     default='2025-26')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

    @property
    def file_size_display(self):
        """Human-readable file size."""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/(1024*1024):.1f} MB"

    @property
    def file_ext(self):
        import os
        _, ext = os.path.splitext(self.file_name or str(self.file))
        return ext.lower().lstrip('.')


class ClassTeacher(models.Model):
    """
    Class Teacher assigned to a section by the HOD.
    One class teacher per class per academic year.
    """
    class_id      = models.CharField(max_length=50)
    class_name    = models.CharField(max_length=200)
    teacher_name  = models.CharField(max_length=200,
                                     help_text='Name of the class teacher')
    academic_year = models.CharField(max_length=20, default='2025-26')
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['class_id', 'academic_year']]
        ordering = ['class_name']

    def __str__(self):
        return f"{self.class_name} — {self.teacher_name} ({self.academic_year})"
