/**
 * Account Management - Gerenciamento da área do usuário
 */

const Account = {
    currentCliente: null,

    /**
     * Busca ou cria um cliente associado ao usuário logado
     */
    async getOrCreateCliente(user) {
        if (this.currentCliente) {
            return this.currentCliente;
        }

        try {
            // Verificar se está autenticado antes de buscar cliente
            if (!API.Auth.isAuthenticated()) {
                console.error('Usuário não autenticado ao tentar buscar/criar cliente');
                throw new Error('Usuário não autenticado. Faça login primeiro.');
            }

            console.log('Buscando cliente para email:', user.email);

            // Tentar buscar cliente por email exato primeiro
            try {
                console.log('Buscando cliente por email exato:', user.email);
                this.currentCliente = await API.Clientes.buscarPorEmail(user.email);
                console.log('✅ Cliente encontrado por email exato:', this.currentCliente?.id);
                return this.currentCliente;
            } catch (error) {
                console.log('Cliente não encontrado por email exato, tentando busca geral...');
                // Se erro 404, cliente não existe, continuar para criar
                if (error.message && error.message.includes('404')) {
                    console.log('Cliente não encontrado (404), tentando criar novo...');
                } else if (error.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
                    console.error('Erro 401: Token inválido ou expirado');
                    throw new Error('Sessão expirada. Faça login novamente.');
                } else {
                    console.error('Erro ao buscar cliente por email:', error);
                }
            }
            
            // Se não encontrou por email exato, tentar busca geral
            let clientes = [];
            try {
                clientes = await API.Clientes.buscar(user.email);
                console.log('Clientes encontrados na busca geral:', clientes?.length || 0);
                if (clientes && clientes.length > 0) {
                    // Filtrar para encontrar o cliente com email exato
                    const clienteExato = clientes.find(c => c.email && c.email.toLowerCase() === user.email.toLowerCase());
                    if (clienteExato) {
                        this.currentCliente = await API.Clientes.buscarPorId(clienteExato.id);
                        console.log('✅ Cliente encontrado na busca geral:', this.currentCliente?.id);
                        return this.currentCliente;
                    }
                }
            } catch (error) {
                console.error('Erro na busca geral:', error);
            }

            // Cliente não encontrado, criar novo (caso não tenha sido criado durante o registro)
            console.log('Tentando criar novo cliente...');
            const novoCliente = {
                nome: user.nome || user.email.split('@')[0],
                email: user.email,
                // telefone é opcional, não enviar se vazio
                ...(user.telefone ? { telefone: user.telefone } : {})
            };

            try {
                console.log('Dados do cliente a criar:', novoCliente);
                this.currentCliente = await API.Clientes.criar(novoCliente);
                console.log('Cliente criado com sucesso:', this.currentCliente?.id);
                return this.currentCliente;
            } catch (error) {
                console.error('Erro ao criar cliente:', error);
                // Se erro 401, usuário não está autenticado
                if (error.message && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
                    console.error('Erro 401 ao criar cliente: Token inválido ou não enviado');
                    throw new Error('Sessão expirada. Faça login novamente.');
                }
                // Se erro 400 (email já cadastrado), buscar o cliente existente por email exato
                if (error.message && (error.message.includes('já cadastrado') || error.message.includes('Email já'))) {
                    console.log('⚠️ Cliente já existe (email já cadastrado), buscando cliente existente por email exato...');
                    try {
                        // Buscar por email exato usando o novo endpoint
                        this.currentCliente = await API.Clientes.buscarPorEmail(user.email);
                        console.log('✅ Cliente existente encontrado por email exato:', this.currentCliente?.id);
                        return this.currentCliente;
                    } catch (buscaError) {
                        console.error('Erro ao buscar cliente por email exato:', buscaError);
                        // Se não conseguir buscar por email exato, tentar busca geral
                        try {
                            clientes = await API.Clientes.buscar(user.email);
                            if (clientes && clientes.length > 0) {
                                // Filtrar para encontrar o cliente com email exato
                                const clienteExato = clientes.find(c => c.email && c.email.toLowerCase() === user.email.toLowerCase());
                                if (clienteExato) {
                                    this.currentCliente = await API.Clientes.buscarPorId(clienteExato.id);
                                    console.log('✅ Cliente encontrado na busca geral:', this.currentCliente?.id);
                                    return this.currentCliente;
                                }
                            }
                        } catch (buscaGeralError) {
                            console.error('Erro na busca geral:', buscaGeralError);
                        }
                        // Se não conseguir buscar, retornar erro mais amigável
                        throw new Error('Cliente já existe, mas não foi possível recuperá-lo. Tente fazer login novamente.');
                    }
                }
                throw error;
            }
        } catch (error) {
            console.error('Erro ao buscar/criar cliente:', error);
            throw error;
        }
    },

    /**
     * Carrega o dashboard do usuário
     */
    async loadDashboard() {
        try {
            const user = API.Auth.getUser();
            if (!user) {
                window.location.href = 'login.html';
                return;
            }

            // Atualizar nome do usuário
            document.getElementById('profileName').textContent = user.nome || user.email.split('@')[0];
            document.getElementById('profileEmail').textContent = user.email;
            if (document.getElementById('userName')) {
                document.getElementById('userName').textContent = user.nome || 'Minha Conta';
            }

            // Buscar cliente
            const cliente = await this.getOrCreateCliente(user);

            // Carregar estatísticas
            await this.loadStats(cliente.id);

            // Carregar pedidos recentes
            await this.loadRecentOrders(cliente.id);
        } catch (error) {
            console.error('Erro ao carregar dashboard:', error);
        }
    },

    /**
     * Carrega estatísticas do usuário
     */
    async loadStats(clienteId) {
        try {
            const pedidos = await API.Pedidos.listarPorCliente(clienteId);
            
            const totalPedidos = pedidos.length;
            const pedidosEntregues = pedidos.filter(p => p.status === 'entregue').length;
            const pedidosPendentes = pedidos.filter(p => 
                ['pendente', 'confirmado', 'em_preparo', 'pronto', 'saiu_entrega'].includes(p.status)
            ).length;
            const totalGasto = pedidos
                .filter(p => p.status === 'entregue')
                .reduce((sum, p) => sum + p.total, 0);

            document.getElementById('totalPedidos').textContent = totalPedidos;
            document.getElementById('pedidosEntregues').textContent = pedidosEntregues;
            document.getElementById('pedidosPendentes').textContent = pedidosPendentes;
            document.getElementById('totalGasto').textContent = `R$ ${totalGasto.toFixed(2).replace('.', ',')}`;
            document.getElementById('ordersBadge').textContent = pedidosPendentes;
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
        }
    },

    /**
     * Carrega pedidos recentes
     */
    async loadRecentOrders(clienteId) {
        try {
            const pedidos = await API.Pedidos.listarPorCliente(clienteId);
            const recentOrders = pedidos.slice(0, 5); // Últimos 5 pedidos

            const ordersList = document.getElementById('recentOrdersList');
            
            if (recentOrders.length === 0) {
                ordersList.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-shopping-bag"></i>
                        <p>Você ainda não realizou nenhum pedido.</p>
                        <a href="doceria.html" class="btn-secondary">Fazer Primeiro Pedido</a>
                    </div>
                `;
                return;
            }

            ordersList.innerHTML = recentOrders.map(pedido => {
                const statusClass = this.getStatusClass(pedido.status);
                const statusLabel = this.getStatusLabel(pedido.status);
                const dataPedido = new Date(pedido.data_pedido).toLocaleDateString('pt-BR');

                return `
                    <div class="order-item-mini">
                        <div class="order-mini-info">
                            <h4>Pedido ${pedido.numero_pedido}</h4>
                            <p>${dataPedido} • R$ ${pedido.total.toFixed(2).replace('.', ',')}</p>
                        </div>
                        <span class="status-badge ${statusClass}">${statusLabel}</span>
                    </div>
                `;
            }).join('');
        } catch (error) {
            console.error('Erro ao carregar pedidos recentes:', error);
            document.getElementById('recentOrdersList').innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Erro ao carregar pedidos.</p>
                </div>
            `;
        }
    },

    /**
     * Retorna classe CSS para status
     */
    getStatusClass(status) {
        const statusMap = {
            'pendente': 'status-pending',
            'confirmado': 'status-confirmed',
            'em_preparo': 'status-preparing',
            'pronto': 'status-ready',
            'saiu_entrega': 'status-delivering',
            'entregue': 'status-delivered',
            'cancelado': 'status-cancelled'
        };
        return statusMap[status] || 'status-pending';
    },

    /**
     * Retorna label para status
     */
    getStatusLabel(status) {
        const labelMap = {
            'pendente': 'Pendente',
            'confirmado': 'Confirmado',
            'em_preparo': 'Em Preparo',
            'pronto': 'Pronto',
            'saiu_entrega': 'Saiu para Entrega',
            'entregue': 'Entregue',
            'cancelado': 'Cancelado'
        };
        return labelMap[status] || status;
    }
};

// Exporta para uso global
window.Account = Account;

