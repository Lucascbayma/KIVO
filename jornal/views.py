from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.db.models import Q
import requests 
from django.http import Http404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Artigo, Categoria
from .forms import ArtigoForm

NEWSDATA_API_KEY = settings.NEWSDATA_API_KEY 
NEWSDATA_API_URL = 'https://newsdata.io/api/1/latest'

# -----------------------------------------------------------------
# --- VIEWS BASEADAS EM MODELO (Artigos no Banco de Dados) ---
# -----------------------------------------------------------------

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

# -----------------------------------------------------------------
# --- VIEW PARA ADICIONAR NOTÍCIA (Baseada em Artigo Model) ---
# -----------------------------------------------------------------

def adicionar_artigo(request):
    if request.method == 'POST':
        form = ArtigoForm(request.POST, request.FILES) 
        if form.is_valid():
            artigo = form.save(commit=False)
            artigo.autor = request.user 
            artigo.save()
            form.save_m2m()
            return redirect('home') 
    else:
        form = ArtigoForm(initial={'autor': request.user})
        
    context = {
        'form': form,
    }
    return render(request, 'adicionar_noticia.html', context)

# -----------------------------------------------------------------
# --- VIEW PARA EXIBIÇÃO INTERNA DA NOTÍCIA (API) ---
# -----------------------------------------------------------------

def detalhe_noticia_estatica(request):
    noticia_id = request.GET.get('id')
    lista_noticias = request.session.get('ultimas_noticias') 

    noticia_detalhe = None
    
    try:
        if lista_noticias and noticia_id is not None:
            noticia_id = int(noticia_id)
            
            if 0 <= noticia_id < len(lista_noticias):
                noticia_detalhe = lista_noticias[noticia_id]
            else:
                raise Http404("ID da notícia fora do alcance da lista.")
        else:
            raise Http404("Notícia não encontrada ou lista da API não está na sessão.")
            
    except (TypeError, ValueError):
        raise Http404("Parâmetro de ID inválido.")
    except Http404:
        return redirect('home')
        
    context = {
        'noticia': noticia_detalhe
    }
    
    return render(request, 'ler_noticia.html', context)

# -----------------------------------------------------------------
# --- VIEW DA HOME (Faz a Requisição da API e Integra o BD) ---
# -----------------------------------------------------------------

def home(request):
    params = {
        'apikey': NEWSDATA_API_KEY,
        'country': 'br',
        'size': 10,
    }
    noticias_api = []
    esportes_api, politica_api, clima_api = [], [], []
    try:
        response = requests.get(NEWSDATA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'success':
            noticias_api = data.get('results', [])

            for n in noticias_api:
                categoria_raw = n.get('category')
                if isinstance(categoria_raw, list):
                    categoria = ",".join(categoria_raw).lower()
                elif isinstance(categoria_raw, str):
                    categoria = categoria_raw.lower()
                else:
                    categoria = ""

                titulo = (n.get('title') or "").lower()
                descricao = (n.get('description') or "").lower()

                if any(word in categoria for word in ["sport", "esporte"]) or \
                   any(word in titulo for word in ["futebol", "ginástica", "boxe", "corrida"]):
                    esportes_api.append(n)

                elif any(word in categoria for word in ["politic", "government", "world"]) or \
                     any(word in titulo for word in ["lula", "boulos", "presidente", "governo", "eleição"]):
                    politica_api.append(n)

                elif any(word in categoria for word in ["science", "environment"]) or \
                     any(word in titulo for word in ["clima", "chuva", "tempo", "calor", "sensor"]) or \
                     "educação" in descricao:
                    clima_api.append(n)

            request.session['ultimas_noticias'] = noticias_api
            request.session['esportes_noticias'] = esportes_api
            request.session['politica_noticias'] = politica_api
            request.session['tec_noticias'] = clima_api

        else:
            print("Erro: status da API não é success.")

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a API: {e}")

    categorias = {c.nome.lower(): c.id for c in Categoria.objects.all()}
    
    artigos_bd_ultimas = Artigo.objects.filter(
        categoria_id=categorias.get('últimas notícias')
    )[:6] 
    
    artigos_bd_esportes = Artigo.objects.filter(
        categoria_id=categorias.get('esportes')
    )[:6]
    
    artigos_bd_politica = Artigo.objects.filter(
        categoria_id=categorias.get('política')
    )[:6]
    
    artigos_bd_clima = Artigo.objects.filter(
        categoria_id=categorias.get('clima')
    )[:6]
    total_ultimas_bd = len(artigos_bd_ultimas)
    ultimas = list(artigos_bd_ultimas) + noticias_api[:(6 - total_ultimas_bd)]
    
    total_esportes_bd = len(artigos_bd_esportes)
    esportes = list(artigos_bd_esportes) + esportes_api[:(6 - total_esportes_bd)]
    
    total_politica_bd = len(artigos_bd_politica)
    politica = list(artigos_bd_politica) + politica_api[:(6 - total_politica_bd)]
    
    total_clima_bd = len(artigos_bd_clima)
    clima = list(artigos_bd_clima) + clima_api[:(6 - total_clima_bd)]


    context = {
        'ultimas': ultimas,
        'esportes': esportes,
        'politica': politica,
        'clima': clima,
    }

    return render(request, 'home.html', context)