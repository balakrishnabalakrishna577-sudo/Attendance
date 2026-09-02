"""
JSON File Storage Service
Handles all read/write operations for JSON data files.
No database is used — all data persists in the data/ directory.
Students and attendance have been removed from this project.
"""

import json
import os
import uuid
import threading
from datetime import datetime
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

# Per-file thread locks to prevent race conditions on concurrent writes
_file_locks = {}
_lock_registry = threading.Lock()


def _get_lock(filename: str) -> threading.Lock:
    with _lock_registry:
        if filename not in _file_locks:
            _file_locks[filename] = threading.Lock()
        return _file_locks[filename]


def _get_path(filename: str) -> str:
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
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


# ── Generic CRUD ───────────────────────────────────────────

def get_by_id(filename: str, record_id: str) -> dict | None:
    for r in read_json(filename):
        if r.get('id') == record_id:
            return r
    return None


def create_record(filename: str, data: dict) -> dict:
    records = read_json(filename)
    data['created_at'] = datetime.now().isoformat()
    records.append(data)
    write_json(filename, records)
    return data


def update_record(filename: str, record_id: str, updates: dict) -> dict | None:
    records = read_json(filename)
    for i, r in enumerate(records):
        if r.get('id') == record_id:
            records[i].update(updates)
            records[i]['updated_at'] = datetime.now().isoformat()
            write_json(filename, records)
            return records[i]
    return None


def delete_record(filename: str, record_id: str) -> bool:
    records = read_json(filename)
    new_records = [r for r in records if r.get('id') != record_id]
    if len(new_records) == len(records):
        return False
    write_json(filename, new_records)
    return True


def find_by_field(filename: str, field: str, value) -> list:
    return [r for r in read_json(filename) if r.get(field) == value]


def find_one_by_field(filename: str, field: str, value) -> dict | None:
    for r in read_json(filename):
        if r.get(field) == value:
            return r
    return None


# ── File name constants ────────────────────────────────────

USERS_FILE       = 'users.json'
TEACHERS_FILE    = 'teachers.json'
CLASSES_FILE     = 'classes.json'
SUBJECTS_FILE    = 'subjects.json'
ASSIGNMENTS_FILE = 'assignments.json'


def init_data_files():
    """Ensure all required data files exist."""
    for fname in [USERS_FILE, TEACHERS_FILE, CLASSES_FILE,
                  SUBJECTS_FILE, ASSIGNMENTS_FILE]:
        read_json(fname)


# ── Users ──────────────────────────────────────────────────

def get_user_by_username(username: str) -> dict | None:
    return find_one_by_field(USERS_FILE, 'username', username)


def verify_password(plain: str, hashed: str) -> bool:
    return check_password(plain, hashed)


def create_hod(username: str, password: str, name: str) -> dict:
    user = {
        'id':       generate_id('U'),
        'username': username,
        'password': make_password(password),
        'role':     'hod',
        'name':     name,
    }
    return create_record(USERS_FILE, user)


# ── Teachers ───────────────────────────────────────────────

def get_all_teachers() -> list:
    return read_json(TEACHERS_FILE)


def get_teacher(teacher_id: str) -> dict | None:
    return get_by_id(TEACHERS_FILE, teacher_id)


def create_teacher_no_login(name: str, email: str,
                             phone: str, department: str) -> dict:
    """Create a teacher record — no login account."""
    teacher = {
        'id':         generate_id('T'),
        'name':       name,
        'email':      email,
        'phone':      phone,
        'department': department,
    }
    return create_record(TEACHERS_FILE, teacher)


def update_teacher(teacher_id: str, name: str, email: str,
                   phone: str, department: str) -> dict | None:
    return update_record(TEACHERS_FILE, teacher_id,
                         {'name': name, 'email': email,
                          'phone': phone, 'department': department})


def delete_teacher(teacher_id: str) -> bool:
    """Delete teacher and all their assignments."""
    delete_record(TEACHERS_FILE, teacher_id)
    assignments = read_json(ASSIGNMENTS_FILE)
    write_json(ASSIGNMENTS_FILE,
               [a for a in assignments if a.get('teacher_id') != teacher_id])
    return True


# ── Classes ────────────────────────────────────────────────

def get_all_classes() -> list:
    return read_json(CLASSES_FILE)


def get_class(class_id: str) -> dict | None:
    return get_by_id(CLASSES_FILE, class_id)


def create_class(name: str, description: str = '') -> dict:
    cls = {'id': generate_id('C'), 'name': name, 'description': description}
    return create_record(CLASSES_FILE, cls)


def update_class(class_id: str, name: str, description: str) -> dict | None:
    return update_record(CLASSES_FILE, class_id,
                         {'name': name, 'description': description})


def delete_class(class_id: str) -> bool:
    """Delete class and cascade to assignments."""
    delete_record(CLASSES_FILE, class_id)
    assignments = read_json(ASSIGNMENTS_FILE)
    write_json(ASSIGNMENTS_FILE,
               [a for a in assignments if a.get('class_id') != class_id])
    return True


# ── Subjects ───────────────────────────────────────────────

def get_all_subjects() -> list:
    return read_json(SUBJECTS_FILE)


def get_subject(subject_id: str) -> dict | None:
    return get_by_id(SUBJECTS_FILE, subject_id)


def create_subject(name: str, code: str, description: str = '') -> dict:
    subj = {'id': generate_id('S'), 'name': name,
            'code': code, 'description': description}
    return create_record(SUBJECTS_FILE, subj)


def update_subject(subject_id: str, name: str,
                   code: str, description: str) -> dict | None:
    return update_record(SUBJECTS_FILE, subject_id,
                         {'name': name, 'code': code, 'description': description})


def delete_subject(subject_id: str) -> bool:
    """Delete subject and cascade to assignments."""
    delete_record(SUBJECTS_FILE, subject_id)
    assignments = read_json(ASSIGNMENTS_FILE)
    write_json(ASSIGNMENTS_FILE,
               [a for a in assignments if a.get('subject_id') != subject_id])
    return True


# ── Assignments ────────────────────────────────────────────

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


def create_assignment(teacher_id: str, class_id: str,
                      subject_id: str) -> dict | None:
    if assignment_exists(teacher_id, class_id, subject_id):
        return None
    assignment = {
        'id':         generate_id('A'),
        'teacher_id': teacher_id,
        'class_id':   class_id,
        'subject_id': subject_id,
    }
    return create_record(ASSIGNMENTS_FILE, assignment)


def delete_assignment(assignment_id: str) -> bool:
    return delete_record(ASSIGNMENTS_FILE, assignment_id)
