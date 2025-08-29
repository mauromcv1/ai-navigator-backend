document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('workspace-grid');
    if (!grid) return;

    const fetchAPI = async (endpoint, options = {}) => {
        options.credentials = 'include';
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`, options);
        if (!response.ok) {
            if (response.status === 401) window.location.href = 'login.html';
            throw new Error(`Network error for ${endpoint}`);
        }
        return response.json();
    };

    const displayTools = (tools) => {
        grid.innerHTML = '';
        if (!tools || tools.length === 0) {
            grid.innerHTML = '<h2>Your Workspace is Empty</h2><p>Click the star icon ⭐ on any tool to add it to your personal collection!</p>';
            return;
        }
        tools.forEach(tool => {
            const cardLink = document.createElement('a');
            cardLink.href = tool.link;
            cardLink.target = '_blank';
            cardLink.rel = 'noopener noreferrer';
            cardLink.className = 'ia-card-link';
            
            cardLink.innerHTML = `
                <div class="ia-card">
                    <div class="card-header">
                        <img src="${tool.logo_url || 'logos/news_placeholder.png'}" alt="" class="tool-logo">
                        <h2>${tool.name}</h2>
                        <!-- No Workspace, a estrela já vem favoritada -->
                        <button class="bookmark-btn favorited" data-id="${tool.id}" title="Remove from Workspace"></button>
                    </div>
                    <p class="tool-description">${tool.description}</p>
                    <p class="price">Price: ${tool.price}</p>
                    <!-- Não precisamos dos botões de voto no workspace -->
                </div>
            `;
            grid.appendChild(cardLink);
        });
    };

    const initialize = async () => {
        try {
            const favoriteTools = await fetchAPI('/api/favorites/tools');
            displayTools(favoriteTools);
        } catch (error) {
            console.error("Error loading workspace:", error);
            // O fetchAPI já redireciona se não estiver logado
        }
    };

    // Lógica para REMOVER do workspace
    grid.addEventListener('click', async (event) => {
        if (event.target.classList.contains('bookmark-btn')) {
            event.preventDefault();
            const toolId = event.target.dataset.id;
            if (confirm('Remove this tool from your Workspace?')) {
                await fetchAPI(`/api/favorites/toggle/${toolId}`, { method: 'POST' });
                // Recarrega a página para mostrar a lista atualizada
                window.location.reload();
            }
        }
    });

    initialize();
});