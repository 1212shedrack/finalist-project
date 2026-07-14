import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils.translation import check_for_language
from django.conf import settings as django_settings

from .forms import ImageUploadForm
from .models import Prediction
from .predictor import predict_image, load_recommendation, get_model_status, DISPLAY_NAMES


# ── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    """Landing page with statistics and recent predictions."""
    total   = Prediction.objects.count()
    healthy = Prediction.objects.filter(predicted_class='health').count()
    diseased = Prediction.objects.filter(
        predicted_class__in=['spot_leaf', 'white_rust']
    ).count()
    recent  = Prediction.objects.select_related()[:3]

    context = {
        'total_predictions': total,
        'healthy_count':     healthy,
        'diseased_count':    diseased,
        'recent_predictions': recent,
    }
    return render(request, 'home.html', context)


# ── Predict ───────────────────────────────────────────────────────────────────
def predict(request):
    """Upload page — GET shows form, POST runs inference and redirects."""
    form = ImageUploadForm()

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']

            # Save the uploaded image via the model so it's stored in media/predictions/
            prediction = Prediction(
                predicted_class='pending',
                display_name='Pending',
                confidence=0.0,
                risk_level='Unknown',
            )
            prediction.image.save(image_file.name, image_file, save=True)

            # Run inference
            try:
                result = predict_image(prediction.image.path)
            except Exception as exc:
                prediction.delete()
                messages.error(request, f'Analysis failed: {exc}')
                return render(request, 'predict.html', {'form': ImageUploadForm()})

            # Load recommendation in the active UI language
            lang = getattr(request, 'LANGUAGE_CODE', 'en').split('-')[0]
            rec = load_recommendation(result['predicted_class'], lang=lang)

            # Update and save prediction record
            prediction.predicted_class   = result['predicted_class']
            prediction.display_name      = result['display_name']
            prediction.confidence        = result['confidence']
            prediction.all_probabilities = result['probabilities']
            prediction.risk_level        = result['risk_level']
            prediction.risk_color        = result['risk_color']
            prediction.save()

            messages.success(request, f"Analysis complete: {result['display_name']} detected ({result['confidence']:.1f}% confidence)")
            return redirect('disease_app:result', pk=prediction.pk)


        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

    return render(request, 'predict.html', {'form': form})


# ── Result ────────────────────────────────────────────────────────────────────
def result(request, pk):
    """Display prediction result with recommendation."""
    prediction  = get_object_or_404(Prediction, pk=pk)
    lang        = getattr(request, 'LANGUAGE_CODE', 'en').split('-')[0]
    rec         = load_recommendation(prediction.predicted_class, lang=lang)

    # Build display probabilities with friendly names
    probs_display = []
    for class_key, prob_val in prediction.all_probabilities.items():
        probs_display.append({
            'class_key':    class_key,
            'display_name': DISPLAY_NAMES.get(class_key, class_key),
            'probability':  prob_val,
            'color':        _prob_color(class_key),
        })
    probs_display.sort(key=lambda x: x['probability'], reverse=True)

    context = {
        'prediction':      prediction,
        'recommendation':  rec,
        'probs_display':   probs_display,
    }
    return render(request, 'result.html', context)


def _prob_color(class_key):
    color_map = {
        'health':         'success',
        'non_amaranthus': 'secondary',
        'spot_leaf':      'warning',
        'white_rust':     'danger',
    }
    return color_map.get(class_key, 'secondary')


# ── History ───────────────────────────────────────────────────────────────────
def history(request):
    """Paginated prediction history with search and filters."""
    qs = Prediction.objects.all()

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(display_name__icontains=search) | qs.filter(predicted_class__icontains=search)

    filter_class = request.GET.get('filter', '')
    if filter_class and filter_class != 'all':
        qs = qs.filter(predicted_class=filter_class)

    paginator = Paginator(qs, 12)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj':      page_obj,
        'search':        search,
        'filter_class':  filter_class,
        'total_count':   qs.count(),
        'display_names': DISPLAY_NAMES,
    }
    return render(request, 'history.html', context)


# ── About ─────────────────────────────────────────────────────────────────────
def about(request):
    """About page with system and model information."""
    model_status = get_model_status()
    total_predictions = Prediction.objects.count()
    context = {
        'model_status':       model_status,
        'total_predictions':  total_predictions,
    }
    return render(request, 'about.html', context)


# ── Delete Prediction ─────────────────────────────────────────────────────────
@require_POST
def delete_prediction(request, pk):
    """Delete a single prediction record."""
    prediction = get_object_or_404(Prediction, pk=pk)
    prediction.image.delete(save=False)
    prediction.delete()
    messages.success(request, 'Prediction deleted successfully.')
    return redirect('disease_app:history')


# ── Statistics API ────────────────────────────────────────────────────────────
def statistics(request):
    """JSON API for chart data on the home/about page."""
    from django.db.models import Count, Avg

    class_counts = (
        Prediction.objects
        .values('predicted_class', 'display_name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    avg_confidence = Prediction.objects.aggregate(avg=Avg('confidence'))['avg'] or 0

    data = {
        'labels':      [DISPLAY_NAMES.get(c['predicted_class'], c['predicted_class']) for c in class_counts],
        'counts':      [c['count'] for c in class_counts],
        'total':       Prediction.objects.count(),
        'avg_confidence': round(avg_confidence, 1),
    }
    return JsonResponse(data)


# ── Language Switcher ─────────────────────────────────────────────────────────
@require_POST
def switch_language(request):
    """
    Custom language switcher view.

    Django's built-in set_language uses translate_url() which fails when
    switching between two non-default languages (e.g. sw → fr) because the
    prefix pattern resolver can't find a match for the old-language URL.

    This view instead:
      1. Reads the target language from POST['language']
      2. Strips the old language prefix from POST['next']  (e.g. /sw/predict/ → /predict/)
      3. Prepends the new language prefix                  (e.g. /predict/ → /fr/predict/)
      4. Sets the language cookie (LANGUAGE_COOKIE_NAME) and redirects
    """
    lang_code = request.POST.get('language', 'en').strip()
    next_url  = request.POST.get('next', '/').strip() or '/'

    # Validate: fall back to English for unknown codes
    if not check_for_language(lang_code):
        lang_code = 'en'

    # ── Strip existing language prefix ────────────────────────────────────────
    # With prefix_default_language=False:
    #   English has NO prefix  → /predict/
    #   Swahili uses /sw/      → /sw/predict/
    #   French  uses /fr/      → /fr/predict/
    for code, _ in django_settings.LANGUAGES:
        if code == 'en':
            continue  # English has no prefix to strip
        if next_url.startswith(f'/{code}/'):
            next_url = next_url[len(f'/{code}'):]   # → /predict/
            break
        if next_url.rstrip('/') == f'/{code}':
            next_url = '/'                           # root page
            break

    # Ensure it starts with /
    if not next_url.startswith('/'):
        next_url = '/'

    # ── Apply new language prefix ─────────────────────────────────────────────
    if lang_code == 'en':
        target_url = next_url                       # no prefix for English
    else:
        target_url = (
            f'/{lang_code}/'
            if next_url == '/'
            else f'/{lang_code}{next_url}'
        )

    # ── Build response and set cookie ─────────────────────────────────────────
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
