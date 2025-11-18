from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Tag")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.nome

class Artigo(models.Model):
    titulo = models.CharField(max_length=255, verbose_name="Título")
    subtitulo = models.CharField(
        max_length=300, 
        blank=True, 
        null=True, 
        verbose_name="Subtítulo/Resumo"
    )
    
    conteudo = models.TextField(verbose_name="Conteúdo")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="artigos")
    tags = models.ManyToManyField(Tag, related_name="artigos", blank=True)
    publicado_em = models.DateTimeField(default=timezone.now, verbose_name="Publicado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    destaque = models.BooleanField(default=False, verbose_name="Destaque na Home")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artigos")
    imagem = models.ImageField(upload_to="artigos/", null=True, blank=True)  # Adicionando campo imagem

    class Meta:
        verbose_name = "Artigo"
        verbose_name_plural = "Artigos"
        ordering = ['-publicado_em']

    def __str__(self):
        return self.titulo[:30]

    @classmethod
    def artigos_populares(cls, limite=5):
        return cls.objects.annotate(total=models.Count("recomendacoes_origem")) \
            .order_by("-total")[:limite]

    def artigos_relacionados(self, limite=3):
        tags_ids = self.tags.values_list('id', flat=True)
        recomendacoes_por_tag = Artigo.objects.filter(
            tags__in=tags_ids
        ).exclude(
            id=self.id 
        ).distinct().annotate(
            num_tags=Count('tags')
        ).order_by('-num_tags', '-publicado_em')[:limite]

        if len(recomendacoes_por_tag) >= limite:
            return recomendacoes_por_tag

        ids_ja_recomendados = list(recomendacoes_por_tag.values_list('id', flat=True))
        
        recomendacoes_por_categoria = Artigo.objects.filter(
            categoria=self.categoria
        ).exclude(
            id__in=ids_ja_recomendados
        ).exclude(
            id=self.id
        ).order_by('-publicado_em')[:limite - len(recomendacoes_por_tag)]

        recomendacoes_finais = list(recomendacoes_por_tag) + list(recomendacoes_por_categoria)
        
        return recomendacoes_finais[:limite]

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

    class Meta:
        verbose_name = "Recomendação"
        verbose_name_plural = "Recomendações"

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

    class Meta:
        verbose_name = "Conteúdo Multimídia"
        verbose_name_plural = "Conteúdos Multimídia"

    def __str__(self):
        return f"{self.tipo} - {self.titulo or self.url}"

class Anuncio(models.Model):
    titulo = models.CharField(max_length=255)
    imagem = models.ImageField(upload_to="anuncios/")
    url_destino = models.URLField()
    posicao = models.CharField(max_length=50, help_text="Ex.: entre artigos, sidebar, header")
    responsivo = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Anúncio"
        verbose_name_plural = "Anúncios"

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

    class Meta:
        verbose_name = "Assinante de Newsletter"
        verbose_name_plural = "Assinantes de Newsletter"

    def __str__(self):
        return f"{self.nome} ({self.email})"

    @classmethod
    def assinantes_por_categoria(cls, categoria_id):
        return cls.objects.filter(categorias__id=categoria_id)

class MenuLateral(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    url_customizada = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Item de Menu Lateral"
        verbose_name_plural = "Itens de Menu Lateral"
        ordering = ['ordem']

    def __str__(self):
        return self.nome