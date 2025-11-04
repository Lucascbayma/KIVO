from django.urls import path
from .views import ArtigoDetailView, detalhe_noticia_estatica 
from . import views

urlpatterns = [
    path('noticia-estatica/', detalhe_noticia_estatica, name='detalhe_noticia_estatica'),
    path('artigo/<int:pk>/', ArtigoDetailView.as_view(), name='artigo_detalhe'),
    path('categoria/<int:pk>/', views.categoria_view, name='categoria_view'),
    path('adicionar/', views.adicionar_artigo, name='adicionar_artigo'),
    path('', views.home, name='home'),
]