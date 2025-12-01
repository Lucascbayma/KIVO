import os
# import git -> REMOVIDO DO TOPO PARA NÃO QUEBRAR O SITE SE FALTAR BIBLIOTECA
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView
from django.db.models import Q
import requests 
from django.http import Http404, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt 
from django.core.management import call_command 
from .models import Artigo, Categoria
from .forms import ArtigoForm
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.template.loader import render_to_string

# Chaves de API e URLs
NEWSDATA_API_KEY = settings.NEWSDATA_API_KEY 
NEWSDATA_API_URL = 'https://newsdata.io/api/1/news'

# =================================================================
# === WEBHOOK PARA DEPLOY AUTOMÁTICO (PythonAnywhere) ===
# =================================================================

@csrf_exempt
def webhook_github(request):
    """
    Recebe o sinal do GitHub Actions, puxa o código novo,
    roda as migrações e reinicia o servidor.
    """
    # Importação segura: só tenta carregar o git quando o deploy é chamado
    try:
        import git
    except ImportError:
        return JsonResponse({"status": "error", "message": "Biblioteca GitPython não instalada no servidor."}, status=500)

    if request.method == "POST":
        repo_path = settings.BASE_DIR

        try:
            # 1. Conectar ao repositório local e baixar mudanças
            repo = git.Repo(repo_path)
            origin = repo.remotes.origin
            origin.pull()
            
            # 2. Atualizar Banco de Dados
            call_command('migrate', interactive=False)
            
            # 3. Atualizar Arquivos Estáticos
            call_command('collectstatic', interactive=False)

            # 4. Forçar o Reload do Site
            wsgi_path = '/var/www/lucasbayma_pythonanywhere_com_wsgi.py'
            
            if os.path.exists(wsgi_path):
                os.utime(wsgi_path, None)
                return JsonResponse({"status": "success", "message": "Deploy realizado: Pull + Migrate + Reload."})
            else:
                return JsonResponse({"status": "warning", "message": "Pull feito, mas arquivo WSGI não encontrado."}, status=200)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "invalid method"}, status=405)


# =================================================================
# === VIEWS DE AUTENTICAÇÃO ===
# =================================================================

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
    # Define o nome padrão, mas vamos adicionar 'noticia' extra no contexto
    context_object_name = 'artigo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        artigo_atual = self.object

        # --- COMPATIBILIDADE ---
        # Passamos a variável com o nome 'noticia' para o template funcionar
        context['noticia'] = artigo_atual
        context['conteudo'] = artigo_atual 
        # ------------------------

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

    if not lista_noticias_api or not noticia_link:
        # Se não tiver dados, redireciona para home em vez de erro 404
        return redirect('home')

    noticia_encontrada = None

    for n in lista_noticias_api:
        if n.get('link') == noticia_link:
            noticia_encontrada = n
            break

    if noticia_encontrada is None:
        raise Http404("Notícia não encontrada na sessão.")

    # --- CORREÇÃO: PADRONIZAÇÃO DOS DADOS DA API ---
    # Convertemos as chaves da API (title, description) para as do BD (titulo, subtitulo)
    # Assim o template 'ler_noticia.html' funciona para os dois casos.
    
    autor_api = noticia_encontrada.get('creator')
    if isinstance(autor_api, list):
        autor_formatado = ", ".join(autor_api)
    else:
        autor_formatado = autor_api or noticia_encontrada.get('source_id')

    noticia_padronizada = {
        # Campos que o template espera (baseados no Model)
        'titulo': noticia_encontrada.get('title'),
        'subtitulo': noticia_encontrada.get('description'),
        'conteudo': noticia_encontrada.get('content') or noticia_encontrada.get('description'),
        'autor': autor_formatado,
        'publicado_em': noticia_encontrada.get('pubDate'),
        
        # Campos específicos da API
        'image_url': noticia_encontrada.get('image_url'),
        'link': noticia_encontrada.get('link'),
        'source_id': noticia_encontrada.get('source_id'),
        
        # Campos originais (backup)
        'title': noticia_encontrada.get('title'),
        'description': noticia_encontrada.get('description'),
    }

    # -------------------------
    # RECOMENDAÇÕES RELACIONADAS (API)
    # -------------------------
    categoria_atual = noticia_encontrada.get('category', [])
    if isinstance(categoria_atual, str):
        categoria_atual = [categoria_atual]

    categoria_atual = [c.lower() for c in categoria_atual]

    recomendacoes = []
    for n in lista_noticias_api:
        if n == noticia_encontrada:
            continue
        
        # Também padronizamos a recomendação para o card funcionar
        rec_padronizada = n.copy()
        rec_padronizada['titulo'] = n.get('title')

        categorias = n.get('category', [])
        if isinstance(categorias, str):
            categorias = [categorias]

        categorias = [c.lower() for c in categorias]

        if any(cat in categorias for cat in categoria_atual):
            recomendacoes.append(rec_padronizada)

        if len(recomendacoes) >= 3:
            break

    context = {
        # Aqui usamos 'noticia' com o objeto padronizado
        'noticia': noticia_padronizada, 
        'conteudo': noticia_padronizada,
        'recomendacoes': recomendacoes
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

    # Pega categorias do banco
    categorias = {c.nome.lower(): c.id for c in Categoria.objects.all()}
    
    # Busca artigos do banco
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
    
    # Mescla Banco + API
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
    
    # Fallback se não tiver nada
    if not context.get('ultimas'):
        context['ultimas'] = [
            {'title': 'Notícia de exemplo 1', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
            {'title': 'Notícia de exemplo 2', 'link': '#', 'description': 'Conteúdo simulado para testes.'},
        ]

    return render(request, 'home.html', context)

# -----------------------------------------------------------------
# --- VIEW PARA EXIBIÇÃO DE CATEGORIAS ESPECÍFICAS ---
# -----------------------------------------------------------------

def categoria_view(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    artigos = Artigo.objects.filter(categoria=categoria).order_by('-destaque', '-publicado_em')

    context = {
        'categoria': categoria,
        'artigos': artigos,
    }
    return render(request, 'categoria.html', context)

# -----------------------------------------------------------------
# --- VIEW PARA PÁGINA DE TODAS AS NOTÍCIAS ---
# -----------------------------------------------------------------

def todas_noticias(request):
    """Página com todas as notícias — inclui busca, filtro e ordenação."""
    categoria_nome = request.GET.get('categoria')
    busca = request.GET.get('q')
    ordenacao = request.GET.get('ordenar', '-publicado_em')  

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