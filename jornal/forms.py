
from django import forms
from .models import Artigo
from django.contrib.auth.models import User 

class ArtigoForm(forms.ModelForm):
    class Meta:
        model = Artigo
        fields = ['titulo', 'subtitulo', 'conteudo', 'categoria', 'tags', 'destaque']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 15, 'placeholder': 'Conteúdo completo da notícia...'}),
            'subtitulo': forms.TextInput(attrs={'placeholder': 'Um breve resumo/subtítulo'}),
        }