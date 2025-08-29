document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('categories-grid');
    if (!grid) return;

    const fetchAPI = async (endpoint) => {
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`);
        if (!response.ok) throw new Error(`Failed to fetch ${endpoint}`);
        return response.json();
    };

    const initialize = async () => {
        try {
            const categories = await fetchAPI('/api/categories');
            grid.innerHTML = ''; // Limpa o "loading"

            categories.forEach(category => {
                const card = document.createElement('a');
                // O link aponta para a página de ferramentas, com o filtro na URL
                card.href = `tools.html?category=${category.category}`;
                card.className = 'category-card';

                card.innerHTML = `
                    <div class="category-icon">
                        <span>${getIconForCategory(category.category)}</span>
                    </div>
                    <div class="category-info">
                        <h3>${formatCategoryName(category.category)}</h3>
                        <p>${category.tool_count} Tools</p>
                    </div>
                    <div class="category-arrow">&rarr;</div>
                `;
                grid.appendChild(card);
            });

        } catch (error) {
            console.error("Error loading categories:", error);
            grid.innerHTML = '<p>Failed to load categories.</p>';
        }
    };

    // Funções auxiliares para ícones e nomes
    const formatCategoryName = (name) => {
        return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };
    const getIconForCategory = (name) => {
        if (name.includes('image') || name.includes('arte') || name.includes('design')) return '🎨';
        if (name.includes('video')) return '🎬';
        if (name.includes('pesquisas') || name.includes('escrita')) return '✍️';
        if (name.includes('code') || name.includes('programacao')) return '💻';
        if (name.includes('music') || name.includes('voz')) return '🎵';
        if (name.includes('marketing')) return '📈';
        if (name.includes('produtividade')) return '⏱️';
        return '🤖';
    };

    initialize();
});