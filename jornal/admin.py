# Register your models here.
from django.contrib import admin
from .models import Categoria, Artigo 
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Artigo)
class ArtigoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria') 
    list_filter = ('categoria',)