from django.urls import path
from .views import ArtigoDetailView, detalhe_noticia_estatica 
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'jornal'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('todas-noticias/', views.todas_noticias, name='todas_as_noticias'),
    path('noticia-estatica/', detalhe_noticia_estatica, name='detalhe_noticia_estatica'),
    path('categoria/<int:pk>/', views.categoria_view, name='categoria_view'),
    path('adicionar/', views.adicionar_artigo, name='adicionar_artigo'),
    path('artigo/<int:pk>/', ArtigoDetailView.as_view(), name='artigo_detalhe'),
    path('webhook/github/', views.webhook_github, name='webhook_github'),
    path("api/sugestoes/", views.sugestoes_busca, name="sugestoes_busca"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)