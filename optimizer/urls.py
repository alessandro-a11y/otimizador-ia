from django.urls import path
from django.views.generic import RedirectView 
from . import views

urlpatterns = [
    # Mapeia a URL vazia ('/') para redirecionar para 'upload/'
    path('', RedirectView.as_view(url='upload/', permanent=True), name='home_redirect'),

    # Mapeia '/upload/' para a view que renderiza o HTML e lida com o POST do formulário
    # O nome (name) 'upload_interface' corresponde ao uso no template HTML.
    path('upload/', views.upload_interface_and_process, name='upload_interface'), 

    # Mapeia '/ask/' para a view de API que lida com as perguntas da IA
    path('ask/', views.ask_rag_api, name='ask_rag'),
]