from django.urls import path
from .views import ArtigoDetailView, detalhe_noticia_estatica 
from . import views

urlpatterns = [
    path('noticia-estatica/', detalhe_noticia_estatica, name='detalhe_noticia_estatica'),
    path('artigo/<int:pk>/', ArtigoDetailView.as_view(), name='detalhe_artigo'),
    path('', views.home, name='home'),
]