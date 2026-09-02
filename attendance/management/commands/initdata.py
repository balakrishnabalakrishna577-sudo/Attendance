"""
Management command: python manage.py initdata

Creates only the HOD account (Naveen / Naveen@2006).
All other data (teachers, classes, subjects, students, assignments)
is added by the HOD through the dashboard.
"""

from django.core.management.base import BaseCommand
from attendance.services import json_storage as db


class Command(BaseCommand):
    help = 'Initialize data files and create the HOD account.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Clear ALL existing data before initializing.'
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting all data files…'))
            for fname in [db.USERS_FILE, db.TEACHERS_FILE, db.CLASSES_FILE,
                          db.SUBJECTS_FILE, db.ASSIGNMENTS_FILE]:
                db.write_json(fname, [])

        # Ensure all data files exist (creates empty files if missing)
        db.init_data_files()

        # ── HOD account ────────────────────────────────────────
        if not db.get_user_by_username('Naveen'):
            db.create_hod('Naveen', 'Naveen@2006', 'Naveen')
            self.stdout.write(self.style.SUCCESS('✓ HOD account created: Naveen / Naveen@2006'))
        else:
            self.stdout.write('  HOD account already exists.')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Setup complete! You can now run the server.'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('  HOD Login → username: Naveen   password: Naveen@2006')
        self.stdout.write('')
