// Chic & Chat - Main JavaScript

// Global state
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing...');
    setupEventListeners();
    checkAuth();
});

// Setup event listeners
function setupEventListeners() {
    // Login button
    const loginBtn = document.getElementById('loginBtn');
    if (loginBtn) {
        loginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal('loginModal');
        });
    }

    // Register button
    const registerBtn = document.getElementById('registerBtn');
    if (registerBtn) {
        registerBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openModal('registerModal');
        });
    }

    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Register form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}

// Modal functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Close modal on background click
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// Auth functions
async function checkAuth() {
    console.log('Checking auth, token:', authToken);
    
    if (!authToken) {
        updateNavForGuest();
        return;
    }

    try {
        const response = await fetch('/api/v1/auth/me', {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            window.currentUser = currentUser;
            window.authToken = authToken;
            console.log('User authenticated:', currentUser);
            updateNavForUser();
        } else {
            console.log('Auth failed, logging out');
            logout();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        logout();
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            window.authToken = authToken;
            
            await checkAuth();
            closeModal('loginModal');
            showAlert('Успешный вход! 💕', 'success');
            
            // Reload page to update content
            setTimeout(() => window.location.reload(), 500);
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Ошибка входа', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Ошибка подключения', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, username, password })
        });

        if (response.ok) {
            closeModal('registerModal');
            showAlert('Регистрация успешна! Теперь войдите в систему 🎉', 'success');
            
            // Auto-fill login form
            document.getElementById('loginUsername').value = username;
            setTimeout(() => openModal('loginModal'), 1000);
        } else {
            const error = await response.json();
            showAlert(error.detail || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showAlert('Ошибка подключения', 'error');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    window.authToken = null;
    window.currentUser = null;
    localStorage.removeItem('authToken');
    updateNavForGuest();
    window.location.href = '/';
}

// Update navigation based on auth state
function updateNavForUser() {
    const nav = document.querySelector('.nav');
    if (nav) {
        nav.innerHTML = `
            <a href="/">Главная</a>
            <a href="/posts">Посты</a>
            <a href="/users">Авторы</a>
            <a href="/bookmarks">Закладки</a>
            <a href="/create-post" class="btn">Написать пост</a>
            <a href="/profile/${currentUser.id}">Профиль</a>
            <a href="#" onclick="logout()" style="color: var(--text-light);">Выйти</a>
        `;
    }
}

function updateNavForGuest() {
    const nav = document.querySelector('.nav');
    if (nav) {
        nav.innerHTML = `
            <a href="/">Главная</a>
            <a href="/posts">Посты</a>
            <a href="/users">Авторы</a>
            <a href="#" id="loginBtn">Войти</a>
            <a href="#" id="registerBtn" class="btn">Регистрация</a>
        `;
        
        // Re-attach event listeners
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) {
            loginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                openModal('loginModal');
            });
        }
        
        const registerBtn = document.getElementById('registerBtn');
        if (registerBtn) {
            registerBtn.addEventListener('click', (e) => {
                e.preventDefault();
                openModal('registerModal');
            });
        }
    }
}

// Alert function
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    alertDiv.style.animation = 'fadeIn 0.3s ease';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transition = 'opacity 0.5s ease';
        setTimeout(() => alertDiv.remove(), 500);
    }, 3000);
}

// API helper function
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (!response.ok && response.status === 401) {
        logout();
        throw new Error('Unauthorized');
    }

    return response;
}

// Export functions for use in other scripts
window.apiRequest = apiRequest;
window.showAlert = showAlert;
window.openModal = openModal;
window.closeModal = closeModal;
window.logout = logout;
window.currentUser = currentUser;
window.authToken = authToken;

console.log('Main.js loaded successfully!');
