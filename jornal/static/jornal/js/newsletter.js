function initNewsletterPage() {

    if (window.__newsletter_initialized__) return;
    window.__newsletter_initialized__ = true;

    const addButtons = document.querySelectorAll('.add-button');
    const selectedList = document.getElementById('selected-topics-list');
    const preferencesInput = document.getElementById('preferences-input');

    if (!addButtons.length || !selectedList || !preferencesInput) {
        return; // A página atual não é a newsletter
    }

    let selectedTopics = [];

    function updateHiddenInput() {
        preferencesInput.value = selectedTopics.join(',');
    }

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

    function addTopic(card) {
        const topicId = card.dataset.topic;
        const labelText = card.querySelector('h3').innerText.trim();
        const btn = card.querySelector('.add-button');

        if (selectedTopics.includes(topicId)) return;

        selectedTopics.push(topicId);
        updateHiddenInput();

        const newItem = createSelectedItemElement(topicId, labelText);
        selectedList.appendChild(newItem);

        btn.innerHTML = '<i class="bi bi-check-lg"></i> Adicionado';
        btn.style.backgroundColor = '#2ECC71';
        btn.style.cursor = 'default';
        btn.disabled = true;
    }

    function removeTopic(closeIcon) {
        const itemDiv = closeIcon.closest('.selected-item');
        const topicId = itemDiv.dataset.topicId;

        selectedTopics = selectedTopics.filter(t => t !== topicId);
        updateHiddenInput();

        itemDiv.remove();

        const cards = document.querySelectorAll('.newsletter-option');

        cards.forEach(card => {
            if (card.dataset.topic === topicId) {
                const btn = card.querySelector('.add-button');
                btn.innerHTML = '+ Adicionar';
                btn.style.backgroundColor = '';
                btn.style.cursor = 'pointer';
                btn.disabled = false;
            }
        });
    }

    addButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const card = this.closest('.newsletter-option');
            addTopic(card);
        });
    });

    selectedList.addEventListener('click', function(e) {
        const removeBtn = e.target.closest('.remove-topic');
        if (removeBtn) {
            removeTopic(removeBtn);
        }
    });
}

document.addEventListener("DOMContentLoaded", initNewsletterPage);

document.body.addEventListener("htmx:afterSwap", function(evt) {
    if (evt.detail.target.id === "main-content") {
        window.__newsletter_initialized__ = false; // permite reinicializar
        initNewsletterPage();
    }
});
