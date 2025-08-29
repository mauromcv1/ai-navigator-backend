document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('glossary-container');
    if (!container) return;

    const initialize = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/glossary');
            const terms = await response.json();
            if (terms.error) throw new Error(terms.error);

            container.innerHTML = '';
            
            // --- A ARMA NUCLEAR QUE FORÇA O GRID ---
            container.style.display = 'grid';
            container.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
            container.style.gap = '1.5rem';

            let currentLetter = '';
            terms.forEach(term => {
                //const firstLetter = term.term.charAt(0).toUpperCase();
                //if (firstLetter !== currentLetter) {
                //    currentLetter = firstLetter;
                //    const letterHeader = document.createElement('h2');
                //    letterHeader.className = 'letter-header';
                //    letterHeader.textContent = currentLetter;
                //    container.appendChild(letterHeader);
                //}
                const termCard = document.createElement('div');
                termCard.className = 'term-card';
                termCard.innerHTML = `
                    <h3>${term.term}</h3>
                    <p>${term.definition}</p>
                    <p class="example"><strong>Exemplo:</strong> <em>${term.example}</em></p>
                `;
                container.appendChild(termCard);
            });
        } catch (error) {
            console.error("Erro ao carregar o glossário:", error);
            container.innerHTML = `<p style="color: red;">Ocorreu um erro: ${error.message}</p>`;
        }
    };
    initialize();
});