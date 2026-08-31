"""
Authentication views: login, logout, and dashboard router.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from attendance.services.json_storage import get_user_by_username, verify_password


def login_view(request):
    """Handle login for both HOD and Teacher."""
    if request.session.get('user_id'):
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, 'Please enter username and password.')
            return render(request, 'attendance/login.html')

        user = get_user_by_username(username)
        if user and verify_password(password, user['password']):
            # Store minimal session data — no DB needed
            request.session['user_id'] = user['id']
            request.session['username'] = user['username']
            request.session['role'] = user['role']
            request.session['name'] = user.get('name', username)
            if user['role'] == 'teacher':
                request.session['teacher_id'] = user.get('teacher_id', '')
            messages.success(request, f"Welcome, {user.get('name', username)}!")
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'attendance/login.html')


def logout_view(request):
    """Clear session and redirect to login."""
    request.session.flush()
    messages.success(request, 'You have been logged out.')
    return redirect('login')


def dashboard_router(request):
    """Route to the correct dashboard based on role."""
    if not request.session.get('user_id'):
        return redirect('login')
    role = request.session.get('role')
    if role == 'hod':
        return redirect('hod_dashboard')
    elif role == 'teacher':
        return redirect('teacher_dashboard')
    else:
        request.session.flush()
        return redirect('login')
