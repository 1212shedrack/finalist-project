from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash, logout
from accounts.decorators import farmer_required
from accounts.models import UserProfile, FavoriteScan, Notification, Feedback
from accounts.forms import ProfileEditForm, AvatarUpdateForm, PasswordChangeForm, FeedbackForm
from disease_app.models import Prediction
import json

@login_required
def dashboard_redirect(request):
    if hasattr(request.user, 'profile') and request.user.profile.is_admin:
        return redirect('accounts:admin_dashboard')
    return redirect('accounts:farmer_dashboard')

@farmer_required
def farmer_dashboard(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    recent_predictions = predictions[:6]
    
    total_scans = predictions.count()
    disease_counts = {}
    for p in predictions:
        disease = p.predicted_class
        disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
    unread_notifs = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'recent_predictions': recent_predictions,
        'stats': {
            'total_scans': total_scans,
            'disease_counts': disease_counts
        },
        'unread_notifications_count': unread_notifs,
    }
    return render(request, 'accounts/farmer/dashboard.html', context)

@farmer_required
def farmer_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:farmer_profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/farmer/profile.html', {'form': form, 'active_tab': 'profile'})

@farmer_required
def farmer_avatar_update(request):
    if request.method == 'POST':
        form = AvatarUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            profile = form.save()
            return JsonResponse({'success': True, 'avatar_url': profile.avatar_url})
        return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@farmer_required
def farmer_change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully.')
            return redirect('accounts:farmer_profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/farmer/profile.html', {'password_form': form, 'active_tab': 'password'})

@farmer_required
def farmer_scan_history(request):
    predictions = Prediction.objects.filter(user=request.user).order_by('-created_at')
    
    q = request.GET.get('q')
    if q:
        predictions = predictions.filter(predicted_class__icontains=q)
        
    disease_class = request.GET.get('class')
    if disease_class:
        predictions = predictions.filter(predicted_class=disease_class)
        
    paginator = Paginator(predictions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/farmer/scan_history.html', {'page_obj': page_obj})

@farmer_required
def farmer_favorites(request):
    favorites = FavoriteScan.objects.filter(user=request.user).select_related('prediction').order_by('-created_at')
    paginator = Paginator(favorites, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounts/farmer/favorites.html', {'page_obj': page_obj})

@farmer_required
def favorite_add(request, pk):
    if request.method == 'POST':
        prediction = get_object_or_404(Prediction, pk=pk, user=request.user)
        FavoriteScan.objects.get_or_create(user=request.user, prediction=prediction)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('accounts:farmer_history')
    return redirect('accounts:farmer_history')

@farmer_required
def favorite_remove(request, pk):
    if request.method == 'POST':
        prediction = get_object_or_404(Prediction, pk=pk, user=request.user)
        FavoriteScan.objects.filter(user=request.user, prediction=prediction).delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('accounts:farmer_favorites')
    return redirect('accounts:farmer_favorites')

@farmer_required
def farmer_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Mark as read
    unread = notifications.filter(is_read=False)
    unread.update(is_read=True)
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounts/farmer/notifications.html', {'page_obj': page_obj})

@farmer_required
def notification_mark_read(request, pk):
    if request.method == 'POST':
        Notification.objects.filter(pk=pk, user=request.user).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@farmer_required
def farmer_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, 'Feedback submitted successfully. Thank you!')
            return redirect('accounts:farmer_dashboard')
    else:
        form = FeedbackForm()
    return render(request, 'accounts/farmer/feedback.html', {'form': form})

@farmer_required
def farmer_delete_account(request):
    if request.method == 'POST':
        request.user.is_active = False
        request.user.save()
        profile = request.user.profile
        profile.is_active = False
        profile.save()
        logout(request)
        messages.info(request, 'Your account has been deleted.')
        return redirect('disease_app:home')
    return render(request, 'accounts/farmer/delete_confirm.html')
