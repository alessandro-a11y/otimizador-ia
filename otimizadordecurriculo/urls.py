from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rota principal / -> upload
    path('', RedirectView.as_view(url='/upload/', permanent=False)),

    # 1. App Otimizador de currículo
    path('', include('optimizer.urls')),

    # 2. Analisador de LinkedIn
    path('linkedin/', include('linkedin_analyser.urls')),

    # 3. Simulador de Entrevista
    path('entrevista/', include('interview_simulator.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
