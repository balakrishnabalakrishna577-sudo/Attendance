"""
Custom access-control decorators.
Replace Django's @login_required (which needs the ORM) with session-based checks.
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def login_required(view_func):
    """Redirect to login if not authenticated."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def hod_required(view_func):
    """Allow only HOD users; return 403 for anyone else."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        if request.session.get('role') != 'hod':
            return HttpResponseForbidden(
                '<h2>403 Forbidden</h2><p>HOD access required.</p>'
                '<a href="/dashboard/">Go back</a>'
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    """Allow only Teacher users; return 403 for anyone else."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        if request.session.get('role') != 'teacher':
            return HttpResponseForbidden(
                '<h2>403 Forbidden</h2><p>Teacher access required.</p>'
                '<a href="/dashboard/">Go back</a>'
            )
        return view_func(request, *args, **kwargs)
    return wrapper
