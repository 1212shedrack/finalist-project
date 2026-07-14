from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from disease_app import views as disease_views

urlpatterns = [
    # Custom language switcher — fixed URL, always reachable regardless of language prefix
    path('switch-lang/', disease_views.switch_language, name='switch_language'),
    # Keep Django's built-in set_language as fallback (not used in templates)
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('disease_app.urls')),
    prefix_default_language=False,   # /predict/ works without /en/ prefix
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)