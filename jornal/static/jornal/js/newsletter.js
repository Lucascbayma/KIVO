function initNewsletterPage() {

    // Evita inicialização múltipla
    if (window.__newsletter_initialized__) return;
    window.__newsletter_initialized__ = true;

    const addButtons = document.querySelectorAll('.add-button');
    const selectedList = document.getElementById('selected-topics-list');
    const preferencesInput = document.getElementById('preferences-input');
    const form = document.getElementById('subscribe-form');
    const overlay = document.getElementById('success-overlay');

    // Se a página não tiver esses elementos, sai da função
    if (!addButtons.length || !selectedList || !preferencesInput) {
        return; 
    }

    let selectedTopics = [];

    // --- FUNÇÕES AUXILIARES ---

    function updateHiddenInput() {
        preferencesInput.value = selectedTopics.join(',');
    }

    // Função que altera o visual do botão (Toggle Vermelho/Preto)
    function updateButtonVisual(btn, isAdded) {
        if (isAdded) {
            btn.innerHTML = '- Remover';
            btn.classList.add('added'); // Fica PRETO
        } else {
            btn.innerHTML = '+ Adicionar';
            btn.classList.remove('added'); // Volta a VERMELHO
        }
    }

    // Cria o item visual na lista de baixo
    function createSelectedItemElement(topicId, labelText) {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('selected-item');
        itemDiv.setAttribute('data-topic-id', topicId);
        
        itemDiv.innerHTML = `
            ${labelText}
            <span class="remove-topic" role="button" aria-label="Remover">
                <i class="bi bi-x-lg"></i>
            </span>
        `;
        return itemDiv;
    }

    // Função para Adicionar Tópico
    function addTopic(card) {
        const topicId = card.dataset.topic; // Pega o atributo data-topic do HTML
        const labelText = card.querySelector('h3').innerText.trim();
        const btn = card.querySelector('.add-button');

        // Se já existe no array, não faz nada
        if (selectedTopics.includes(topicId)) return;

        // 1. Adiciona dados
        selectedTopics.push(topicId);
        updateHiddenInput();

        // 2. Cria visualmente na lista
        const newItem = createSelectedItemElement(topicId, labelText);
        selectedList.appendChild(newItem);

        // 3. Atualiza botão para Preto e Texto "- Remover"
        updateButtonVisual(btn, true);
    }

    // Função para Remover Tópico
    function removeTopic(topicId) {
        // 1. Remove dados
        selectedTopics = selectedTopics.filter(t => t !== topicId);
        updateHiddenInput();

        // 2. Remove visualmente da lista de baixo
        const itemDiv = selectedList.querySelector(`.selected-item[data-topic-id="${topicId}"]`);
        if (itemDiv) itemDiv.remove();

        // 3. Encontra o botão original e reverte para Vermelho
        const cards = document.querySelectorAll('.newsletter-option');
        cards.forEach(card => {
            if (card.dataset.topic === topicId) {
                const btn = card.querySelector('.add-button');
                updateButtonVisual(btn, false);
            }
        });
    }

    // --- EVENT LISTENERS ---

    // 1. Clique nos botões (+ Adicionar / - Remover)
    addButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const card = this.closest('.newsletter-option');
            const topicId = card.dataset.topic;

            // Lógica Toggle: se já tem, remove; se não tem, adiciona
            if (selectedTopics.includes(topicId)) {
                removeTopic(topicId);
            } else {
                addTopic(card);
            }
        });
    });

    // 2. Clique no 'X' da lista de selecionados
    selectedList.addEventListener('click', function(e) {
        const removeBtn = e.target.closest('.remove-topic');
        if (removeBtn) {
            const itemDiv = removeBtn.closest('.selected-item');
            const topicId = itemDiv.dataset.topicId;
            removeTopic(topicId);
        }
    });

    // 3. Envio do Formulário (Validação e Overlay)
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            if (selectedTopics.length === 0) {
                alert("Por favor, selecione pelo menos uma newsletter.");
                return;
            }

            // Mostra o Overlay Preto
            if (overlay) overlay.classList.add('visible');

            // Espera 2 segundos e envia
            setTimeout(function() {
                form.submit();
            }, 2000);
        });
    }
}

// Inicializa quando o DOM carrega
document.addEventListener("DOMContentLoaded", initNewsletterPage);

// Re-inicializa se usar HTMX
document.body.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "main-content") {
        window.__newsletter_initialized__ = false; 
        initNewsletterPage();
    }
});