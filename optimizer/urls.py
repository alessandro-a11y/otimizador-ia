from django.urls import path
from . import views

urlpatterns = [
    # Rota para a página de upload/inicial. 
    # Usei o caminho 'upload/' como no seu original, mas 'upload_route' 
    # é o nome que usaremos para o redirect interno.
    path('upload/', views.upload_pdf, name='upload_route'),
    
    # Rota para as requisições AJAX das perguntas à IA
    path('ask/', views.ask_rag, name='ask_rag'),
]