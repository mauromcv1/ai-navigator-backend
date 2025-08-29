document.addEventListener('DOMContentLoaded', () => {
    // Só executa se estivermos na página correta
    const grid = document.getElementById('ia-grid');
    if (!grid) return;

    // Seleção de todos os elementos da página
    const filter = document.getElementById('category-filter');
    const searchInput = document.getElementById('search-input');
    const toolCountSpan = document.getElementById('tool-count');
    const titleContainer = document.getElementById('dynamic-title-container');
    let allAiTools = [];
    let userFavorites = [];

    // --- FUNÇÃO ESSENCIAL QUE ESTAVA FALTANDO ---
    const fetchAPI = async (endpoint, options = {}) => {
        options.credentials = 'include';
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`, options);
        if (!response.ok) {
            if (response.status === 401) return null;
            const errorText = await response.text();
            throw new Error(`Network response was not ok for ${endpoint}. Server says: ${errorText}`);
        }
        return response.json();
    };
    
    // Funções para gerenciar o localStorage de votos
    const getUserVotes = () => JSON.parse(localStorage.getItem('user_votes')) || {};
    const recordVote = (toolId) => {
        const votes = getUserVotes();
        votes[toolId] = true;
        localStorage.setItem('user_votes', JSON.stringify(votes));
    };

    // Popula o dropdown de categorias
    const populateFilterDropdown = (categories) => {
        if (!filter || !Array.isArray(categories)) return;
        filter.innerHTML = '<option value="all">All Categories</option>';
        categories.forEach(categoryObj => {
            const option = document.createElement('option');
            option.value = categoryObj.category;
            option.textContent = categoryObj.category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            filter.appendChild(option);
        });
    };

    // Renderiza os cards das IAs na tela
    const displayTools = (tools) => {
        const userVotes = getUserVotes();
        grid.innerHTML = '';
        if (!tools || tools.length === 0) {
            grid.innerHTML = '<p>No tools found matching your criteria.</p>';
            return;
        }
        tools.forEach(tool => {
            const hasVoted = userVotes[tool.id];
            const isFavorited = userFavorites.includes(tool.id);
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
                        <button class="bookmark-btn ${isFavorited ? 'favorited' : ''}" data-id="${tool.id}" title="Add to Workspace">☆</button>
                    </div>
                    <p class="tool-description">${tool.description}</p>
                    <p class="price">Price: ${tool.price}</p>
                    <div class="vote-section">
                        <button class="like-btn" data-id="${tool.id}" ${hasVoted ? 'disabled' : ''}>👍</button>
                        <span id="votes-${tool.id}">${tool.votes}</span>
                        <button class="dislike-btn" data-id="${tool.id}" ${hasVoted ? 'disabled' : ''}>👎</button>
                    </div>
                </div>
            `;
            grid.appendChild(cardLink);
        });
    };

    // Aplica os filtros de categoria e busca
    const applyFilters = () => {
        const categoryValue = filter.value;
        const searchValue = searchInput.value.toLowerCase().trim();
        let filteredTools = allAiTools;
        if (categoryValue !== 'all') {
            filteredTools = filteredTools.filter(tool => tool.category === categoryValue);
        }
        if (searchValue) {
            filteredTools = filteredTools.filter(tool => tool.name.toLowerCase().includes(searchValue));
        }
        displayTools(filteredTools);
    };

    // Lida com todos os cliques dentro do grid (votos e bookmarks)
    const handleGridInteraction = async (event) => { /* ... (código completo que já te passei) ... */ };

    // Função principal que inicia a página
    const initialize = async () => {
        try {
            grid.innerHTML = '<p>Loading tools...</p>';
            const [categories, tools, favoritesData] = await Promise.all([
                fetchAPI('/api/categories'),
                fetchAPI('/api/tools'),
                fetchAPI('/api/favorites').catch(() => ({ favorites: [] }))
            ]);
            
            userFavorites = favoritesData ? favoritesData.favorites : [];
            
            if (toolCountSpan && tools) toolCountSpan.textContent = tools.length;
            
            populateFilterDropdown(categories);
            allAiTools = tools;
            
            const urlParams = new URLSearchParams(window.location.search);
            const categoryFromURL = urlParams.get('category');
            
            if (titleContainer) {
                if (categoryFromURL) {
                    const formattedCategoryName = categoryFromURL.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    titleContainer.innerHTML = `<h2 class="dynamic-category-title">Showing Tools for: ${formattedCategoryName}</h2>`;
                } else {
                    titleContainer.innerHTML = '';
                }
            }
            
            if (categoryFromURL) filter.value = categoryFromURL;
            
            applyFilters();
        } catch (error) {
            console.error('Error on tools page:', error);
            grid.innerHTML = `<p style="color: red;">${error.message}</p>`;
        }
    };

    // Configura os "ouvintes"
    if (filter) filter.addEventListener('change', applyFilters);
    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (grid) grid.addEventListener('click', handleGridInteraction);
    
    // Inicia tudo
    initialize();
});