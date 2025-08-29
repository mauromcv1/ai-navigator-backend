document.addEventListener('DOMContentLoaded', () => {
    // Função genérica e segura para chamar a API
    const fetchWithCreds = async (url, options = {}) => {
        const defaultOptions = { credentials: 'include' };
        const finalOptions = { ...defaultOptions, ...options };
        const response = await fetch(url, finalOptions);
        if (!response.ok) {
            // Se o erro for 401 (não autorizado), não quebra o script, retorna null
            if (response.status === 401) return null;
            throw new Error(`Network error for ${url}`);
        }
        return response.json();
    };

    // --- LÓGICA DE SESSÃO DO USUÁRIO (UNIVERSAL) ---
    const nav = document.querySelector('.header-nav');
    if (nav) {
        (async () => {
            const data = await fetchWithCreds('http://127.0.0.1:5000/api/status');
            const referenceNode = nav.querySelector('.font-controls');
            if (referenceNode) {
                // Remove botões antigos para não duplicar
                nav.querySelector('#login-link')?.remove();
                nav.querySelector('#register-link')?.remove();
                nav.querySelector('#workspace-link')?.remove();
                nav.querySelector('#logout-link')?.remove();

                if (data && data.logged_in) {
                    const loggedInHTML = `
                        <a href="workspace.html" id="workspace-link" class="header-link">${data.username}'s Workspace</a>
                        <a href="#" id="logout-link" class="header-link">Logout</a>
                    `;
                    referenceNode.insertAdjacentHTML('beforebegin', loggedInHTML);
                    
                    const logoutLink = document.getElementById('logout-link');
                    if (logoutLink) {
                        logoutLink.addEventListener('click', async (e) => {
                            e.preventDefault();
                            await fetchWithCreds('http://127.0.0.1:5000/api/logout', { method: 'POST' });
                            window.location.reload();
                        });
                    }
                } else {
                    const loggedOutHTML = `
                        <a href="login.html" id="login-link" class="header-link">Login</a>
                        <a href="register.html" id="register-link" class="header-link">Register</a>
                    `;
                    referenceNode.insertAdjacentHTML('beforebegin', loggedOutHTML);
                }
            }
        })();
    }
    // --- LÓGICA DE TEMA (UNIVERSAL) ---
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const applyTheme = (theme) => {
            document.body.classList.toggle('dark-mode', theme === 'dark');
            themeToggle.textContent = theme === 'dark' ? '☀️' : '🌙';
        };
        themeToggle.addEventListener('click', () => {
            const newTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            applyTheme(newTheme);
        });
        applyTheme(localStorage.getItem('theme') || 'light');
    }

    // --- LÓGICA DE FONTE (UNIVERSAL) ---
    const fontDecreaseBtn = document.getElementById('font-decrease');
    const fontResetBtn = document.getElementById('font-reset');
    const fontIncreaseBtn = document.getElementById('font-increase');
    if (fontDecreaseBtn && fontResetBtn && fontIncreaseBtn) {
        const rootElement = document.documentElement;
        const FONT_SIZES = [0.875, 1.0, 1.125, 1.25];
        let currentFontIndex = 1;
        const applyFontSize = () => {
            rootElement.style.fontSize = `${FONT_SIZES[currentFontIndex]}rem`;
            fontDecreaseBtn.disabled = (currentFontIndex === 0);
            fontIncreaseBtn.disabled = (currentFontIndex === FONT_SIZES.length - 1);
        };
        fontIncreaseBtn.addEventListener('click', () => { if (currentFontIndex < FONT_SIZES.length - 1) { currentFontIndex++; applyFontSize(); } });
        fontDecreaseBtn.addEventListener('click', () => { if (currentFontIndex > 0) { currentFontIndex--; applyFontSize(); } });
        fontResetBtn.addEventListener('click', () => { currentFontIndex = 1; applyFontSize(); });
        applyFontSize();
    }
   
});