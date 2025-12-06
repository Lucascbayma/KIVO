document.addEventListener('DOMContentLoaded', function() {
    
    // Elementos do DOM
    const addButtons = document.querySelectorAll('.add-button');
    const selectedList = document.getElementById('selected-topics-list');
    const preferencesInput = document.getElementById('preferences-input');
    
    // Array para armazenar os nomes das newsletters selecionadas
    let selectedTopics = [];

    // --- FUNÇÕES AUXILIARES ---

    // Atualiza o input hidden que será enviado para o Django (views.py)
    function updateHiddenInput() {
        // Transforma o array em string separada por vírgulas (ex: "Política,Esportes")
        preferencesInput.value = selectedTopics.join(',');
    }

    // Cria o HTML do retângulo (baseado no seu CSS)
    function createSelectedItemElement(topicName) {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('selected-item');
        itemDiv.setAttribute('data-topic-name', topicName);
        
        // Estrutura interna: Texto + Botão X
        itemDiv.innerHTML = `
            ${topicName}
            <span class="remove-topic" role="button" aria-label="Remover">
                <i class="bi bi-x-lg"></i>
            </span>
        `;
        return itemDiv;
    }

    // --- AÇÕES ---

    // 1. Função de Adicionar
    function addTopic(card) {
        const topicName = card.querySelector('h3').innerText.trim();
        const btn = card.querySelector('.add-button');

        // Verifica se já foi adicionado
        if (selectedTopics.includes(topicName)) return;

        // Adiciona ao array e atualiza input
        selectedTopics.push(topicName);
        updateHiddenInput();

        // Cria e adiciona o elemento visual na lista
        const newItem = createSelectedItemElement(topicName);
        selectedList.appendChild(newItem);

        // Feedback Visual no Botão (Muda para Verde e Desabilita)
        btn.innerHTML = '<i class="bi bi-check-lg"></i> Adicionado';
        btn.style.backgroundColor = '#2ECC71'; // Verde sucesso
        btn.style.cursor = 'default';
        btn.disabled = true;
    }

    // 2. Função de Remover
    function removeTopic(closeIcon) {
        // Encontra o elemento pai (o retângulo cinza)
        const itemDiv = closeIcon.closest('.selected-item');
        const topicName = itemDiv.getAttribute('data-topic-name');

        // Remove do array e atualiza input
        selectedTopics = selectedTopics.filter(t => t !== topicName);
        updateHiddenInput();

        // Remove do HTML
        itemDiv.remove();

        // Reabilita o botão "Adicionar" original
        const cards = document.querySelectorAll('.newsletter-option');
        cards.forEach(card => {
            if (card.querySelector('h3').innerText.trim() === topicName) {
                const btn = card.querySelector('.add-button');
                btn.innerHTML = '+ Adicionar'; // Volta o texto original
                btn.style.backgroundColor = ''; // Remove a cor inline (volta para o CSS original/vermelho)
                btn.style.cursor = 'pointer';
                btn.disabled = false;
            }
        });
    }

    // --- EVENT LISTENERS (Gatilhos) ---

    // Clique nos botões de adicionar
    addButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault(); // Evita recarregar a página
            const card = this.closest('.newsletter-option');
            addTopic(card);
        });
    });

    // Clique no X para remover (Delegação de evento)
    selectedList.addEventListener('click', function(e) {
        // Verifica se clicou no span .remove-topic ou no icone i dentro dele
        const removeBtn = e.target.closest('.remove-topic');
        if (removeBtn) {
            removeTopic(removeBtn);
        }
    });

});