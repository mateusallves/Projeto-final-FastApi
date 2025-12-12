/**
 * API Service - Comunicação com o Backend
 */

const API_BASE_URL = 'http://127.0.0.1:8000';

const AUTH_TOKEN_KEY = 'authToken';
const AUTH_USER_KEY = 'authUser';

// Carregar token do localStorage ao inicializar
let authToken = localStorage.getItem(AUTH_TOKEN_KEY);
let authUser = getStoredAuthUser();

// Sincronizar token do localStorage periodicamente (a cada requisição)
if (authToken) {
    console.log('✅ Token encontrado no localStorage ao carregar a página');
} else {
    console.log('ℹ️ Nenhum token encontrado no localStorage');
}

function getStoredAuthUser() {
    try {
        const stored = localStorage.getItem(AUTH_USER_KEY);
        return stored ? JSON.parse(stored) : null;
    } catch (error) {
        console.warn('Não foi possível ler o usuário salvo.', error);
        return null;
    }
}

function decodeJwt(token) {
    if (!token) return null;
    try {
        const [, payload] = token.split('.');
        const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
        const padded = normalized.padEnd(normalized.length + (4 - normalized.length % 4) % 4, '=');
        return JSON.parse(atob(padded));
    } catch (error) {
        console.warn('Token JWT inválido.', error);
        return null;
    }
}

function buildUserFromToken(payload, fallbackEmail) {
    const email = payload?.email || fallbackEmail || null;
    if (!email) return null;
    return {
        id: payload?.id ?? null,
        email,
        nome: (payload?.nome || email.split('@')[0] || 'Cliente')
    };
}

function emitAuthChange() {
    if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('authChange', {
            detail: {
                isAuthenticated: !!authToken,
                user: authUser
            }
        }));
    }
}

function persistAuthState(token, fallbackEmail) {
    if (!token) {
        console.error('Tentativa de salvar token vazio');
        return;
    }
    
    // Salvar token no localStorage
    authToken = token;
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    console.log('✅ Token de autenticação salvo no localStorage');

    const payload = decodeJwt(token);
    const user = buildUserFromToken(payload, fallbackEmail);

    if (user) {
        authUser = user;
        localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
        console.log('✅ Usuário autenticado e salvo:', user);
    } else {
        authUser = null;
        localStorage.removeItem(AUTH_USER_KEY);
        console.warn('⚠️ Não foi possível construir objeto de usuário do token');
    }

    emitAuthChange();
}

function clearAuthState() {
    authToken = null;
    authUser = null;
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    emitAuthChange();
}

/**
 * Configuração padrão para requisições
 */
function getHeaders(includeAuth = false) {
    const headers = {
        'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
        // Sempre ler do localStorage para garantir que temos o token mais recente
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            // Atualizar variável global também
            authToken = token;
        } else {
            console.error('❌ Tentativa de requisição autenticada sem token disponível no localStorage');
            console.error('Token no localStorage:', localStorage.getItem(AUTH_TOKEN_KEY));
            console.error('Token na variável:', authToken);
        }
    }
    
    return headers;
}

/**
 * Handler de erros da API
 */
async function handleResponse(response) {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
        throw new Error(error.detail || `Erro ${response.status}`);
    }
    return response.json();
}

/**
 * Wrapper para requisições fetch com tratamento de erro melhorado
 */
async function safeFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        return response;
    } catch (error) {
        // Se for erro de CORS ou conexão
        if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
            console.error(`Erro ao conectar com a API em ${url}`);
            console.error('Verifique se o servidor backend está rodando em http://127.0.0.1:8000');
            console.error('Dica: Se estiver abrindo o arquivo via file://, use um servidor HTTP local');
            throw new Error('Não foi possível conectar ao servidor. Verifique se o backend está rodando.');
        }
        throw error;
    }
}

/**
 * API de Autenticação
 */
const AuthAPI = {
    async login(email, senha) {
        console.log('🔐 Iniciando processo de login para:', email);
        const response = await safeFetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ email, senha }),
        });
        const data = await handleResponse(response);
        
        // Garantir que o token seja salvo no localStorage
        if (data.access_token) {
            console.log('📦 Token recebido do servidor, salvando no localStorage...');
            persistAuthState(data.access_token, email);
            
            // Verificar se foi salvo corretamente
            const tokenSalvo = localStorage.getItem(AUTH_TOKEN_KEY);
            if (tokenSalvo === data.access_token) {
                console.log('✅ Token salvo com sucesso no localStorage');
            } else {
                console.error('❌ Erro: Token não foi salvo corretamente no localStorage');
            }
        } else {
            console.error('❌ Erro: Token não recebido na resposta do servidor');
            throw new Error('Token de autenticação não recebido');
        }
        
        return {
            ...data,
            user: authUser
        };
    },
    
    async register(nome, email, senha) {
        const response = await safeFetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ nome, email, senha }),
        });
        return handleResponse(response);
    },
    
    getUser() {
        return authUser;
    },
    
    logout() {
        clearAuthState();
    },
    
    isAuthenticated() {
        // Sempre verificar no localStorage para garantir que está atualizado
        const token = localStorage.getItem(AUTH_TOKEN_KEY);
        if (token) {
            authToken = token; // Sincronizar variável global
        }
        return !!token;
    },

    async changePassword(senhaAtual, novaSenha) {
        const response = await safeFetch(`${API_BASE_URL}/auth/change-password`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify({
                senha_atual: senhaAtual,
                nova_senha: novaSenha
            }),
        });
        return handleResponse(response);
    }
};

/**
 * API de Categorias
 */
const CategoriasAPI = {
    async listar() {
        const response = await safeFetch(`${API_BASE_URL}/categorias/`, {
            headers: getHeaders(),
        });
        return handleResponse(response);
    },
    
    async criar(nome) {
        const response = await safeFetch(`${API_BASE_URL}/categorias/`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify({ nome }),
        });
        return handleResponse(response);
    }
};

/**
 * API de Produtos
 */
const ProdutosAPI = {
    async listar() {
        const response = await safeFetch(`${API_BASE_URL}/produtos/`, {
            headers: getHeaders(),
        });
        return handleResponse(response);
    },
    
    async buscar(id) {
        const response = await safeFetch(`${API_BASE_URL}/produtos/${id}`, {
            headers: getHeaders(),
        });
        return handleResponse(response);
    },
    
    async criar(produto) {
        const response = await safeFetch(`${API_BASE_URL}/produtos/`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify(produto),
        });
        return handleResponse(response);
    }
};

/**
 * API de Kits
 */
const KitsAPI = {
    async listar() {
        const response = await safeFetch(`${API_BASE_URL}/kits/`, {
            headers: getHeaders(),
        });
        return handleResponse(response);
    },
    
    async buscar(id) {
        const response = await safeFetch(`${API_BASE_URL}/kits/${id}`, {
            headers: getHeaders(),
        });
        return handleResponse(response);
    }
};

/**
 * API de Clientes
 */
const ClientesAPI = {
    async criar(cliente) {
        const headers = getHeaders(true);
        console.log('📤 Criando cliente com headers:', {
            hasAuth: !!headers['Authorization'],
            authHeader: headers['Authorization'] ? 'Bearer ***' : 'não presente'
        });
        const response = await safeFetch(`${API_BASE_URL}/clientes/`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(cliente),
        });
        return handleResponse(response);
    },
    
    async buscarPorId(id) {
        const headers = getHeaders(true);
        console.log('📤 Buscando cliente por ID com headers:', {
            hasAuth: !!headers['Authorization'],
            authHeader: headers['Authorization'] ? 'Bearer ***' : 'não presente'
        });
        const response = await safeFetch(`${API_BASE_URL}/clientes/${id}`, {
            headers: headers,
        });
        return handleResponse(response);
    },

    async buscar(termo) {
        const headers = getHeaders(true);
        console.log('📤 Buscando cliente com termo:', termo, 'headers:', {
            hasAuth: !!headers['Authorization'],
            authHeader: headers['Authorization'] ? 'Bearer ***' : 'não presente'
        });
        const response = await safeFetch(`${API_BASE_URL}/clientes/buscar?q=${encodeURIComponent(termo)}`, {
            headers: headers,
        });
        return handleResponse(response);
    },

    async buscarPorEmail(email) {
        const headers = getHeaders(true);
        console.log('📤 Buscando cliente por email exato:', email);
        const response = await safeFetch(`${API_BASE_URL}/clientes/por-email?email=${encodeURIComponent(email)}`, {
            headers: headers,
        });
        return handleResponse(response);
    },

    async atualizar(id, dados) {
        const headers = getHeaders(true);
        console.log('📤 Atualizando cliente com headers:', {
            hasAuth: !!headers['Authorization'],
            authHeader: headers['Authorization'] ? 'Bearer ***' : 'não presente'
        });
        const response = await safeFetch(`${API_BASE_URL}/clientes/${id}`, {
            method: 'PUT',
            headers: headers,
            body: JSON.stringify(dados),
        });
        return handleResponse(response);
    }
};

/**
 * API de Pedidos
 */
const PedidosAPI = {
    async criar(pedido) {
        const response = await safeFetch(`${API_BASE_URL}/pedidos/`, {
            method: 'POST',
            headers: getHeaders(true),
            body: JSON.stringify(pedido),
        });
        return handleResponse(response);
    },
    
    async listar(skip = 0, limit = 100, status = null, cliente_id = null) {
        let url = `${API_BASE_URL}/pedidos/?skip=${skip}&limit=${limit}`;
        if (status) url += `&status=${encodeURIComponent(status)}`;
        if (cliente_id) url += `&cliente_id=${cliente_id}`;
        
        const response = await safeFetch(url, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    },

    async listarPorCliente(clienteId) {
        const response = await safeFetch(`${API_BASE_URL}/pedidos/cliente/${clienteId}`, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    },
    
    async buscar(id) {
        const response = await safeFetch(`${API_BASE_URL}/pedidos/${id}`, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    },
    
    async buscarPorNumero(numero) {
        const response = await safeFetch(`${API_BASE_URL}/pedidos/numero/${numero}`, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    }
};

/**
 * API de Contato
 */
const ContatoAPI = {
    async enviar(contato) {
        const response = await safeFetch(`${API_BASE_URL}/contato/`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(contato),
        });
        return handleResponse(response);
    }
};

/**
 * API de Pagamentos
 */
const PagamentosAPI = {
    async listarPorCliente(clienteId, skip = 0, limit = 100) {
        const response = await safeFetch(`${API_BASE_URL}/pagamentos/cliente/${clienteId}?skip=${skip}&limit=${limit}`, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    },

    async buscarPorId(id) {
        const response = await safeFetch(`${API_BASE_URL}/pagamentos/${id}`, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    },

    async historico(pagamentoId) {
        const response = await safeFetch(`${API_BASE_URL}/pagamentos/${pagamentoId}/historico`, {
            headers: getHeaders(true),
        });
        return handleResponse(response);
    }
};

// Exporta para uso global
window.API = {
    Auth: AuthAPI,
    Categorias: CategoriasAPI,
    Produtos: ProdutosAPI,
    Kits: KitsAPI,
    Clientes: ClientesAPI,
    Pedidos: PedidosAPI,
    Contato: ContatoAPI,
    Pagamentos: PagamentosAPI,
};


