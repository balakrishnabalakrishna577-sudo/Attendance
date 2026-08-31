"""
Management command: python manage.py initdata

Creates:
- Default HOD account (admin / admin123)
- Sample classes, subjects, a teacher, and students
  so the system can be tested immediately after setup.
"""

from django.core.management.base import BaseCommand
from attendance.services import json_storage as db


class Command(BaseCommand):
    help = 'Initialize data files and create a default HOD + sample data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Clear ALL existing data before initializing.'
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting all data files…'))
            for fname in [db.USERS_FILE, db.TEACHERS_FILE, db.CLASSES_FILE,
                          db.SUBJECTS_FILE, db.STUDENTS_FILE,
                          db.ASSIGNMENTS_FILE, db.ATTENDANCE_FILE]:
                db.write_json(fname, [])

        # Ensure data files exist
        db.init_data_files()

        # ── HOD account ────────────────────────────────────────
        if not db.get_user_by_username('admin'):
            db.create_hod('admin', 'admin123', 'Head of Department')
            self.stdout.write(self.style.SUCCESS('✓ HOD account created: admin / admin123'))
        else:
            self.stdout.write('  HOD account already exists.')

        # ── Sample classes ─────────────────────────────────────
        classes = db.get_all_classes()
        if not classes:
            c1 = db.create_class('MCA 1st Year', 'Master of Computer Applications — Year 1')
            c2 = db.create_class('MCA 2nd Year', 'Master of Computer Applications — Year 2')
            c3 = db.create_class('BCA 1st Year', 'Bachelor of Computer Applications — Year 1')
            self.stdout.write(self.style.SUCCESS('✓ Sample classes created.'))
        else:
            c1 = classes[0]
            c2 = classes[1] if len(classes) > 1 else classes[0]
            c3 = classes[2] if len(classes) > 2 else classes[0]
            self.stdout.write('  Classes already exist.')

        # ── Sample subjects ────────────────────────────────────
        subjects = db.get_all_subjects()
        if not subjects:
            s1 = db.create_subject('Python Programming', 'MCA101', 'Core Python and OOP concepts')
            s2 = db.create_subject('Data Structures', 'MCA102', 'Arrays, lists, trees, graphs')
            s3 = db.create_subject('Database Management', 'MCA103', 'RDBMS concepts and SQL')
            s4 = db.create_subject('Web Technologies', 'BCA201', 'HTML, CSS, JavaScript basics')
            self.stdout.write(self.style.SUCCESS('✓ Sample subjects created.'))
        else:
            s1 = subjects[0]
            s2 = subjects[1] if len(subjects) > 1 else subjects[0]
            s3 = subjects[2] if len(subjects) > 2 else subjects[0]
            s4 = subjects[3] if len(subjects) > 3 else subjects[0]
            self.stdout.write('  Subjects already exist.')

        # ── Sample teacher ─────────────────────────────────────
        teachers = db.get_all_teachers()
        if not teachers:
            t1 = db.create_teacher(
                name='Dr. Priya Sharma',
                email='priya@college.edu',
                phone='9876543210',
                department='Computer Science',
                username='teacher1',
                password='teacher123',
            )
            t2 = db.create_teacher(
                name='Prof. Ravi Kumar',
                email='ravi@college.edu',
                phone='9876543211',
                department='Information Technology',
                username='teacher2',
                password='teacher123',
            )
            self.stdout.write(self.style.SUCCESS('✓ Sample teachers created: teacher1/teacher123, teacher2/teacher123'))
        else:
            t1 = teachers[0]
            t2 = teachers[1] if len(teachers) > 1 else teachers[0]
            self.stdout.write('  Teachers already exist.')

        # ── Sample students ────────────────────────────────────
        students = db.get_all_students()
        if not students:
            mca1_students = [
                ('01', 'Aarav Singh'),
                ('02', 'Meera Patel'),
                ('03', 'Rahul Verma'),
                ('04', 'Anjali Nair'),
                ('05', 'Kiran Reddy'),
            ]
            for roll, name in mca1_students:
                db.create_student(roll, name, c1['id'])

            bca1_students = [
                ('01', 'Rohan Gupta'),
                ('02', 'Sneha Iyer'),
                ('03', 'Amit Kumar'),
            ]
            for roll, name in bca1_students:
                db.create_student(roll, name, c3['id'])

            self.stdout.write(self.style.SUCCESS('✓ Sample students created.'))
        else:
            self.stdout.write('  Students already exist.')

        # ── Sample assignments ─────────────────────────────────
        assignments = db.get_all_assignments()
        if not assignments:
            db.create_assignment(t1['id'], c1['id'], s1['id'])  # teacher1 → MCA1 → Python
            db.create_assignment(t1['id'], c1['id'], s2['id'])  # teacher1 → MCA1 → DS
            db.create_assignment(t2['id'], c2['id'], s3['id'])  # teacher2 → MCA2 → DBMS
            db.create_assignment(t2['id'], c3['id'], s4['id'])  # teacher2 → BCA1 → Web Tech
            self.stdout.write(self.style.SUCCESS('✓ Sample assignments created.'))
        else:
            self.stdout.write('  Assignments already exist.')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Setup complete! You can now run the server.'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('  HOD Login     → username: admin       password: admin123')
        self.stdout.write('  Teacher Login → username: teacher1    password: teacher123')
        self.stdout.write('  Teacher Login → username: teacher2    password: teacher123')
        self.stdout.write('')
