from django.urls import path
from . import views

urlpatterns = [
    # Etapa 1: Tela de Configuração (Escolher setor, subir edital)
    path('', views.setup_page, name='interview_setup'),

    # Etapa 2: Tela da Entrevista (Câmera e Perguntas)
    path('start/', views.interview_page, name='interview_start'),

    # API: Gerar nova pergunta (AJAX)
    path('new_question/', views.get_new_question, name='get_new_question'),

    # API: Analisar resposta de áudio (AJAX)
    path('analyze/', views.analyze_response, name='analyze_response'),
]