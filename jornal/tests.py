from django.test import TestCase
from django.contrib.auth.models import User
from .models import Artigo, Categoria, Tag

class HistoriaRecomendacoesContextuaisTest(TestCase):
    """
    História de Usuário:
    Como leitor de notícias no site,
    quero visualizar recomendações contextuais de artigos relacionados ao que estou lendo,
    para descobrir novos conteúdos de interesse, aumentar meu engajamento e continuar navegando sem esforço.
    """

    def setUp(self):
        self.user = User.objects.create(username="autor")
        self.cat_esportes = Categoria.objects.create(nome="Esportes")
        self.cat_moda = Categoria.objects.create(nome="Moda")
        self.tag_futebol = Tag.objects.create(nome="futebol")
        self.tag_corrida = Tag.objects.create(nome="corrida")

        self.artigo_principal = Artigo.objects.create(
            titulo="Notícia Principal de Esportes",
            conteudo="Conteúdo sobre futebol e esportes em geral",
            categoria=self.cat_esportes,
            autor=self.user
        )
        self.artigo_principal.tags.add(self.tag_futebol)

        self.rel1 = Artigo.objects.create(
            titulo="Partida de Futebol Hoje",
            conteudo="Notícia sobre futebol",
            categoria=self.cat_esportes,
            autor=self.user
        )
        self.rel1.tags.add(self.tag_futebol)

        self.rel2 = Artigo.objects.create(
            titulo="Maratona Nacional",
            conteudo="Notícia sobre corrida",
            categoria=self.cat_esportes,
            autor=self.user
        )
        self.rel2.tags.add(self.tag_corrida)

        self.rel3 = Artigo.objects.create(
            titulo="Treino da Seleção",
            conteudo="Cobertura esportiva",
            categoria=self.cat_esportes,
            autor=self.user
        )

        self.irrelevante = Artigo.objects.create(
            titulo="Tendências de Moda Verão",
            conteudo="Conteúdo de moda e estilo",
            categoria=self.cat_moda,
            autor=self.user
        )

    def test_cenario1_exibicao_de_recomendacoes_relacionadas(self):
        """
        Cenário 1: Exibição de recomendações relacionadas
        Dado que estou na página de leitura de uma notícia,
        Quando acesso o final do conteúdo,
        Então devo visualizar pelo menos 3 recomendações de artigos relacionados,
        baseados em tags e categorias do artigo atual.
        """
        response = self.client.get(f'/artigo/{self.artigo_principal.pk}/')
        self.assertEqual(response.status_code, 200)
        recomendacoes = response.context['recomendacoes']
        self.assertGreaterEqual(len(recomendacoes), 3)
        for rec in recomendacoes:
            mesma_categoria = rec.categoria == self.artigo_principal.categoria
            tags_em_comum = set(rec.tags.all()).intersection(self.artigo_principal.tags.all())
            self.assertTrue(mesma_categoria or tags_em_comum)

    def test_cenario2_relevancia_das_recomendacoes(self):
        """
        Cenário 2: Relevância das recomendações
        Dado que estou lendo uma notícia da categoria "Esportes",
        Quando chego ao final da página,
        Então as recomendações devem priorizar conteúdos da mesma categoria ou de tags semelhantes,
        E não devem incluir artigos sem relação direta com o tema.
        """
        recomendacoes = self.artigo_principal.artigos_relacionados(limite=3)
        for rec in recomendacoes:
            relacao_valida = (
                rec.categoria == self.artigo_principal.categoria or
                set(rec.tags.all()).intersection(self.artigo_principal.tags.all())
            )
            self.assertTrue(relacao_valida)

    def test_cenario3_recomendacoes_irrelevantes_exibidas(self):
        """
        Cenário 3: Recomendações irrelevantes exibidas (negativo)
        Dado que estou lendo uma notícia da categoria "Esportes",
        Quando chego ao final da página,
        Então não devo visualizar recomendações de artigos que não têm relação com a categoria
        ou tags da notícia atual (ex.: 'Economia' ou 'Moda'),
        pois isso prejudica minha experiência de navegação.
        """
        recomendacoes = self.artigo_principal.artigos_relacionados(limite=3)
        for rec in recomendacoes:
            self.assertNotEqual(rec.categoria, self.cat_moda)
