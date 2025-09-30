from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    def __str__(self):
        return self.nome

class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Tag")

    def __str__(self):
        return self.nome

class Artigo(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título")
    conteudo = models.TextField(verbose_name="Conteúdo")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="artigos")
    tags = models.ManyToManyField(Tag, related_name="artigos", blank=True)
    publicado_em = models.DateTimeField(default=timezone.now, verbose_name="Publicado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    destaque = models.BooleanField(default=False, verbose_name="Destaque na Home")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artigos")

    def __str__(self):
        return self.titulo[:30]

    @classmethod
    def artigos_populares(cls, limite=5):
        """
        Retorna os artigos mais populares baseados em quantidade de recomendações.
        """
        return cls.objects.annotate(total=models.Count("recomendacoes")) \
            .order_by("-total")[:limite]

class Recomendacao(models.Model):
    artigo_origem = models.ForeignKey(
        Artigo,
        on_delete=models.CASCADE,
        related_name="recomendacoes_origem"
    )
    artigo_recomendado = models.ForeignKey(
        Artigo,
        on_delete=models.CASCADE,
        related_name="recomendacoes"
    )
    relevancia = models.FloatField(default=0.0, verbose_name="Relevância")

    def __str__(self):
        return f"{self.artigo_origem.titulo[:20]} → {self.artigo_recomendado.titulo[:20]}"

class ConteudoMultimidia(models.Model):
    TIPO_CHOICES = (
        ("video", "Vídeo"),
        ("audio", "Áudio"),
        ("radio", "Rádio Ao Vivo"),
    )
    artigo = models.ForeignKey(
        Artigo,
        on_delete=models.CASCADE,
        related_name="multimidias",
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    url = models.URLField()
    titulo = models.CharField(max_length=255, blank=True, null=True)
    duracao_segundos = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.titulo or self.url}"

class Anuncio(models.Model):
    titulo = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to="anuncios/")
    url_destino = models.URLField()
    posicao = models.CharField(max_length=50, help_text="Ex.: entre artigos, sidebar, header")
    responsivo = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Anúncio: {self.titulo}"

class AssinanteNewsletter(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assinaturas", null=True, blank=True)
    nome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    categorias = models.ManyToManyField(Categoria, related_name="assinantes")
    frequencia = models.CharField(
        max_length=20,
        choices=(("diaria", "Diária"), ("semanal", "Semanal")),
        default="diaria"
    )
    criado_em = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nome} ({self.email})"

    @classmethod
    def assinantes_por_categoria(cls, categoria_id):
        """
        Retorna todos os assinantes de uma categoria específica.
        """
        return cls.objects.filter(categorias__id=categoria_id)

class MenuLateral(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    url_customizada = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nome
