from django.urls import path
from . import views

urlpatterns = [
    path('', views.linkedin_home, name='linkedin_home'),
    path('ask/', views.linkedin_ask, name='linkedin_ask'),
]