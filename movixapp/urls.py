from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_movie, name='search_movie'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]