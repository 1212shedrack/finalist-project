from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.http import JsonResponse
from disease_app import views as disease_views
import os

def db_status(request):
    """
    Diagnostic endpoint — visit /db-status/?token=check123 on Render
    to confirm database connection without needing shell access.
    """
    token = request.GET.get('token', '')
    if token != 'check123':
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    result = {
        'DATABASE_URL_set': bool(os.environ.get('DATABASE_URL')),
        'database_engine': settings.DATABASES['default'].get('ENGINE', 'unknown'),
        'database_name': str(settings.DATABASES['default'].get('NAME', 'unknown')),
    }
    try:
        from django.contrib.auth.models import User
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        result['db_connection'] = 'OK'
        result['user_count'] = User.objects.count()
        users = list(User.objects.values_list('username', flat=True))
        result['users'] = users
    except Exception as e:
        result['db_connection'] = f'FAILED: {e}'

    return JsonResponse(result)

urlpatterns = [
    path('db-status/', db_status),
    path('switch-lang/', disease_views.switch_language, name='switch_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', include('accounts.urls')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('disease_app.urls')),
    prefix_default_language=False,
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

