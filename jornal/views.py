from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
import requests 
from django.http import Http404
from django.conf import settings

from .models import Artigo 

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
# --- VIEW PARA EXIBIÇÃO INTERNA DA NOTÍCIA (API) ---
# -----------------------------------------------------------------

def detalhe_noticia_estatica(request):
    # 1. Recupera o ID (índice) da notícia da URL (?id=X)
    noticia_id = request.GET.get('id')
    
    # 2. Recupera a lista de notícias que foi salva na sessão pela view 'home'
    lista_noticias = request.session.get('ultimas_noticias')

    noticia_detalhe = None
    
    # Validação e Extração
    try:
        if lista_noticias and noticia_id is not None:
            noticia_id = int(noticia_id)
            
            if 0 <= noticia_id < len(lista_noticias):
                # 3. Extrai a notícia específica da lista
                noticia_detalhe = lista_noticias[noticia_id]
            else:
                raise Http404("ID da notícia fora do alcance da lista.")
        else:
            raise Http404("Notícia não encontrada ou lista da API não está na sessão.")
            
    except (TypeError, ValueError):
        # Captura se 'id' não for um número
        raise Http404("Parâmetro de ID inválido.")
    except Http404:
        # Em caso de falha, redireciona para a home para recarregar a lista.
        return redirect('home')
        
    context = {
        'noticia': noticia_detalhe
    }
    
    return render(request, 'ler_noticia.html', context)

# -----------------------------------------------------------------
# --- VIEW DA HOME (Faz a Requisição da API) ---
# -----------------------------------------------------------------

def home(request):
    params = {
        'apikey': NEWSDATA_API_KEY,
        'country': 'br',
        'size': 10,
    }

    noticias = []
    esportes, politica, clima = [], [], []

    try:
        response = requests.get(NEWSDATA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        print("\n=======================")
        print("🔍 Retorno completo da API:")
        print(data)
        print("=======================\n")

        if data.get('status') == 'success':
            noticias = data.get('results', [])
            print(f"✅ Total de artigos recebidos: {len(noticias)}")

            if noticias:
                print("🔹 Primeira notícia exemplo:")
                print(noticias[0])  # Mostra os campos disponíveis

            # ✅ Classificação segura (corrigida)
            for n in noticias:
                categoria_raw = n.get('category')

                # Pode ser lista, string ou None
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
                    esportes.append(n)

                elif any(word in categoria for word in ["politic", "government", "world"]) or \
                     any(word in titulo for word in ["lula", "boulos", "presidente", "governo", "eleição"]):
                    politica.append(n)

                elif any(word in categoria for word in ["science", "environment"]) or \
                     any(word in titulo for word in ["clima", "chuva", "tempo", "calor", "sensor"]) or \
                     "educação" in descricao:
                    clima.append(n)

            # Guarda na sessão para view detalhe
            request.session['ultimas_noticias'] = noticias
            request.session['esportes_noticias'] = esportes
            request.session['politica_noticias'] = politica
            request.session['tec_noticias'] = clima

            # Apenas debug pra ver contagem
            print(f"🏈 Esportes: {len(esportes)} | 🏛️ Política: {len(politica)} | ☁️ Clima: {len(clima)}")

        else:
            print("❌ Erro: status da API não é success.")
            print("Mensagem:", data.get('message'))

    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erro de conexão com a API: {e}")

    context = {
        'ultimas': noticias[:6],
        'esportes': esportes[:6],
        'politica': politica[:6],
        'clima': clima[:6],
    }

    return render(request, 'home.html', context)
