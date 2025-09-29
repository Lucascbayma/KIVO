from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Tag(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome


class Artigo(models.Model):
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="artigos")
    tags = models.ManyToManyField(Tag, related_name="artigos", blank=True)
    publicado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    destaque = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo

class Recomendacao(models.Model):
    artigo_origem = models.ForeignKey(Artigo, on_delete=models.CASCADE, related_name="recomendacoes_origem")
    artigo_recomendado = models.ForeignKey(Artigo, on_delete=models.CASCADE, related_name="recomendacoes")
    relevancia = models.FloatField(default=0.0)  # pode ser calculado via tags/categorias

    def __str__(self):
        return f"Recomendação para {self.artigo_origem} → {self.artigo_recomendado}"

class ConteudoMultimidia(models.Model):
    TIPO_CHOICES = (
        ("video", "Vídeo"),
        ("audio", "Áudio"),
        ("radio", "Rádio Ao Vivo"),
    )
    artigo = models.ForeignKey(Artigo, on_delete=models.CASCADE, related_name="multimidias", null=True, blank=True)
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
        return self.titulo

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
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assinante: {self.nome} ({self.email})"

class MenuLateral(models.Model):
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)
    url_customizada = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nome
