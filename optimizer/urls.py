from django.urls import path
from . import views

urlpatterns = [
    # Quando o Frontend/Proxy faz o POST para a URL base (/) do Render, ele atinge esta rota.
    path('', views.process_uploaded_pdf_api, name='upload_api_root'),
    
    # Rota para as requisições POST das perguntas à IA
    path('ask/', views.ask_rag_api, name='ask_rag_api'),
]