from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.db.models import Q
from datetime import date
import csv

from accounts.decorators import admin_required
from accounts.models import UserProfile, Notification, Feedback, SystemLog
from disease_app.models import Prediction
from accounts.views.auth_views import log_system_action, get_client_ip

def _ensure_user_profiles_exist():
    """Self-healing helper: ensure every User has a UserProfile."""
    existing_user_ids = UserProfile.objects.values_list('user_id', flat=True)
    users_without_profile = User.objects.exclude(id__in=existing_user_ids)
    for u in users_without_profile:
        role = 'admin' if (u.is_staff or u.is_superuser) else 'farmer'
        UserProfile.objects.get_or_create(user=u, defaults={'role': role})

@admin_required
def admin_dashboard(request):
    _ensure_user_profiles_exist()
    total_farmers = UserProfile.objects.filter(role='farmer').count()
    total_scans = Prediction.objects.count()
    scans_today = Prediction.objects.filter(created_at__date=date.today()).count()
    
    recent_predictions = Prediction.objects.order_by('-created_at')[:10]
    recent_farmers = UserProfile.objects.filter(role='farmer').order_by('-created_at')[:5]
    
    context = {
        'total_farmers': total_farmers,
        'total_scans': total_scans,
        'scans_today': scans_today,
        'recent_predictions': recent_predictions,
        'recent_farmers': recent_farmers,
    }
    return render(request, 'accounts/admin_panel/dashboard.html', context)

@admin_required
def admin_farmers(request):
    _ensure_user_profiles_exist()
    farmers_qs = UserProfile.objects.filter(role='farmer').select_related('user').order_by('-created_at')
    
    q = request.GET.get('q', '').strip()
    if q:
        farmers_qs = farmers_qs.filter(
            Q(user__username__icontains=q) |
            Q(user__email__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q) |
            Q(phone__icontains=q) |
            Q(location__icontains=q)
        )
        
    paginator = Paginator(farmers_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin_panel/farmers.html', {
        'farmers': page_obj,
        'page_obj': page_obj,
        'q': q,
    })

@admin_required
def admin_farmer_detail(request, user_id):
    _ensure_user_profiles_exist()
    user = get_object_or_404(User, pk=user_id)
    profile = getattr(user, 'profile', None)
    if profile is None:
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'farmer'})

    if request.method == 'POST':
        messages.success(request, 'Farmer details updated.')
        return redirect('accounts:admin_farmer_detail', user_id=user_id)
        
    scans = Prediction.objects.filter(user=user).order_by('-created_at')[:10]
    return render(request, 'accounts/admin_panel/farmer_detail.html', {
        'farmer': profile,
        'farmer_user': user,
        'scans': scans
    })

@admin_required
def admin_toggle_active(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.is_active = not user.is_active
        user.save()
        if hasattr(user, 'profile'):
            user.profile.is_active = user.is_active
            user.profile.save()
        log_system_action(request.user, 'admin_action', f'Toggled active status for {user.username}', get_client_ip(request))
        messages.success(request, f'Account status for {user.username} changed.')
        return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_farmers'))
    return redirect('accounts:admin_farmers')

@admin_required
def admin_delete_farmer(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        username = user.username
        user.delete()
        log_system_action(request.user, 'delete', f'Deleted farmer account {username}', get_client_ip(request))
        messages.success(request, f'Farmer account {username} deleted.')
        return redirect('accounts:admin_farmers')
    return redirect('accounts:admin_farmers')

@admin_required
def admin_reset_password(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        temp_password = get_random_string(12)
        user.set_password(temp_password)
        user.save()
        log_system_action(request.user, 'admin_action', f'Reset password for {user.username}', get_client_ip(request))
        messages.success(request, f'Password for {user.username} reset to: {temp_password}')
        return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_farmers'))
    return redirect('accounts:admin_farmers')

@admin_required
def admin_all_scans(request):
    scans_qs = Prediction.objects.select_related('user').order_by('-created_at')
    
    q = request.GET.get('q', '').strip()
    if q:
        scans_qs = scans_qs.filter(
            Q(user__username__icontains=q) |
            Q(predicted_class__icontains=q) |
            Q(display_name__icontains=q)
        )
        
    disease = request.GET.get('disease', '').strip()
    if disease:
        scans_qs = scans_qs.filter(predicted_class=disease)
        
    risk = request.GET.get('risk', '').strip()
    if risk:
        scans_qs = scans_qs.filter(risk_level=risk)
        
    paginator = Paginator(scans_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin_panel/scans.html', {
        'all_predictions': page_obj,
        'page_obj': page_obj,
        'q': q,
        'selected_disease': disease,
        'selected_risk': risk,
    })

@admin_required
def admin_reports(request):
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="scans_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Disease', 'Confidence', 'Risk Level', 'Date'])
        
        scans = Prediction.objects.all().order_by('-created_at')
        for scan in scans:
            username = scan.user.username if scan.user else 'Anonymous'
            writer.writerow([scan.id, username, scan.predicted_class, scan.confidence, scan.risk_level, scan.created_at])
            
        return response
        
    return render(request, 'accounts/admin_panel/reports.html')

@admin_required
def admin_feedback(request):
    feedbacks_qs = Feedback.objects.select_related('user').order_by('-created_at')
    
    category = request.GET.get('category', '').strip()
    if category:
        feedbacks_qs = feedbacks_qs.filter(category=category)
        
    status = request.GET.get('status', '').strip()
    if status == 'resolved':
        feedbacks_qs = feedbacks_qs.filter(is_resolved=True)
    elif status == 'pending':
        feedbacks_qs = feedbacks_qs.filter(is_resolved=False)
        
    paginator = Paginator(feedbacks_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin_panel/feedback.html', {
        'feedbacks': page_obj,
        'page_obj': page_obj,
        'selected_category': category,
        'selected_status': status,
    })

@admin_required
def admin_resolve_feedback(request, pk):
    if request.method == 'POST':
        feedback = get_object_or_404(Feedback, pk=pk)
        feedback.is_resolved = not feedback.is_resolved
        feedback.save()
        messages.success(request, 'Feedback status updated.')
        return redirect(request.META.get('HTTP_REFERER', 'accounts:admin_feedback'))
    return redirect('accounts:admin_feedback')

@admin_required
def admin_logs(request):
    logs_qs = SystemLog.objects.select_related('user').order_by('-created_at')
    paginator = Paginator(logs_qs, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounts/admin_panel/logs.html', {
        'logs': page_obj,
        'page_obj': page_obj,
    })

@admin_required
def admin_send_notification(request, user_id=None):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        notif_type = request.POST.get('notif_type', 'info')
        target = request.POST.get('target', 'all')
        
        if target == 'all':
            users = User.objects.filter(profile__role='farmer', is_active=True)
            notifications = [
                Notification(user=u, title=title, message=message, notif_type=notif_type)
                for u in users
            ]
            Notification.objects.bulk_create(notifications)
            messages.success(request, f'Notification sent to {users.count()} farmers.')
        else:
            target_user_id = request.POST.get('user_id')
            if target_user_id:
                user = get_object_or_404(User, pk=target_user_id)
                Notification.objects.create(user=user, title=title, message=message, notif_type=notif_type)
                messages.success(request, f'Notification sent to {user.username}.')
                
        return redirect('accounts:admin_dashboard')
        
    return render(request, 'accounts/admin_panel/notify.html', {'target_user_id': user_id})

@admin_required
def admin_chart_data(request):
    from disease_app.predictor import DISPLAY_NAMES
    predictions = Prediction.objects.all()
    disease_counts = {}
    for p in predictions:
        disease = p.predicted_class
        disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
    labels = [DISPLAY_NAMES.get(k, k) for k in disease_counts.keys()]
    data = list(disease_counts.values())
    colors = ['#198754', '#fd7e14', '#dc3545', '#6c757d'][:len(labels)]
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'colors': colors,
    })
