from django.urls import path
from django.views.generic import RedirectView 
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='upload/', permanent=True), name='home_redirect'),

    path('upload/', views.upload_interface_and_process, name='upload_interface'), 

    path('ask/', views.ask_rag_api, name='ask_rag'),
]