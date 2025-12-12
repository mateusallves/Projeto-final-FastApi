/**
 * Cart Service - Gerenciamento do Carrinho
 */

const Cart = {
    STORAGE_KEY: 'doceria_cart',
    
    /**
     * Obtém os itens do carrinho
     */
    getItems() {
        const cart = localStorage.getItem(this.STORAGE_KEY);
        return cart ? JSON.parse(cart) : [];
    },
    
    /**
     * Salva os itens no carrinho
     */
    saveItems(items) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
        this.updateCartCount();
        this.dispatchEvent('cartUpdated', items);
    },
    
    /**
     * Adiciona um item ao carrinho
     */
    addItem(product, quantity = 1) {
        const items = this.getItems();
        const existingIndex = items.findIndex(item => 
            item.id === product.id && item.type === product.type
        );
        
        if (existingIndex > -1) {
            items[existingIndex].quantity += quantity;
        } else {
            items.push({
                id: product.id,
                type: product.type || 'produto', // produto ou kit
                name: product.nome,
                description: product.descricao,
                price: product.preco,
                quantity: quantity,
                image: product.imagem || null,
            });
        }
        
        this.saveItems(items);
        this.showNotification(`${product.nome} adicionado ao carrinho!`);
    },
    
    /**
     * Remove um item do carrinho
     */
    removeItem(id, type = 'produto') {
        const items = this.getItems().filter(item => 
            !(item.id === id && item.type === type)
        );
        this.saveItems(items);
    },
    
    /**
     * Atualiza a quantidade de um item
     */
    updateQuantity(id, type, quantity) {
        const items = this.getItems();
        const item = items.find(item => item.id === id && item.type === type);
        
        if (item) {
            if (quantity <= 0) {
                this.removeItem(id, type);
            } else {
                item.quantity = quantity;
                this.saveItems(items);
            }
        }
    },
    
    /**
     * Limpa o carrinho
     */
    clear() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.updateCartCount();
        this.dispatchEvent('cartUpdated', []);
    },
    
    /**
     * Calcula o total do carrinho
     */
    getTotal() {
        const items = this.getItems();
        return items.reduce((total, item) => total + (item.price * item.quantity), 0);
    },
    
    /**
     * Conta o número de itens no carrinho
     */
    getItemCount() {
        const items = this.getItems();
        return items.reduce((count, item) => count + item.quantity, 0);
    },
    
    /**
     * Atualiza o contador do carrinho na interface
     */
    updateCartCount() {
        const countElement = document.getElementById('cartCount');
        if (countElement) {
            countElement.textContent = this.getItemCount();
        }
    },
    
    /**
     * Mostra notificação de item adicionado
     */
    showNotification(message) {
        // Cria elemento de notificação
        const notification = document.createElement('div');
        notification.className = 'cart-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${message}</span>
        `;
        
        // Estilos inline para a notificação
        notification.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: #4caf50;
            color: white;
            padding: 15px 25px;
            border-radius: 50px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: slideUp 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Remove após 3 segundos
        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },
    
    /**
     * Dispara eventos personalizados
     */
    dispatchEvent(name, data) {
        window.dispatchEvent(new CustomEvent(name, { detail: data }));
    },
    
    /**
     * Formata um item para o pedido
     */
    formatForOrder() {
        return this.getItems().map(item => ({
            produto_id: item.type === 'produto' ? item.id : null,
            kit_id: item.type === 'kit' ? item.id : null,
            quantidade: item.quantity,
            observacoes: item.observacoes || null,
        }));
    }
};

// Adiciona estilos de animação
const style = document.createElement('style');
style.textContent = `
    @keyframes slideUp {
        from { opacity: 0; transform: translateX(-50%) translateY(20px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
    @keyframes slideDown {
        from { opacity: 1; transform: translateX(-50%) translateY(0); }
        to { opacity: 0; transform: translateX(-50%) translateY(20px); }
    }
`;
document.head.appendChild(style);

// Inicializa o contador do carrinho quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    Cart.updateCartCount();
});

// Exporta para uso global
window.Cart = Cart;

