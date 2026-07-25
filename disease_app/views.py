# import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils.translation import check_for_language, gettext as _
from django.conf import settings as django_settings

from .forms import ImageUploadForm
from .models import Prediction
from .predictor import (
    DISPLAY_NAMES,
    get_model_status,
    load_recommendation,
    predict_image,
)


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _is_admin_user(user):
    """Return True if user is a superuser or has admin profile role."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'admin'


# Home — public, shows aggregate statistics
def home(request):
    """Landing page with statistics and recent predictions."""
    total = Prediction.objects.count()
    healthy = Prediction.objects.filter(predicted_class='health').count()
    diseased = Prediction.objects.filter(
        predicted_class__in=['spot_leaf', 'white_rust']
    ).count()
    recent = Prediction.objects.select_related('user')[:3]

    context = {
        'total_predictions': total,
        'healthy_count': healthy,
        'diseased_count': diseased,
        'recent_predictions': recent,
    }
    return render(request, 'home.html', context)


# Predict — requires login (Option A: all scans tied to a user)
@login_required
def predict(request):
    """Upload page — GET shows form, POST runs inference and redirects."""
    form = ImageUploadForm()

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            lang = getattr(request, 'LANGUAGE_CODE', 'en').split('-')[0]

            # Save the uploaded image (attached to the current user)
            prediction = Prediction(
                user=request.user,
                predicted_class='pending',
                display_name='Pending',
                confidence=0.0,
                risk_level='Unknown',
                language_used=lang,
            )
            prediction.image.save(image_file.name, image_file, save=True)

            # Run inference
            try:
                result = predict_image(prediction.image.path)
            except Exception as exc:
                prediction.image.delete(save=False)
                prediction.delete()
                messages.error(request, _('Analysis failed: %(error)s') % {'error': exc})
                return render(request,
                              'predict.html', {'form': ImageUploadForm()})

            # Load recommendation in the active UI language
            rec = load_recommendation(result['predicted_class'], lang=lang)

            # Update and save prediction record
            prediction.predicted_class = result['predicted_class']
            prediction.display_name = result['display_name']
            prediction.confidence = result['confidence']
            prediction.all_probabilities = result['probabilities']
            prediction.risk_level = result['risk_level']
            prediction.risk_color = result['risk_color']
            prediction.language_used = lang
            prediction.save()

            # Log the scan action
            try:
                from accounts.models import SystemLog
                SystemLog.objects.create(
                    user=request.user,
                    action='scan',
                    description=f"Scan: {result['display_name']} ({result['confidence']:.1f}%)",
                    ip_address=_get_client_ip(request),
                )
            except Exception:
                pass  # Never block inference due to logging failures

            messages.success(request,
                             _('Analysis complete: %(name)s detected (%(conf).1f%% confidence)') % {
                                 'name': _(result['display_name']),
                                 'conf': result['confidence'],
                             })
            return redirect('disease_app:result', pk=prediction.pk)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    return render(request, 'predict.html', {'form': form})


# Result — requires login; farmers can only view their own results
@login_required
def result(request, pk):
    """Display prediction result with recommendation."""
    prediction = get_object_or_404(Prediction, pk=pk)

    # Ownership check: farmers see only their own; admins see all
    if not _is_admin_user(request.user):
        if prediction.user != request.user:
            raise PermissionDenied

    lang = getattr(request, 'LANGUAGE_CODE', 'en').split('-')[0]
    rec = load_recommendation(prediction.predicted_class, lang=lang)

    # Build display probabilities with friendly names
    probs_display = []
    for class_key, prob_val in prediction.all_probabilities.items():
        name_str = DISPLAY_NAMES.get(class_key, class_key)
        probs_display.append({
            'class_key': class_key,
            'display_name': _(name_str),
            'probability': prob_val,
            'color': _prob_color(class_key),
        })
    probs_display.sort(key=lambda x: x['probability'], reverse=True)


    # Check if scan is in user's favorites
    is_favorite = False
    try:
        from accounts.models import FavoriteScan
        is_favorite = FavoriteScan.objects.filter(
            user=request.user, prediction=prediction).exists()
    except Exception:
        pass

    context = {
        'prediction': prediction,
        'recommendation': rec,
        'probs_display': probs_display,
        'is_favorite': is_favorite,
    }
    return render(request, 'result.html', context)


def _prob_color(class_key):
    color_map = {
        'health': 'success',
        'non_amaranthus': 'secondary',
        'spot_leaf': 'warning',
        'white_rust': 'danger',
    }
    return color_map.get(class_key, 'secondary')


# History — requires login; farmers see only their own scans
@login_required
def history(request):
    """Paginated prediction history with search and filters."""
    if _is_admin_user(request.user):
        qs = Prediction.objects.select_related('user').all()
    else:
        qs = Prediction.objects.filter(user=request.user)

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(
            display_name__icontains=search) | qs.filter(
                predicted_class__icontains=search)

    filter_class = request.GET.get('filter', '')
    if filter_class and filter_class != 'all':
        qs = qs.filter(predicted_class=filter_class)

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'search': search,
        'filter_class': filter_class,
        'total_count': qs.count(),
        'display_names': DISPLAY_NAMES,
    }
    return render(request, 'history.html', context)


# About — public
def about(request):
    """About page with system and model information."""
    model_status = get_model_status()
    total_predictions = Prediction.objects.count()
    context = {
        'model_status': model_status,
        'total_predictions': total_predictions,
    }
    return render(request, 'about.html', context)


# Delete Prediction — login required; farmers can only delete their own
@login_required
@require_POST
def delete_prediction(request, pk):
    """Delete a single prediction record."""
    prediction = get_object_or_404(Prediction, pk=pk)

    # Ownership check
    if not _is_admin_user(request.user):
        if prediction.user != request.user:
            raise PermissionDenied

    prediction.image.delete(save=False)
    prediction.delete()
    messages.success(request, _('Prediction deleted successfully.'))

    # Redirect back to appropriate history page
    referer = request.META.get('HTTP_REFERER', '')
    if 'dashboard' in referer:
        return redirect('accounts:farmer_history')
    return redirect('disease_app:history')


# Statistics API
def statistics(request):
    """JSON API for chart data on the home/about page."""
    from django.db.models import Count, Avg

    class_counts = (
        Prediction.objects
        .values('predicted_class', 'display_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    avg_confidence = Prediction.objects.aggregate(
        avg=Avg('confidence'))['avg'] or 0

    data = {
        'labels': [DISPLAY_NAMES.get(
            c['predicted_class'], c['predicted_class']) for c in class_counts],
        'counts': [c['count'] for c in class_counts],
        'total': Prediction.objects.count(),
        'avg_confidence': round(avg_confidence, 1),
    }
    return JsonResponse(data)


# Language Switcher
@require_POST
def switch_language(request):
    """
    Custom language switcher view.

    Django's built-in set_language uses translate_url() which fails when
    switching between two non-default languages (e.g. sw -> fr) because the
    prefix pattern resolver can't find a match for the old-language URL.

    This view instead:
      1. Reads the target language from POST['language']
      2. Strips the old language prefix from POST['next']
      3. Prepends the new language prefix
      4. Sets the language cookie (LANGUAGE_COOKIE_NAME) and redirects
    """
    lang_code = request.POST.get('language', 'en').strip()
    next_url = request.POST.get('next', '/').strip() or '/'

    # Validate: fall back to English for unknown codes
    if not check_for_language(lang_code):
        lang_code = 'en'

    # Strip existing language prefix
    for code, _ in django_settings.LANGUAGES:
        if code == 'en':
            continue  # English has no prefix to strip
        if next_url.startswith(f'/{code}/'):
            next_url = next_url[len(f'/{code}'):]
            break
        if next_url.rstrip('/') == f'/{code}':
            next_url = '/'
            break

    # Ensure it starts with /
    if not next_url.startswith('/'):
        next_url = '/'

    # Apply new language prefix
    if lang_code == 'en':
        target_url = next_url
    else:
        target_url = (
            f'/{lang_code}/'
            if next_url == '/'
            else f'/{lang_code}{next_url}'
        )

    # Build response and set cookie
    response = HttpResponseRedirect(target_url)
    response.set_cookie(
        django_settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=django_settings.LANGUAGE_COOKIE_AGE,
        path='/',
        samesite='Lax',
        httponly=False,
    )
    return response
