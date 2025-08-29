document.addEventListener('DOMContentLoaded', () => {
    // Seleciona os DOIS containers da home page
    const popularGrid = document.querySelector('#popular-tools-section .ia-grid');
    const newGrid = document.querySelector('#new-tools-section .ia-grid');

    // Função genérica de API
    const fetchAPI = async (endpoint) => {
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`);
        if (!response.ok) throw new Error(`Failed to fetch ${endpoint}`);
        return response.json();
    };

    // Função para renderizar os cards em um grid específico
    const renderToolsInGrid = (gridElement, tools) => {
        if (!gridElement) return;
        gridElement.innerHTML = ''; // Limpa a mensagem de "loading"

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
                    </div>
                    <p class="tool-description">${tool.description}</p>
                    <p class="price">Price: ${tool.price}</p>
                </div>`;
            gridElement.appendChild(cardLink);
        });
    };

    // Função principal que carrega a página
    const loadHomePage = async () => {
        // Verifica se estamos na home page
        if (!popularGrid || !newGrid) return; 

        try {
            // Busca as IAs populares e as novas em paralelo
            const [popularTools, newTools] = await Promise.all([
                fetchAPI('/api/tools'),
                fetchAPI('/api/tools/newest')
            ]);
            
            // Renderiza os 12 mais populares no grid de populares
            renderToolsInGrid(popularGrid, popularTools.slice(0, 12));
            
            // Renderiza os 12 mais novos no grid de novos
            renderToolsInGrid(newGrid, newTools);

        } catch (error) {
            console.error("Error loading home page:", error);
            popularGrid.innerHTML = '<p>Could not load popular tools.</p>';
            newGrid.innerHTML = '<p>Could not load new tools.</p>';
        }
    };

    // Inicia a aplicação
    loadHomePage();
});