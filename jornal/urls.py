from django.urls import path
from .views import ArtigoDetailView

urlpatterns = [
    path('artigo/<int:pk>/',ArtigoDetailView.as_view(),name='detalhe_artigo'),
]
