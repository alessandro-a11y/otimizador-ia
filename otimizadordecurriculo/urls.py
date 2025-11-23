from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Rota do Otimizador de Currículos (App Padrão)
    # Inclui as rotas /upload/ e /ask/ definidas em optimizer.urls
    path('', include('optimizer.urls')),

    # 2. Rota do Analisador de LinkedIn (ATIVADO)
    # Acessível em: http://127.0.0.1:8000/linkedin/
    path('linkedin/', include('linkedin_analyser.urls')),

    # 3. Rota do Simulador de Entrevista (ATIVADO)
    # Acessível em: http://127.0.0.1:8000/entrevista/
    path('entrevista/', include('interview_simulator.urls')),

    # Redireciona a raiz do site (/) direto para o upload de currículos
    # Útil para quando o utilizador acede apenas ao domínio base
    path('', RedirectView.as_view(url='/upload/', permanent=False)),
]

# Configuração para servir ficheiros de média (PDFs/Áudios) no modo Debug
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)