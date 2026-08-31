"""
JSON File Storage Service
Handles all read/write operations for JSON data files.
No database is used — all data persists in the data/ directory.
"""

import json
import os
import uuid
import threading
from datetime import datetime
from django.conf import settings

# Thread lock to prevent race conditions on concurrent writes
_file_locks = {}
_lock_registry = threading.Lock()


def _get_lock(filename: str) -> threading.Lock:
    """Return (or create) a per-file lock."""
    with _lock_registry:
        if filename not in _file_locks:
            _file_locks[filename] = threading.Lock()
        return _file_locks[filename]


def _get_path(filename: str) -> str:
    """Return the absolute path for a data file."""
    return os.path.join(settings.DATA_DIR, filename)


def read_json(filename: str) -> list:
    """Read a JSON file and return its contents as a list. Creates file if missing."""
    path = _get_path(filename)
    lock = _get_lock(filename)
    with lock:
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return []
        with open(path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, ValueError):
                return []


def write_json(filename: str, data: list) -> None:
    """Write a list to a JSON file, overwriting existing content."""
    path = _get_path(filename)
    lock = _get_lock(filename)
    with lock:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def generate_id(prefix: str = '') -> str:
    """Generate a unique ID with an optional prefix (e.g., 'T', 'C', 'S')."""
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


# ──────────────────────────────────────────────
# Generic CRUD helpers
# ──────────────────────────────────────────────

def get_all(filename: str) -> list:
    return read_json(filename)


def get_by_id(filename: str, record_id: str) -> dict | None:
    records = read_json(filename)
    for r in records:
        if r.get('id') == record_id:
            return r
    return None


def create_record(filename: str, data: dict) -> dict:
    """Insert a new record. Adds 'created_at' timestamp automatically."""
    records = read_json(filename)
    data['created_at'] = datetime.now().isoformat()
    records.append(data)
    write_json(filename, records)
    return data


def update_record(filename: str, record_id: str, updates: dict) -> dict | None:
    """Update fields of a record identified by id."""
    records = read_json(filename)
    for i, r in enumerate(records):
        if r.get('id') == record_id:
            records[i].update(updates)
            records[i]['updated_at'] = datetime.now().isoformat()
            write_json(filename, records)
            return records[i]
    return None


def delete_record(filename: str, record_id: str) -> bool:
    """Delete a record by id. Returns True if deleted."""
    records = read_json(filename)
    new_records = [r for r in records if r.get('id') != record_id]
    if len(new_records) == len(records):
        return False
    write_json(filename, new_records)
    return True


def find_by_field(filename: str, field: str, value) -> list:
    """Return all records where record[field] == value."""
    return [r for r in read_json(filename) if r.get(field) == value]


def find_one_by_field(filename: str, field: str, value) -> dict | None:
    """Return the first record where record[field] == value."""
    for r in read_json(filename):
        if r.get(field) == value:
            return r
    return None


# ──────────────────────────────────────────────
# File names (constants)
# ──────────────────────────────────────────────
USERS_FILE = 'users.json'
TEACHERS_FILE = 'teachers.json'
CLASSES_FILE = 'classes.json'
SUBJECTS_FILE = 'subjects.json'
STUDENTS_FILE = 'students.json'
ASSIGNMENTS_FILE = 'assignments.json'
ATTENDANCE_FILE = 'attendance.json'


def init_data_files():
    """Ensure all data files exist with empty arrays."""
    for fname in [USERS_FILE, TEACHERS_FILE, CLASSES_FILE, SUBJECTS_FILE,
                  STUDENTS_FILE, ASSIGNMENTS_FILE, ATTENDANCE_FILE]:
        read_json(fname)  # creates file if missing


# ──────────────────────────────────────────────
# User helpers
# ──────────────────────────────────────────────

from django.contrib.auth.hashers import make_password, check_password


def get_user_by_username(username: str) -> dict | None:
    return find_one_by_field(USERS_FILE, 'username', username)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password(plain, hashed)


def create_hod(username: str, password: str, name: str) -> dict:
    user = {
        'id': generate_id('U'),
        'username': username,
        'password': make_password(password),
        'role': 'hod',
        'name': name,
    }
    return create_record(USERS_FILE, user)


def create_teacher_user(username: str, password: str, name: str, teacher_id: str) -> dict:
    user = {
        'id': generate_id('U'),
        'username': username,
        'password': make_password(password),
        'role': 'teacher',
        'name': name,
        'teacher_id': teacher_id,
    }
    return create_record(USERS_FILE, user)


# ──────────────────────────────────────────────
# Teacher helpers
# ──────────────────────────────────────────────

def get_all_teachers() -> list:
    return read_json(TEACHERS_FILE)


def get_teacher(teacher_id: str) -> dict | None:
    return get_by_id(TEACHERS_FILE, teacher_id)


def create_teacher(name: str, email: str, phone: str,
                   department: str, username: str, password: str) -> dict:
    teacher_id = generate_id('T')
    teacher = {
        'id': teacher_id,
        'name': name,
        'email': email,
        'phone': phone,
        'department': department,
    }
    create_record(TEACHERS_FILE, teacher)
    create_teacher_user(username, password, name, teacher_id)
    return teacher


def update_teacher(teacher_id: str, name: str, email: str,
                   phone: str, department: str) -> dict | None:
    updates = {'name': name, 'email': email, 'phone': phone, 'department': department}
    # Also update name in users file
    users = read_json(USERS_FILE)
    for u in users:
        if u.get('teacher_id') == teacher_id:
            u['name'] = name
    write_json(USERS_FILE, users)
    return update_record(TEACHERS_FILE, teacher_id, updates)


def delete_teacher(teacher_id: str) -> bool:
    # Delete teacher, their user account, and all assignments
    delete_record(TEACHERS_FILE, teacher_id)
    users = read_json(USERS_FILE)
    write_json(USERS_FILE, [u for u in users if u.get('teacher_id') != teacher_id])
    assignments = read_json(ASSIGNMENTS_FILE)
    write_json(ASSIGNMENTS_FILE, [a for a in assignments if a.get('teacher_id') != teacher_id])
    return True


# ──────────────────────────────────────────────
# Class helpers
# ──────────────────────────────────────────────

def get_all_classes() -> list:
    return read_json(CLASSES_FILE)


def get_class(class_id: str) -> dict | None:
    return get_by_id(CLASSES_FILE, class_id)


def create_class(name: str, description: str = '') -> dict:
    cls = {'id': generate_id('C'), 'name': name, 'description': description}
    return create_record(CLASSES_FILE, cls)


def update_class(class_id: str, name: str, description: str) -> dict | None:
    return update_record(CLASSES_FILE, class_id, {'name': name, 'description': description})


def delete_class(class_id: str) -> bool:
    delete_record(CLASSES_FILE, class_id)
    # Remove assignments referencing this class
    assignments = read_json(ASSIGNMENTS_FILE)
    write_json(ASSIGNMENTS_FILE, [a for a in assignments if a.get('class_id') != class_id])
    # Remove students from this class
    students = read_json(STUDENTS_FILE)
    write_json(STUDENTS_FILE, [s for s in students if s.get('class_id') != class_id])
    return True


# ──────────────────────────────────────────────
# Subject helpers
# ──────────────────────────────────────────────

def get_all_subjects() -> list:
    return read_json(SUBJECTS_FILE)


def get_subject(subject_id: str) -> dict | None:
    return get_by_id(SUBJECTS_FILE, subject_id)


def create_subject(name: str, code: str, description: str = '') -> dict:
    subj = {'id': generate_id('S'), 'name': name, 'code': code, 'description': description}
    return create_record(SUBJECTS_FILE, subj)


def update_subject(subject_id: str, name: str, code: str, description: str) -> dict | None:
    return update_record(SUBJECTS_FILE, subject_id,
                         {'name': name, 'code': code, 'description': description})


def delete_subject(subject_id: str) -> bool:
    delete_record(SUBJECTS_FILE, subject_id)
    assignments = read_json(ASSIGNMENTS_FILE)
    write_json(ASSIGNMENTS_FILE, [a for a in assignments if a.get('subject_id') != subject_id])
    return True


# ──────────────────────────────────────────────
# Student helpers
# ──────────────────────────────────────────────

def get_all_students() -> list:
    return read_json(STUDENTS_FILE)


def get_student(student_id: str) -> dict | None:
    return get_by_id(STUDENTS_FILE, student_id)


def get_students_by_class(class_id: str) -> list:
    return find_by_field(STUDENTS_FILE, 'class_id', class_id)


def create_student(roll_number: str, name: str, class_id: str) -> dict:
    student = {
        'id': generate_id('ST'),
        'roll_number': roll_number,
        'name': name,
        'class_id': class_id,
    }
    return create_record(STUDENTS_FILE, student)


def update_student(student_id: str, roll_number: str,
                   name: str, class_id: str) -> dict | None:
    return update_record(STUDENTS_FILE, student_id,
                         {'roll_number': roll_number, 'name': name, 'class_id': class_id})


def delete_student(student_id: str) -> bool:
    return delete_record(STUDENTS_FILE, student_id)


# ──────────────────────────────────────────────
# Assignment helpers
# ──────────────────────────────────────────────

def get_all_assignments() -> list:
    return read_json(ASSIGNMENTS_FILE)


def get_assignment(assignment_id: str) -> dict | None:
    return get_by_id(ASSIGNMENTS_FILE, assignment_id)


def get_teacher_assignments(teacher_id: str) -> list:
    return find_by_field(ASSIGNMENTS_FILE, 'teacher_id', teacher_id)


def assignment_exists(teacher_id: str, class_id: str, subject_id: str) -> bool:
    for a in read_json(ASSIGNMENTS_FILE):
        if (a.get('teacher_id') == teacher_id and
                a.get('class_id') == class_id and
                a.get('subject_id') == subject_id):
            return True
    return False


def create_assignment(teacher_id: str, class_id: str, subject_id: str) -> dict | None:
    if assignment_exists(teacher_id, class_id, subject_id):
        return None  # already exists
    assignment = {
        'id': generate_id('A'),
        'teacher_id': teacher_id,
        'class_id': class_id,
        'subject_id': subject_id,
    }
    return create_record(ASSIGNMENTS_FILE, assignment)


def delete_assignment(assignment_id: str) -> bool:
    return delete_record(ASSIGNMENTS_FILE, assignment_id)


def teacher_has_assignment(teacher_id: str, class_id: str, subject_id: str) -> bool:
    """Security check: verify teacher is authorised for this class+subject."""
    return assignment_exists(teacher_id, class_id, subject_id)


# ──────────────────────────────────────────────
# Attendance helpers
# ──────────────────────────────────────────────

def get_all_attendance() -> list:
    return read_json(ATTENDANCE_FILE)


def get_attendance_record(att_id: str) -> dict | None:
    return get_by_id(ATTENDANCE_FILE, att_id)


def get_attendance_by_filters(date: str = None, teacher_id: str = None,
                               class_id: str = None, subject_id: str = None) -> list:
    records = read_json(ATTENDANCE_FILE)
    if date:
        records = [r for r in records if r.get('date') == date]
    if teacher_id:
        records = [r for r in records if r.get('teacher_id') == teacher_id]
    if class_id:
        records = [r for r in records if r.get('class_id') == class_id]
    if subject_id:
        records = [r for r in records if r.get('subject_id') == subject_id]
    return records


def find_existing_attendance(date: str, teacher_id: str,
                              class_id: str, subject_id: str) -> dict | None:
    """Find attendance record for exact date+teacher+class+subject combination."""
    for r in read_json(ATTENDANCE_FILE):
        if (r.get('date') == date and
                r.get('teacher_id') == teacher_id and
                r.get('class_id') == class_id and
                r.get('subject_id') == subject_id):
            return r
    return None


def save_attendance(date: str, teacher_id: str, class_id: str,
                    subject_id: str, records: list) -> dict:
    """Create or update attendance. Returns the saved record."""
    existing = find_existing_attendance(date, teacher_id, class_id, subject_id)
    if existing:
        return update_record(ATTENDANCE_FILE, existing['id'], {'records': records})
    att = {
        'id': generate_id('ATT'),
        'date': date,
        'teacher_id': teacher_id,
        'class_id': class_id,
        'subject_id': subject_id,
        'records': records,
    }
    return create_record(ATTENDANCE_FILE, att)


def get_student_attendance_stats(student_id: str, class_id: str,
                                  subject_id: str = None) -> dict:
    """Return present/absent counts and percentage for a student."""
    all_att = read_json(ATTENDANCE_FILE)
    present = 0
    absent = 0
    for att in all_att:
        if att.get('class_id') != class_id:
            continue
        if subject_id and att.get('subject_id') != subject_id:
            continue
        for rec in att.get('records', []):
            if rec.get('student_id') == student_id:
                if rec.get('status') == 'Present':
                    present += 1
                else:
                    absent += 1
    total = present + absent
    percentage = round((present / total) * 100, 1) if total > 0 else 0.0
    return {'present': present, 'absent': absent, 'total': total, 'percentage': percentage}


def get_today_attendance_count(date: str) -> int:
    """Return number of students marked today (across all records)."""
    count = 0
    for att in read_json(ATTENDANCE_FILE):
        if att.get('date') == date:
            count += len(att.get('records', []))
    return count
