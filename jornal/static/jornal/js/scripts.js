document.addEventListener('DOMContentLoaded', () => {
    
    const allOptions = document.querySelectorAll('.newsletter-option');
    const selectedTopicsList = document.getElementById('selected-topics-list');
    const preferencesInput = document.getElementById('preferences-input'); 

    
    let selectedTopics = new Set();

    
    function renderSelectedTopics() {
        selectedTopicsList.innerHTML = ''; 

        if (selectedTopics.size === 0) {
            selectedTopicsList.innerHTML = '<p style="color: var(--muted); font-size: 14px; margin-top: 5px;">Nenhuma newsletter selecionada ainda.</p>';
        }

        selectedTopics.forEach(topicName => {
            const topicElement = document.createElement('div');
            topicElement.classList.add('selected-item');
            topicElement.setAttribute('data-topic-name', topicName);
            
            // Texto do item
            topicElement.innerHTML = `Conteúdo da sua Newsletter: ${topicName} `;
            
            // Botão de remoção (X)
            const removeSpan = document.createElement('span');
            removeSpan.classList.add('remove-topic');
            removeSpan.innerHTML = '&times;';
            
            // Adiciona o evento de remoção ao X
            removeSpan.addEventListener('click', () => {
                handleSelection(topicName, false); 
            });

            topicElement.appendChild(removeSpan);
            selectedTopicsList.appendChild(topicElement);
        });

        
        preferencesInput.value = Array.from(selectedTopics).join(',');
    }

    
    function handleSelection(topicName, isAdding) {
        
        const optionElement = document.querySelector(`.newsletter-option[data-topic="${topicName.toLowerCase().replace(/\s/g, '-')
                                                                                                                   .replace(/[^\w-]/g, '')}"]`);
        const button = optionElement ? optionElement.querySelector('.add-button') : null;

        if (isAdding) {
            selectedTopics.add(topicName);
            if (button) {
                button.textContent = 'Adicionado';
                button.classList.add('selected');
            }
        } else {
            selectedTopics.delete(topicName);
            if (button) {
                button.textContent = 'Adicionar';
                button.classList.remove('selected');
            }
        }

        
        renderSelectedTopics();
    }


    
    allOptions.forEach(option => {
        const button = option.querySelector('.add-button');
        const topicId = option.getAttribute('data-topic'); 
        
       
        const topicTitle = option.querySelector('h3').textContent.trim(); 

        button.addEventListener('click', (e) => {
            e.preventDefault();
            const isSelected = selectedTopics.has(topicTitle);
            
            if (isSelected) {
                
                handleSelection(topicTitle, false);
            } else {
                
                handleSelection(topicTitle, true);
            }
        });
    });
    
    
    handleSelection('Saúde e Bem-Estar', true);
    handleSelection('Blog do Torcedor', true);
    
    
    const form = document.getElementById('subscribe-form');
    form.addEventListener('submit', (e) => {
        
        
        if (selectedTopics.size === 0) {
            alert("Por favor, selecione pelo menos uma newsletter antes de concluir a inscrição.");
            e.preventDefault();
            return;
        }

    });
});