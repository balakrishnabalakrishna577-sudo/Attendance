# HOD–Teacher Attendance Management System

A simple, professional attendance management system built with **Python Django** and **JSON file storage** — no database required.

---

## Features

| Role    | Capabilities |
|---------|-------------|
| **HOD** | Manage teachers, classes, subjects, students; assign teachers; view full reports with CSV export |
| **Teacher** | Mark attendance for assigned classes/subjects only; edit past attendance; view own records |
| **Student** | No login — exists as data records only |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize sample data

```bash
python manage.py initdata
```

This creates:
- HOD account: `admin` / `admin123`
- Two sample teachers: `teacher1` / `teacher123`, `teacher2` / `teacher123`
- Sample classes, subjects, students, and assignments

To reset everything and start fresh:

```bash
python manage.py initdata --reset
```

### 3. Run the development server

```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## Login Credentials (after initdata)

| Role    | Username  | Password    |
|---------|-----------|-------------|
| HOD     | admin     | admin123    |
| Teacher | teacher1  | teacher123  |
| Teacher | teacher2  | teacher123  |

---

## Project Structure

```
attendance_system/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── attendance_system/          ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── attendance/                 ← Main app
│   ├── views_auth.py           ← Login / Logout
│   ├── views_hod.py            ← All HOD views
│   ├── views_teacher.py        ← All Teacher views
│   ├── urls.py                 ← URL routing
│   ├── decorators.py           ← Access control decorators
│   ├── services/
│   │   └── json_storage.py     ← All JSON read/write helpers
│   ├── management/commands/
│   │   └── initdata.py         ← Setup command
│   ├── templates/attendance/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── hod/                ← HOD templates
│   │   └── teacher/            ← Teacher templates
│   └── static/
│       ├── css/style.css
│       └── js/app.js
│
├── data/                       ← JSON storage files (auto-created)
│   ├── users.json
│   ├── teachers.json
│   ├── classes.json
│   ├── subjects.json
│   ├── students.json
│   ├── assignments.json
│   └── attendance.json
│
└── sessions/                   ← Django file-based sessions (auto-created)
```

---

## Data Storage

All data is stored as JSON in the `data/` directory. Files are created automatically on first run.

| File              | Contents |
|-------------------|----------|
| `users.json`      | HOD and teacher login accounts (hashed passwords) |
| `teachers.json`   | Teacher profiles |
| `classes.json`    | Class records |
| `subjects.json`   | Subject records |
| `students.json`   | Student records (no login) |
| `assignments.json`| Teacher → Class → Subject assignments |
| `attendance.json` | Daily attendance records |

> **Note:** JSON file storage is suitable for demos and small college projects. For large-scale production use with many simultaneous users, migrate to a proper database like PostgreSQL.

---

## Security

- Passwords are hashed using Django's PBKDF2 hasher (same algorithm Django uses for its own auth)
- Sessions are file-based — no database required
- Every teacher request is verified server-side against the assignments file
- Unauthorized URL access returns **403 Forbidden**
- CSRF protection is enabled on all POST forms

---

## Import Students from CSV

CSV format:
```csv
roll_number,name
01,Student One
02,Student Two
03,Student Three
```

Upload via **HOD → Students → Import CSV**.

---

## Attendance Report Export

Go to **HOD → Attendance Reports** and click **Export CSV** to download filtered data.

---

## Deployment (Render / Railway / PythonAnywhere)

1. Set `DEBUG = False` and update `SECRET_KEY` in `settings.py`
2. Set `ALLOWED_HOSTS` to your domain
3. Run `python manage.py collectstatic` for static files
4. Use `gunicorn attendance_system.wsgi` as the start command

For persistent storage on cloud platforms, ensure the `data/` directory is on a persistent disk/volume.
