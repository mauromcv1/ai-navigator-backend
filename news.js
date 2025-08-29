document.addEventListener('DOMContentLoaded', () => {
    const newsContainer = document.getElementById('news-container');
    if (!newsContainer) return;

    const initialize = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/news');
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            
            const articles = await response.json();
            newsContainer.innerHTML = '';

            const gridSizer = document.createElement('div');
            gridSizer.className = 'grid-sizer';
            newsContainer.appendChild(gridSizer);

            articles.forEach(article => {
                const articleCard = document.createElement('a');
                articleCard.className = 'news-card';
                articleCard.href = article.link;
                articleCard.target = '_blank';
                articleCard.rel = 'noopener noreferrer';
                articleCard.innerHTML = `
                    <img src="${article.image_url}" alt="" class="news-image">
                    <div class="news-content">
                        <h3>${article.title}</h3>
                        <div class="news-footer">
                            <p class="source"><strong>Fonte:</strong> ${article.source}</p>
                            <span class="published-date">${new Date(article.published).toLocaleDateString('pt-BR')}</span>
                        </div>
                    </div>
                `;
                newsContainer.appendChild(articleCard);
            });
            
            imagesLoaded(newsContainer, () => {
                new Masonry(newsContainer, {
                    itemSelector: '.news-card',
                    columnWidth: '.grid-sizer',
                    gutter: 20,
                    percentPosition: true
                });
            });

        } catch (error) {
            console.error("Erro ao buscar notícias:", error);
            newsContainer.innerHTML = '<p>Ocorreu um erro ao carregar o feed de notícias.</p>';
        }
    };

    initialize();
});