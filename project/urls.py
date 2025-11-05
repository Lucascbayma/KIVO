"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import ArtigoDetailView, detalhe_noticia_estatica 
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('noticia-estatica/', detalhe_noticia_estatica, name='detalhe_noticia_estatica'),
    path('artigo/<int:pk>/', ArtigoDetailView.as_view(), name='artigo_detalhe'),
    path('categoria/<int:pk>/', views.categoria_view, name='categoria_view'),
    path('adicionar/', views.adicionar_artigo, name='adicionar_artigo'),
    path('todas-noticias/', views.todas_noticias, name='todas_noticias'),
    path('', views.home, name='home'),
]
