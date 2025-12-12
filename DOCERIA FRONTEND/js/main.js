/**
 * Main JavaScript - Funcionalidades principais
 */

document.addEventListener('DOMContentLoaded', () => {
    initSlider();
    initMobileMenu();
    initSearch();
    initBackToTop();
    loadCategories();
    loadProducts();
    initAuthUI();
});

/**
 * Hero Slider
 */
function initSlider() {
    const slidesContainer = document.getElementById('slidesContainer');
    const slides = document.querySelectorAll('.slide');
    const prevBtn = document.getElementById('prevSlide');
    const nextBtn = document.getElementById('nextSlide');
    const dotsContainer = document.getElementById('sliderDots');
    
    if (!slidesContainer || slides.length === 0) return;
    
    let currentSlide = 0;
    const totalSlides = slides.length;
    let autoPlayInterval;
    
    // Cria os dots
    slides.forEach((_, index) => {
        const dot = document.createElement('span');
        dot.className = `dot ${index === 0 ? 'active' : ''}`;
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });
    
    const dots = dotsContainer.querySelectorAll('.dot');
    
    function goToSlide(index) {
        slides[currentSlide].classList.remove('active');
        dots[currentSlide].classList.remove('active');
        
        currentSlide = (index + totalSlides) % totalSlides;
        
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
        slidesContainer.style.transform = `translateX(-${currentSlide * 100}%)`;
    }
    
    function nextSlide() {
        goToSlide(currentSlide + 1);
    }
    
    function prevSlide() {
        goToSlide(currentSlide - 1);
    }
    
    // Event listeners
    nextBtn?.addEventListener('click', () => {
        nextSlide();
        resetAutoPlay();
    });
    
    prevBtn?.addEventListener('click', () => {
        prevSlide();
        resetAutoPlay();
    });
    
    // Autoplay
    function startAutoPlay() {
        autoPlayInterval = setInterval(nextSlide, 5000);
    }
    
    function resetAutoPlay() {
        clearInterval(autoPlayInterval);
        startAutoPlay();
    }
    
    startAutoPlay();
    
    // Pause on hover
    slidesContainer.addEventListener('mouseenter', () => clearInterval(autoPlayInterval));
    slidesContainer.addEventListener('mouseleave', startAutoPlay);
}

/**
 * Mobile Menu
 */
function initMobileMenu() {
    const menuBtn = document.getElementById('mobileMenuBtn');
    const navMenu = document.getElementById('navMenu');
    
    if (!menuBtn || !navMenu) return;
    
    menuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('active');
        menuBtn.querySelector('i').classList.toggle('fa-bars');
        menuBtn.querySelector('i').classList.toggle('fa-times');
    });
    
    // Fecha menu ao clicar em um link
    navMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            menuBtn.querySelector('i').classList.add('fa-bars');
            menuBtn.querySelector('i').classList.remove('fa-times');
        });
    });
}

/**
 * Search Overlay
 */
function initSearch() {
    const searchBtn = document.getElementById('searchBtn');
    const searchOverlay = document.getElementById('searchOverlay');
    const searchClose = document.getElementById('searchClose');
    const searchInput = document.getElementById('searchInput');
    
    if (!searchBtn || !searchOverlay) return;
    
    searchBtn.addEventListener('click', () => {
        searchOverlay.classList.add('active');
        searchInput?.focus();
    });
    
    searchClose?.addEventListener('click', () => {
        searchOverlay.classList.remove('active');
    });
    
    // Fecha ao clicar fora
    searchOverlay.addEventListener('click', (e) => {
        if (e.target === searchOverlay) {
            searchOverlay.classList.remove('active');
        }
    });
    
    // Fecha com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && searchOverlay.classList.contains('active')) {
            searchOverlay.classList.remove('active');
        }
    });
    
    // Busca
    searchInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `pages/doceria.html?search=${encodeURIComponent(query)}`;
            }
        }
    });
}

/**
 * Back to Top Button
 */
function initBackToTop() {
    const backToTop = document.getElementById('backToTop');
    
    if (!backToTop) return;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 500) {
            backToTop.classList.add('visible');
        } else {
            backToTop.classList.remove('visible');
        }
    });
    
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Auth UI bindings
 */
function initAuthUI() {
    const accountButtons = document.querySelectorAll('.account-btn');
    const protectedButtons = document.querySelectorAll('[data-requires-auth]');
    if (!accountButtons.length && !protectedButtons.length) return;

    const isPagesFolder = window.location.pathname.includes('/pages/');
    const loginHref = isPagesFolder ? 'login.html' : 'pages/login.html';

    accountButtons.forEach(btn => {
        if (!btn.dataset.loginHref) {
            btn.dataset.loginHref = btn.getAttribute('href') || loginHref;
        }
    });

    function getUserDisplayName(user) {
        if (!user) return 'Minha conta';
        if (user.nome) return `Olá, ${user.nome}`;
        if (user.email) return user.email.split('@')[0];
        return 'Minha conta';
    }

    function enforceLogin(event) {
        event.preventDefault();
        const params = new URLSearchParams();
        params.set('next', window.location.pathname + window.location.search);
        window.location.href = `${loginHref}?${params.toString()}`;
    }

    function handleLogout(event) {
        event.preventDefault();
        if (confirm('Deseja sair da sua conta?')) {
            API.Auth.logout();
        }
    }

    function renderAuthState() {
        const isLogged = API.Auth?.isAuthenticated?.() || false;
        const user = API.Auth?.getUser?.() || null;

        accountButtons.forEach(btn => {
            btn.onclick = null;

            if (isLogged && user) {
                btn.classList.add('account-btn--logged');
                const isPagesFolder = window.location.pathname.includes('/pages/');
                const accountHref = isPagesFolder ? 'minha-conta.html' : 'pages/minha-conta.html';
                btn.setAttribute('href', accountHref);
                btn.innerHTML = `<i class="fas fa-user-check"></i><span>${getUserDisplayName(user)}</span>`;
            } else {
                btn.classList.remove('account-btn--logged');
                btn.setAttribute('href', btn.dataset.loginHref || loginHref);
                btn.innerHTML = `<i class="fas fa-user"></i><span>Entrar</span>`;
            }
        });

        protectedButtons.forEach(btn => {
            btn.removeEventListener('click', enforceLogin);
            if (!isLogged) {
                btn.addEventListener('click', enforceLogin);
            }
        });
    }

    renderAuthState();
    window.addEventListener('authChange', renderAuthState);
    window.addEventListener('storage', renderAuthState);
}

/**
 * Carrega categorias da API
 */
async function loadCategories() {
    const grid = document.getElementById('categoriesGrid');
    if (!grid) return;
    
    // Ícones para cada categoria
    const categoryIcons = {
        'Bolos': 'fa-birthday-cake',
        'Doces': 'fa-cookie',
        'Salgados': 'fa-bread-slice',
        'Sanduíches': 'fa-burger',
        'Sobremesas': 'fa-ice-cream',
        'Bebidas': 'fa-mug-hot',
        'Finger Foods': 'fa-utensils',
        'Corporativos': 'fa-briefcase',
    };
    
    try {
        const categorias = await API.Categorias.listar();
        
        if (categorias.length === 0) {
            // Mostra categorias padrão se não houver da API
            grid.innerHTML = getDefaultCategories(categoryIcons);
            return;
        }
        
        grid.innerHTML = categorias.map(cat => `
            <div class="category-card" onclick="window.location.href='pages/doceria.html?categoria=${cat.id}'">
                <div class="image-wrapper">
                    <i class="fas ${categoryIcons[cat.nome] || 'fa-star'}"></i>
                </div>
                <h3>${cat.nome}</h3>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Erro ao carregar categorias:', error);
        grid.innerHTML = getDefaultCategories(categoryIcons);
    }
}

function getDefaultCategories(icons) {
    const defaultCats = ['Bolos', 'Doces', 'Salgados', 'Sobremesas', 'Finger Foods', 'Bebidas'];
    return defaultCats.map(cat => `
        <div class="category-card">
            <div class="image-wrapper">
                <i class="fas ${icons[cat] || 'fa-star'}"></i>
            </div>
            <h3>${cat}</h3>
        </div>
    `).join('');
}

/**
 * Carrega produtos da API
 */
async function loadProducts() {
    const grid = document.getElementById('productsGrid');
    if (!grid) return;
    
    try {
        const produtos = await API.Produtos.listar();
        
        if (produtos.length === 0) {
            grid.innerHTML = getDefaultProducts();
            return;
        }
        
        grid.innerHTML = produtos.slice(0, 4).map(prod => {
            const icon = getProductIcon(prod);
            return `
            <div class="product-card">
                <div class="image-wrapper">
                    <i class="fas ${icon}"></i>
                    <span class="badge">Destaque</span>
                </div>
                <div class="content">
                    <h3>${prod.nome}</h3>
                    <p class="description">${prod.descricao || 'Delicioso produto artesanal'}</p>
                    <p class="price">R$ ${prod.preco.toFixed(2).replace('.', ',')}</p>
                    <div class="actions">
                        <button class="btn-add" onclick="addToCart(${JSON.stringify(prod).replace(/"/g, '&quot;')})">
                            <i class="fas fa-plus"></i> Adicionar
                        </button>
                    </div>
                </div>
            </div>
        `;
        }).join('');
        
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        grid.innerHTML = getDefaultProducts();
    }
}

function getDefaultProducts() {
    const products = [
        { nome: 'Bolo de Chocolate', descricao: 'Bolo artesanal de chocolate belga', preco: 89.90 },
        { nome: 'Brigadeiros (50un)', descricao: 'Brigadeiros tradicionais', preco: 75.00 },
        { nome: 'Torta de Morango', descricao: 'Torta com morangos frescos', preco: 95.00 },
        { nome: 'Cupcakes (12un)', descricao: 'Cupcakes decorados', preco: 60.00 },
    ];
    
    return products.map((prod, i) => {
        const icon = getProductIcon(prod);
        return `
        <div class="product-card">
            <div class="image-wrapper">
                <i class="fas ${icon}"></i>
                <span class="badge">Destaque</span>
            </div>
            <div class="content">
                <h3>${prod.nome}</h3>
                <p class="description">${prod.descricao}</p>
                <p class="price">R$ ${prod.preco.toFixed(2).replace('.', ',')}</p>
                <div class="actions">
                    <button class="btn-add" onclick="addToCartDefault('${prod.nome}', ${prod.preco})">
                        <i class="fas fa-plus"></i> Adicionar
                    </button>
                </div>
            </div>
        </div>
    `;
    }).join('');
}

/**
 * Adiciona produto ao carrinho
 */
function addToCart(product) {
    Cart.addItem({
        id: product.id,
        type: 'produto',
        nome: product.nome,
        descricao: product.descricao,
        preco: product.preco,
    });
}

function addToCartDefault(nome, preco) {
    Cart.addItem({
        id: Date.now(), // ID temporário
        type: 'produto',
        nome: nome,
        descricao: '',
        preco: preco,
    });
}

/**
 * Determina o ícone apropriado para um produto
 * Produtos com "Bolo" no nome ou categoria "Bolos" recebem ícone de bolo
 * Produtos da categoria "Doces" recebem ícone de brigadeiro
 */
function getProductIcon(product, categoryName = null) {
    const nome = (product.nome || '').toLowerCase();
    const categoria = (categoryName || '').toLowerCase();
    
    // Verifica se é bolo pelo nome ou categoria
    if (nome.includes('bolo') || categoria.includes('bolo')) {
        return 'fa-birthday-cake';
    }
    
    // Verifica se é da categoria "Doces" - recebe ícone de brigadeiro
    if (categoria.includes('doce') && !categoria.includes('sobremesa')) {
        return 'fa-cookie';
    }
    
    // Outros produtos recebem ícones padrão baseados no nome
    if (nome.includes('brigadeiro') || nome.includes('doce')) {
        return 'fa-cookie';
    }
    if (nome.includes('torta') || nome.includes('sobremesa')) {
        return 'fa-cake-candles';
    }
    if (nome.includes('cupcake') || nome.includes('muffin')) {
        return 'fa-cake-candles';
    }
    if (nome.includes('salgado') || nome.includes('salgadinho')) {
        return 'fa-bread-slice';
    }
    if (nome.includes('bebida') || nome.includes('suco') || nome.includes('refrigerante')) {
        return 'fa-mug-hot';
    }
    if (nome.includes('sorvete') || nome.includes('gelado')) {
        return 'fa-ice-cream';
    }
    
    // Padrão
    return 'fa-birthday-cake';
}

/**
 * Formata valores monetários
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Exporta funções globais
window.addToCart = addToCart;
window.addToCartDefault = addToCartDefault;
window.formatCurrency = formatCurrency;
window.getProductIcon = getProductIcon;

