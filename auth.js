document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const messageArea = document.getElementById('message-area');

    const handleFormSubmit = async (url, body) => {
        try {
            const response = await fetch(url, {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            return await response.json();
        } catch (error) {
            return { success: false, message: 'Network error. Please try again.' };
        }
    };

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = loginForm.querySelector('#username').value;
            const password = loginForm.querySelector('#password').value;
            const data = await handleFormSubmit('http://127.0.0.1:5000/api/login', { username, password });
            
            if (data.success) {
                window.location.href = 'index.html';
            } else {
                messageArea.textContent = data.message;
                messageArea.style.color = 'red';
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = registerForm.querySelector('#username').value;
            const email = registerForm.querySelector('#email').value; // <-- Pega o novo campo
            const password = registerForm.querySelector('#password').value;

            // Envia o email junto no corpo da requisição
            const data = await handleFormSubmit('http://127.0.0.1:5000/api/register', { username, email, password });

            messageArea.textContent = data.message;
            // ... (o resto da lógica continua igual)
        });
    }
});