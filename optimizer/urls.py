from django.urls import path
from django.views.generic import RedirectView # Importação necessária!
from . import views

urlpatterns = [
    # 1. Rota de Redirecionamento: Mapeia o caminho vazio ('/') para /upload/
    path('', RedirectView.as_view(url='upload/', permanent=True), name='home_redirect'),

    # 2. Rota de Upload (agora acessível via /upload/)
    path('upload/', views.process_uploaded_pdf_api, name='upload_api_root'), 
    
    # 3. Rota de Perguntas
    path('ask/', views.ask_rag_api, name='ask_rag_api'),
]