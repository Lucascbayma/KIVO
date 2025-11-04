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

class HistoriaOrganizacaoPortalTest(TestCase):
    """
    Como leitor do portal de notícias,
    Quero que a homepage e as páginas internas sejam estruturadas de forma clara e lógica,
    destacando as notícias mais relevantes e os temas locais,
    Para que eu encontre facilmente o que mais importa e continue explorando conteúdos de interesse sem me perder na navegação.
    """

    def setUp(self):
        self.user = User.objects.create(username="editor")
        self.cat_esportes = Categoria.objects.create(nome="Esportes")
        self.cat_politica = Categoria.objects.create(nome="Política")

        self.manchete = Artigo.objects.create(
            titulo="Crise Política Atual",
            conteudo="Notícia principal da editoria de política",
            categoria=self.cat_politica,
            autor=self.user,
            destaque=True
        )

        self.ultima_hora = Artigo.objects.create(
            titulo="Resultado da Partida de Ontem",
            conteudo="Notícia de última hora sobre esportes",
            categoria=self.cat_esportes,
            autor=self.user,
            destaque=False
        )

        self.complementar = Artigo.objects.create(
            titulo="Análise Pós-Jogo",
            conteudo="Análise detalhada do resultado esportivo",
            categoria=self.cat_esportes,
            autor=self.user,
            destaque=False
        )

    def test_cenario1_exploracao_intuitiva_homepage(self):
        """
        Cenário 1: Exploração intuitiva na homepage
        Dado que estou acessando a homepage do portal,
        Quando visualizo o layout principal,
        Então devo perceber claramente a separação entre notícias de última hora, destaques do dia e categorias temáticas,
        E essa organização deve me ajudar a identificar rapidamente o que quero ler sem precisar rolar excessivamente ou procurar manualmente.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('ultimas_noticias', context)
        self.assertIn('destaques', context)
        self.assertIn('categorias', context)
        self.assertTrue(len(context['destaques']) > 0)
        self.assertTrue(all(isinstance(cat, Categoria) for cat in context['categorias']))

    def test_cenario2_agrupamento_de_conteudo_por_relevancia(self):
        """
        Cenário 2: Agrupamento de conteúdo por relevância
        Dado que estou navegando em uma editoria específica (como política ou esportes),
        Quando acesso essa seção,
        Então devo visualizar as matérias organizadas por ordem de importância — como manchetes principais, análises e conteúdos complementares —,
        E isso deve facilitar a identificação do que é mais relevante sem precisar abrir cada matéria individualmente.
        """
        response = self.client.get(f'/categoria/{self.cat_esportes.pk}/')
        self.assertEqual(response.status_code, 200)
        artigos = response.context['artigos']
        self.assertGreaterEqual(len(artigos), 1)
        self.assertTrue(hasattr(artigos[0], 'titulo'))

    def test_cenario3_retorno_inesperado_a_homepage(self):
        """
        Cenário 3: Retorno inesperado à homepage
        Dado que estou lendo uma matéria em uma editoria específica,
        Quando clico acidentalmente no botão "voltar" do navegador ou retorno à homepage,
        Então o sistema deve manter a estrutura organizada e oferecer atalhos para que eu retorne rapidamente ao conteúdo que estava explorando,
        E não deve exigir que eu reinicie a navegação do zero.
        """
        artigo = self.manchete
        self.client.get(f'/artigo/{artigo.pk}/')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('atalhos', response.context)
        self.assertTrue(isinstance(response.context['atalhos'], list))

class HistoriaAnunciosIntegradosTest(TestCase):
    """
    Como leitor do portal de notícias,
    Quero que os anúncios apareçam de forma integrada e harmônica ao layout,
    Para que eu não tenha a experiência de leitura prejudicada por poluição visual,
    mas ainda permita a sustentabilidade do modelo de negócio.
    """

    def setUp(self):
        self.user = User.objects.create(username="redator")
        self.cat_esportes = Categoria.objects.create(nome="Esportes")
        self.cat_politica = Categoria.objects.create(nome="Política")

        self.artigo1 = Artigo.objects.create(
            titulo="Nova vitória do time local",
            conteudo="Detalhes da partida e reações dos torcedores",
            categoria=self.cat_esportes,
            autor=self.user
        )
        self.artigo2 = Artigo.objects.create(
            titulo="Entrevista com o técnico",
            conteudo="Análise sobre o desempenho da equipe",
            categoria=self.cat_esportes,
            autor=self.user
        )
        self.artigo3 = Artigo.objects.create(
            titulo="Decisões políticas da semana",
            conteudo="Resumo dos principais acontecimentos em Brasília",
            categoria=self.cat_politica,
            autor=self.user
        )

    def test_cenario1_insercao_sutil_de_anuncios_no_feed(self):
        """
        Cenário 1: Inserção de forma sutil de anúncios no feed
        Dado que estou navegando pela homepage ou páginas de categoria,
        Quando novos blocos de notícias são carregados,
        Então os anúncios devem aparecer de forma intercalada entre os conteúdos,
        mantendo o mesmo estilo visual, sem prejudicar a experiência.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertIn('anuncios', response.context)
        anuncios = response.context['anuncios']
        self.assertTrue(isinstance(anuncios, list))
        self.assertGreaterEqual(len(anuncios), 1)

        total_conteudo = len(response.context.get('ultimas', [])) + len(anuncios)
        proporcao = len(anuncios) / total_conteudo if total_conteudo else 0
        self.assertLessEqual(proporcao, 0.3, "Os anúncios não devem ocupar mais de 30% do feed")

    def test_cenario2_insercao_invasiva_de_anuncios(self):
        """
        Cenário 2: Inserção invasiva de anúncios (negativo)
        Dado que estou navegando pelo portal de notícias,
        Quando múltiplos anúncios são exibidos de forma destacada e com layout diferente do conteúdo,
        Então minha experiência de leitura é prejudicada por excesso de poluição visual.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        anuncios = response.context.get('anuncios', [])
        self.assertLess(len(anuncios), 5, "Excesso de anúncios prejudica a leitura")

    def test_cenario3_experiencia_responsiva(self):
        """
        Cenário 3: Experiência responsiva
        Dado que acesso o portal de diferentes dispositivos,
        Quando um anúncio é carregado,
        Então ele deve se adaptar ao tamanho da tela,
        mantendo legibilidade e harmonia com o layout em qualquer resolução.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        anuncios = response.context.get('anuncios', [])
        for anuncio in anuncios:
            self.assertIn('formato', anuncio)
            self.assertIn(anuncio['formato'], ['mobile', 'tablet', 'desktop'])