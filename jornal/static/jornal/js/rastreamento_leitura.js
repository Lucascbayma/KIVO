const STORAGE_KEY = 'noticiaIncompleta'; 

function configurarRastreamentoSaida() {

    const body = document.getElementById('body-noticia');
    const linkFonte = document.getElementById('link-fonte-original');

    if (!body) return; 

    const noticiaTitulo = body.dataset.noticiaTitulo;
    const noticiaUrl = window.location.href; 

    sessionStorage.setItem(STORAGE_KEY, JSON.stringify({
        titulo: noticiaTitulo,
        url: noticiaUrl 
    }));

    if (linkFonte) {
        linkFonte.addEventListener('click', () => {

            sessionStorage.removeItem(STORAGE_KEY);
        });
    }
}

function exibirBannerContinuacao() {
    const banner = document.getElementById('banner-continuar-leitura');
    const tituloElement = document.getElementById('titulo-noticia-banner');
    const linkElement = document.getElementById('link-noticia-banner');
    const fecharBtn = document.getElementById('fechar-banner');
    const dadosSalvos = sessionStorage.getItem(STORAGE_KEY);
    
    const isCurrentPage = document.getElementById('body-noticia');
    if (!dadosSalvos || (isCurrentPage && JSON.parse(dadosSalvos).url === window.location.href)) {
        if (banner) banner.style.display = 'none';
        return;
    }

    try {
        const noticia = JSON.parse(dadosSalvos);
        
        if (banner && tituloElement && linkElement) {

            tituloElement.textContent = noticia.titulo;
            linkElement.href = noticia.url; 
            
            banner.style.display = 'flex';

            setTimeout(() => {
                banner.classList.add('visivel');
            }, 10); 

            fecharBtn.addEventListener('click', () => {
                banner.classList.remove('visivel');
                sessionStorage.removeItem(STORAGE_KEY);
            });
            

            linkElement.addEventListener('click', () => {
                sessionStorage.removeItem(STORAGE_KEY);
            });
        }
    } catch (e) {
        console.error("Erro ao carregar dados salvos:", e);
        sessionStorage.removeItem(STORAGE_KEY);
    }
}


document.addEventListener('DOMContentLoaded', () => {

    exibirBannerContinuacao();

    if (document.getElementById('body-noticia')) {
        configurarRastreamentoSaida();
    }
});