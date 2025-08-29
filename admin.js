document.addEventListener('DOMContentLoaded', () => {
    // --- CONFIGURAÇÃO ---
    const SECRET_KEY = "1620"; // Mude sua senha aqui!

    // --- ELEMENTOS ---
    const authSection = document.getElementById('auth-section');
    const contentSection = document.getElementById('content-section');
    const secretKeyInput = document.getElementById('secret-key');
    const authBtn = document.getElementById('auth-btn');
    const toolsListDiv = document.getElementById('tools-list');
    
    const addForm = {
        name: document.getElementById('name'),
        category: document.getElementById('category-input'),
        description: document.getElementById('description'),
        price: document.getElementById('price'),
        link: document.getElementById('link'),
        logo_url: document.getElementById('logo_url'),
        base_popularity: document.getElementById('base_popularity'),
        suggestions: document.getElementById('category-suggestions'),
        button: document.getElementById('add-tool-btn')
    };

    const batchForm = {
        textarea: document.getElementById('batch-data'),
        button: document.getElementById('batch-add-btn')
    };

    // --- FUNÇÕES DE API ---
    const fetchAPI = async (endpoint, options = {}) => {
        const response = await fetch(`http://127.0.0.1:5000${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`Erro na chamada API para ${endpoint}. Status: ${response.status}`);
        }
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json();
        }
    };

    // --- LÓGICA PRINCIPAL ---
    async function loadPageData() {
        try {
            const [tools, categories] = await Promise.all([
                fetchAPI('/api/tools'),
                fetchAPI('/api/categories')
            ]);
            renderTools(tools);
            renderCategorySuggestions(categories);
        } catch (error) {
            console.error("Falha ao carregar dados:", error);
            alert("Não foi possível carregar os dados. Verifique se o servidor Python está rodando.");
        }
    }

    function renderTools(tools) {
        toolsListDiv.innerHTML = '';
        tools.forEach(tool => {
            const item = document.createElement('div');
            item.className = 'tool-list-item';
            item.innerHTML = `
                <span><strong>${tool.name}</strong> (${tool.category}) - Votos: ${tool.votes}, Pop: ${tool.base_popularity}</span>
                <button class="delete-btn" data-id="${tool.id}">Deletar</button>
            `;
            toolsListDiv.appendChild(item);
        });
    }

    function renderCategorySuggestions(categories) {
        addForm.suggestions.innerHTML = '';
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            addForm.suggestions.appendChild(option);
        });
    }

    // --- FUNÇÕES DE EVENTOS ---
    function attemptLogin() {
        if (secretKeyInput.value === SECRET_KEY) {
            authSection.style.display = 'none';
            contentSection.style.display = 'block';
            loadPageData();
        } else {
            alert('Chave secreta incorreta!');
        }
    }

    async function addSingleTool() {
        const newTool = {
            name: addForm.name.value,
            category: addForm.category.value,
            description: addForm.description.value,
            price: addForm.price.value,
            link: addForm.link.value,
            logo_url: addForm.logo_url.value,
            base_popularity: addForm.base_popularity.value
        };
        if (!newTool.name || !newTool.link) return alert('Nome e Link são obrigatórios!');
        
        try {
            const result = await fetchAPI('/api/admin/tools/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newTool)
            });
            const feedback = result.logo_found ? "Ferramenta adicionada e logo encontrado!" : "Ferramenta adicionada, mas logo não encontrado.";
            alert(feedback);
            
            // Limpa o formulário
            addForm.name.value = '';
            addForm.category.value = '';
            addForm.description.value = '';
            addForm.price.value = '';
            addForm.link.value = '';
            addForm.logo_url.value = '';
            
            loadPageData();
        } catch (error) {
            console.error("Falha ao adicionar ferramenta:", error);
            alert("Não foi possível adicionar a ferramenta.");
        }
    }

    async function addBatchTools() {
        const data = batchForm.textarea.value;
        if (!data.trim()) return alert('A área de texto está vazia!');
        
        if (confirm('Tem certeza que deseja adicionar estas ferramentas em lote?')) {
            try {
                const result = await fetchAPI('/api/admin/tools/batch-add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data: data })
                });
                alert(`${result.tools_added} ferramentas processadas. ${result.logos_found} logos foram encontrados e baixados!`);
                batchForm.textarea.value = '';
                loadPageData();
            } catch (error) {
                console.error("Falha ao adicionar em lote:", error);
                alert("Ocorreu um erro ao adicionar as ferramentas em lote.");
            }
        }
    }

    async function deleteTool(event) {
        if (event.target.classList.contains('delete-btn')) {
            const toolId = event.target.dataset.id;
            if (confirm(`Tem certeza que deseja deletar esta ferramenta (ID: ${toolId})?`)) {
                try {
                    await fetchAPI(`/api/admin/tools/delete/${toolId}`, { method: 'DELETE' });
                    loadPageData(); 
                } catch (error) {
                    console.error('Falha ao deletar a ferramenta:', error);
                    alert('Não foi possível deletar a ferramenta.');
                }
            }
        }
    }

    // --- CONFIGURAÇÃO DOS EVENT LISTENERS ---
    authBtn.addEventListener('click', attemptLogin);
    secretKeyInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            attemptLogin();
        }
    });

    addForm.button.addEventListener('click', addSingleTool);
    batchForm.button.addEventListener('click', addBatchTools);
    toolsListDiv.addEventListener('click', deleteTool);
});