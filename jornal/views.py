from django.shortcuts import render
from django.views.generic import DetailView


from .models import Artigo 


class ArtigoDetailView(DetailView):
    model = Artigo
    template_name = 'ler_noticia.html' 
    context_object_name = 'artigo' 

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)    
        artigo_atual = self.object 

        try:

             context['recomendacoes'] = artigo_atual.artigos_relacionados(limite=3) 
        except AttributeError:

             context['recomendacoes'] = []
        
        return context

def detalhe_noticia_estatica(request):
    """Renderiza o template 'ler_noticia.html' com dados estáticos."""

    return render(request, 'ler_noticia.html', {})
def home(request):
    return render(request, 'home.html')