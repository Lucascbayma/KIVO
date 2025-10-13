from django.shortcuts import render

# Create your views here.

from django.views.generic import DetailView
from .models import Artigo

class ArtigoDetailView(DetailView):
    model = Artigo
    template_name = 'templates/artigo.html'
    context_object_name = 'artigo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        artigo_atual = self.object 

        context['recomendacoes'] = artigo_atual.artigos_relacionados(limite=3) 
        
        return context
    