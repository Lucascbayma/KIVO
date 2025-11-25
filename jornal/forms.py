from django import forms
from .models import Artigo
from django.contrib.auth.models import User 

class ArtigoForm(forms.ModelForm):
    class Meta:
        model = Artigo
        # Importante: incluí 'imagem' e 'video' nesta lista
        fields = [
            'titulo', 
            'subtitulo', 
            'conteudo', 
            'categoria', 
            'tags', 
            'destaque', 
            'imagem', 
            'video'
        ]
        
        widgets = {
            'conteudo': forms.Textarea(attrs={
                'rows': 15, 
                'placeholder': 'Escreva o conteúdo completo da notícia aqui...'
            }),
            'subtitulo': forms.TextInput(attrs={
                'placeholder': 'Um breve resumo que aparecerá abaixo do título'
            }),
            'titulo': forms.TextInput(attrs={
                'placeholder': 'Manchete Principal'
            }),
        }