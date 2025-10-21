from django import forms
from .models import NoticiaPersonalizada

class NoticiaPersonalizadaForm(forms.ModelForm):
    class Meta:
        model = NoticiaPersonalizada
        fields = ['autor', 'titulo', 'subtitulo', 'conteudo', 'categoria', 'imagem']
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Título principal da notícia'}),
            'subtitulo': forms.TextInput(attrs={'placeholder': 'Um breve resumo'}),
            'conteudo': forms.Textarea(attrs={'rows': 10}),
        }