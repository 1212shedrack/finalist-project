from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def farmer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('accounts:login')
            return redirect(f'{login_url}?next={request.path}')
        profile = getattr(request.user, 'profile', None)
        if profile is None:
            return redirect('accounts:login')
        if not profile.is_active:
            messages.error(request, 'Your account has been disabled.')
            return redirect('accounts:login')
        if profile.role not in ('farmer', 'admin') and not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = reverse('accounts:login')
            return redirect(f'{login_url}?next={request.path}')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if profile is None or profile.role != 'admin':
            raise PermissionDenied
        if not profile.is_active:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
