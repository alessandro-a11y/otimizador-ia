# optimizer/urls.py (Corrigido)
from django.urls import path
from . import views

urlpatterns = [
    # Mapeia para a URL: /upload/ (A URL que você estava usando)
    path('upload/', views.process_uploaded_pdf_api, name='upload_api_root'), 
    
    # Mapeia para a URL: /ask/
    path('ask/', views.ask_rag_api, name='ask_rag_api'),
]