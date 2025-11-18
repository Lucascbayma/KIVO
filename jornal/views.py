from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.db.models import Q
import requests 
from django.http import Http404, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Artigo, Categoria
from .forms import ArtigoForm
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.template.loader import render_to_string

# Chaves de API e URLs
NEWSDATA_API_KEY = settings.NEWSDATA_API_KEY 
NEWSDATA_API_URL = 'https://newsdata.io/api/1/latest'

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('jornal:registro')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'O apelido "{username}" já está em uso!')
            return redirect('jornal:registro')
        if User.objects.filter(email=email).exists():
            messages.error(request, f'O e-mail "{email}" já foi cadastrado!')
            return redirect('jornal:registro')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        auth_login(request, user)
        messages.success(request, f'Conta criada com sucesso! Bem-vindo, {username}.')
        return redirect('jornal:home')
    return render(request, 'registro.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('jornal:home')
        else:
            messages.error(request, 'Apelido ou senha inválidos.')
            return redirect('jornal:login')
    return render(request, 'login.html')

def logout_view(request):
    auth_logout(request)
    return redirect('jornal:login')

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

@login_required
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
        form = ArtigoForm()
        
    context = {
        'form': form,
    }
    return render(request, 'adicionar_noticia.html', context)

# -----------------------------------------------------------------
# --- VIEW PARA EXIBIÇÃO INTERNA DA NOTÍCIA (API) ---
# -----------------------------------------------------------------

def detalhe_noticia_estatica(request):
    noticia_link = request.GET.get('link')
    lista_noticias_api = request.session.get('ultimas_noticias') 

    noticia_detalhe = None
    
    try:
        if lista_noticias_api and noticia_link:
            for noticia in lista_noticias_api:
                if noticia.get('link') == noticia_link:
                    noticia_detalhe = noticia
                    break
            
            if noticia_detalhe is None:
                raise Http404("Notícia não encontrada pelo link na sessão.")
                
        else:
            raise Http404("Link da notícia não fornecido ou lista da API não está na sessão.")
            
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
                
                if any(word in categoria for word in ["sport", "esporte"]) or \
                   any(word in titulo for word in ["futebol", "ginástica", "boxe", "corrida"]):
                    esportes_api.append(n)

                elif any(word in categoria for word in ["politic", "government", "world"]) or \
                     any(word in titulo for word in ["lula", "boulos", "presidente", "governo", "eleição"]):
                    politica_api.append(n)

                elif any(word in categoria for word in ["science", "environment"]) or \
                     any(word in titulo for word in ["clima", "chuva", "tempo", "calor", "sensor"]):
                    clima_api.append(n)

            request.session['ultimas_noticias'] = noticias_api
            request.session['esportes_noticias'] = esportes_api
            request.session['politica_noticias'] = politica_api
            request.session['clima_noticias'] = clima_api 

        else:
            print("Erro: status da API não é success.")

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a API: {e}")

    categorias = {c.nome.lower(): c.id for c in Categoria.objects.all()}
    
    artigos_bd_ultimas = Artigo.objects.filter(
        categoria__nome__iexact='Últimas Notícias'
    ).order_by('-publicado_em')[:6] 
    
    artigos_bd_esportes = Artigo.objects.filter(
        categoria__nome__iexact='Esportes'
    ).order_by('-publicado_em')[:6]
    
    artigos_bd_politica = Artigo.objects.filter(
        categoria__nome__iexact='Política'
    ).order_by('-publicado_em')[:6]
    
    artigos_bd_clima = Artigo.objects.filter(
        categoria__nome__iexact='Clima'
    ).order_by('-publicado_em')[:6]
    
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

    context.update({
        'ultimas_noticias': context.get('ultimas', []),
        'destaques': Artigo.objects.filter(destaque=True).order_by('-publicado_em')[:3],
        'categorias': Categoria.objects.all(),
        'atalhos': [
            {'nome': 'Home', 'url': '/'},
            {'nome': 'Esportes', 'url': '/categoria/1/'},
            {'nome': 'Política', 'url': '/categoria/2/'},
            {'nome': 'Clima', 'url': '/categoria/3/'},
        ],
        'anuncios': [
            {'titulo': 'Curso de Jornalismo Online', 'formato': 'desktop'},
            {'titulo': 'Assine o Portal Premium', 'formato': 'mobile'},
        ]
    })
        # -----------------------------------------------------------------
    # Conteúdo simulado apenas se a API falhar (para manter proporção do feed)
    # -----------------------------------------------------------------
    if not context.get('ultimas'):
        context['ultimas'] = [
            {'title': 'Notícia de exemplo 1', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
            {'title': 'Notícia de exemplo 2', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
            {'title': 'Notícia de exemplo 3', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
            {'title': 'Notícia de exemplo 4', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
            {'title': 'Notícia de exemplo 5', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
        ]

    return render(request, 'home.html', context)

# -----------------------------------------------------------------
# --- VIEW PARA EXIBIÇÃO DE CATEGORIAS ESPECÍFICAS (História 2) ---
# -----------------------------------------------------------------

def categoria_view(request, pk):
    """
    Exibe as notícias de uma categoria específica, agrupadas por relevância.
    Adicionada para suportar os testes de organização do portal (História 2).
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    artigos = Artigo.objects.filter(categoria=categoria).order_by('-destaque', '-publicado_em')

    context = {
        'categoria': categoria,
        'artigos': artigos,
    }
    return render(request, 'categoria.html', context)

#view para página de todas as notícias

def todas_noticias(request):
    """Página com todas as notícias — inclui busca, filtro e ordenação."""
    categoria_nome = request.GET.get('categoria')
    busca = request.GET.get('q')
    ordenacao = request.GET.get('ordenar', '-publicado_em')  # padrão: mais recentes primeiro

    noticias = Artigo.objects.all()

    if categoria_nome:
        noticias = noticias.filter(categoria__nome__icontains=categoria_nome)

    if busca:
        noticias = noticias.filter(
            Q(titulo__icontains=busca) |
            Q(conteudo__icontains=busca)
        )

    opcoes_validas = {
        'mais_recentes': '-publicado_em',
        'mais_antigas': 'publicado_em',
        'titulo_az': 'titulo',
        'titulo_za': '-titulo'
    }
    noticias = noticias.order_by(opcoes_validas.get(ordenacao, '-publicado_em'))

    paginator = Paginator(noticias, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorias = Categoria.objects.all()

    contexto = {
        'page_obj': page_obj,
        'categorias': categorias,
        'categoria_nome': categoria_nome,
        'busca': busca,
        'ordenacao': ordenacao,
    }
    return render(request, 'todas_as_noticias.html', contexto)

def ajax_todas_noticias(request):
    page_number = request.GET.get('page', 1)
    categoria_nome = request.GET.get('categoria')
    busca = request.GET.get('q')
    ordenar = request.GET.get('ordenar', '-publicado_em')
    noticias = Artigo.objects.all()
    if categoria_nome:
        noticias = noticias.filter(categoria__nome__icontains=categoria_nome)
    if busca:
        noticias = noticias.filter(Q(titulo__icontains=busca) | Q(conteudo__icontains=busca))
    opcoes_validas = {
        'mais_recentes': '-publicado_em',
        'mais_antigas': 'publicado_em',
        'titulo_az': 'titulo',
        'titulo_za': '-titulo'
    }
    noticias = noticias.order_by(opcoes_validas.get(ordenar, '-publicado_em'))
    paginator = Paginator(noticias, 8)
    page_obj = paginator.get_page(page_number)
    artigos_html = [render_to_string('partials/card_noticia.html', {'n': n}) for n in page_obj]
    return JsonResponse({'artigos': artigos_html, 'has_next': page_obj.has_next()})