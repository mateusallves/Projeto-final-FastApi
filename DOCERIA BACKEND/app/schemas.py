from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
from datetime import datetime
import re


# ================================
# SCHEMAS DE AUTENTICAÇÃO
# ================================

class LoginSchema(BaseModel):
    """Schema para login"""
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=6, description="Senha do usuário (mínimo 6 caracteres)")


class RegisterSchema(BaseModel):
    """Schema para registro de usuário"""
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=6, description="Senha do usuário (mínimo 6 caracteres)")
    
    @field_validator('senha')
    @classmethod
    def validar_senha(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        if not any(c.isdigit() for c in v):
            raise ValueError('Senha deve conter pelo menos um número')
        return v


class TokenResponse(BaseModel):
    """Schema de resposta do token"""
    access_token: str
    token_type: str = "bearer"


class ChangePasswordSchema(BaseModel):
    """Schema para alteração de senha"""
    senha_atual: str = Field(..., min_length=6, description="Senha atual do usuário")
    nova_senha: str = Field(..., min_length=6, description="Nova senha (mínimo 6 caracteres)")
    
    @field_validator('nova_senha')
    @classmethod
    def validar_nova_senha(cls, v):
        if len(v) < 6:
            raise ValueError('A nova senha deve ter pelo menos 6 caracteres')
        if not any(c.isdigit() for c in v):
            raise ValueError('A nova senha deve conter pelo menos um número')
        return v


class CategoriaCreate(BaseModel):
    nome: str


class CategoriaOut(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    categoria_id: int


class ProdutoOut(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    preco: float
    categoria_id: int

    class Config:
        from_attributes = True


class ContatoCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    numero_pessoas: Optional[int] = None
    tipo_evento: Optional[str] = None
    data: Optional[str] = None
    local: Optional[str] = None
    observacao: Optional[str] = None


class ContatoOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: Optional[str]

    class Config:
        from_attributes = True


# ================================
# SCHEMAS DE CLIENTE
# ================================

class ClienteCreate(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    data_nascimento: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        if v is None:
            return v
        # Remove caracteres não numéricos
        cpf_limpo = re.sub(r'\D', '', v)
        if len(cpf_limpo) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf_limpo

    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v):
        if v is None or v == '':
            return None
        # Remove caracteres não numéricos
        telefone_limpo = re.sub(r'\D', '', v)
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return telefone_limpo

    @field_validator('cep')
    @classmethod
    def validar_cep(cls, v):
        if v is None:
            return v
        cep_limpo = re.sub(r'\D', '', v)
        if len(cep_limpo) != 8:
            raise ValueError('CEP deve ter 8 dígitos')
        return cep_limpo


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cpf: Optional[str] = None
    endereco: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    data_nascimento: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None

    @field_validator('cpf')
    @classmethod
    def validar_cpf(cls, v):
        if v is None:
            return v
        cpf_limpo = re.sub(r'\D', '', v)
        if len(cpf_limpo) != 11:
            raise ValueError('CPF deve ter 11 dígitos')
        return cpf_limpo

    @field_validator('telefone')
    @classmethod
    def validar_telefone(cls, v):
        if v is None:
            return v
        telefone_limpo = re.sub(r'\D', '', v)
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            raise ValueError('Telefone deve ter 10 ou 11 dígitos')
        return telefone_limpo

    @field_validator('cep')
    @classmethod
    def validar_cep(cls, v):
        if v is None:
            return v
        cep_limpo = re.sub(r'\D', '', v)
        if len(cep_limpo) != 8:
            raise ValueError('CEP deve ter 8 dígitos')
        return cep_limpo


class ClienteOut(BaseModel):
    id: int
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cpf: Optional[str]
    endereco: Optional[str]
    numero: Optional[str]
    complemento: Optional[str]
    bairro: Optional[str]
    cidade: Optional[str]
    estado: Optional[str]
    cep: Optional[str]
    data_nascimento: Optional[str]
    observacoes: Optional[str]
    ativo: bool
    data_cadastro: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class ClienteResumo(BaseModel):
    """Schema resumido para listagens"""
    id: int
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cidade: Optional[str]
    ativo: bool

    class Config:
        from_attributes = True


# ================================
# SCHEMAS DE PEDIDO
# ================================

class ItemPedidoCreate(BaseModel):
    """Schema para criar item do pedido"""
    produto_id: Optional[int] = None
    kit_id: Optional[int] = None
    quantidade: int = 1
    observacoes: Optional[str] = None

    @field_validator('quantidade')
    @classmethod
    def validar_quantidade(cls, v):
        if v < 1:
            raise ValueError('Quantidade deve ser pelo menos 1')
        return v


class ItemPedidoOut(BaseModel):
    """Schema de saída do item do pedido"""
    id: int
    produto_id: Optional[int]
    kit_id: Optional[int]
    nome_item: str
    descricao_item: Optional[str]
    quantidade: int
    preco_unitario: float
    subtotal: float
    observacoes: Optional[str]

    class Config:
        from_attributes = True


class PedidoCreate(BaseModel):
    """Schema para criar pedido"""
    cliente_id: int
    tipo_entrega: str = "entrega"  # entrega ou retirada
    
    # Data e hora desejada
    data_entrega: Optional[str] = None
    hora_entrega: Optional[str] = None
    
    # Endereço de entrega (opcional, pode usar do cliente)
    usar_endereco_cliente: bool = True
    endereco_entrega: Optional[str] = None
    numero_entrega: Optional[str] = None
    complemento_entrega: Optional[str] = None
    bairro_entrega: Optional[str] = None
    cidade_entrega: Optional[str] = None
    estado_entrega: Optional[str] = None
    cep_entrega: Optional[str] = None
    
    # Pagamento
    forma_pagamento: Optional[str] = None
    troco_para: Optional[float] = None
    
    # Itens do pedido
    itens: list[ItemPedidoCreate]
    
    # Valores opcionais
    desconto: float = 0.0
    taxa_entrega: float = 0.0
    
    # Observações
    observacoes: Optional[str] = None

    @field_validator('tipo_entrega')
    @classmethod
    def validar_tipo_entrega(cls, v):
        tipos_validos = ['entrega', 'retirada']
        if v.lower() not in tipos_validos:
            raise ValueError(f'Tipo de entrega deve ser: {", ".join(tipos_validos)}')
        return v.lower()

    @field_validator('forma_pagamento')
    @classmethod
    def validar_forma_pagamento(cls, v):
        if v is None:
            return v
        formas_validas = ['dinheiro', 'pix', 'cartao_credito', 'cartao_debito', 'transferencia']
        if v.lower() not in formas_validas:
            raise ValueError(f'Forma de pagamento deve ser: {", ".join(formas_validas)}')
        return v.lower()


class PedidoUpdate(BaseModel):
    """Schema para atualizar pedido"""
    status: Optional[str] = None
    tipo_entrega: Optional[str] = None
    data_entrega: Optional[str] = None
    hora_entrega: Optional[str] = None
    endereco_entrega: Optional[str] = None
    numero_entrega: Optional[str] = None
    complemento_entrega: Optional[str] = None
    bairro_entrega: Optional[str] = None
    cidade_entrega: Optional[str] = None
    estado_entrega: Optional[str] = None
    cep_entrega: Optional[str] = None
    forma_pagamento: Optional[str] = None
    troco_para: Optional[float] = None
    desconto: Optional[float] = None
    taxa_entrega: Optional[float] = None
    observacoes: Optional[str] = None


class PedidoOut(BaseModel):
    """Schema de saída do pedido completo"""
    id: int
    numero_pedido: str
    cliente_id: int
    status: str
    tipo_entrega: str
    data_pedido: datetime
    data_entrega: Optional[str]
    hora_entrega: Optional[str]
    endereco_entrega: Optional[str]
    numero_entrega: Optional[str]
    complemento_entrega: Optional[str]
    bairro_entrega: Optional[str]
    cidade_entrega: Optional[str]
    estado_entrega: Optional[str]
    cep_entrega: Optional[str]
    subtotal: float
    desconto: float
    taxa_entrega: float
    total: float
    forma_pagamento: Optional[str]
    troco_para: Optional[float]
    observacoes: Optional[str]
    itens: list[ItemPedidoOut]
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class PedidoResumo(BaseModel):
    """Schema resumido para listagens"""
    id: int
    numero_pedido: str
    cliente_id: int
    status: str
    tipo_entrega: str
    data_pedido: datetime
    data_entrega: Optional[str]
    hora_entrega: Optional[str]
    total: float
    forma_pagamento: Optional[str]

    class Config:
        from_attributes = True


class AtualizarStatusPedido(BaseModel):
    """Schema para atualizar apenas o status"""
    status: str

    @field_validator('status')
    @classmethod
    def validar_status(cls, v):
        status_validos = ['pendente', 'confirmado', 'em_preparo', 'pronto', 'saiu_entrega', 'entregue', 'cancelado']
        if v.lower() not in status_validos:
            raise ValueError(f'Status deve ser: {", ".join(status_validos)}')
        return v.lower()


# ================================
# SCHEMAS DE PAGAMENTO
# ================================

class PagamentoCreate(BaseModel):
    """Schema para criar pagamento"""
    pedido_id: int
    valor: float
    forma_pagamento: str
    
    # Para dinheiro
    valor_pago: Optional[float] = None  # Valor que o cliente pagou
    
    # Para cartão
    bandeira_cartao: Optional[str] = None
    ultimos_digitos: Optional[str] = None
    parcelas: int = 1
    
    # Para PIX
    chave_pix: Optional[str] = None
    comprovante: Optional[str] = None
    
    # Transação externa
    codigo_transacao: Optional[str] = None
    codigo_autorizacao: Optional[str] = None
    nsu: Optional[str] = None
    
    observacoes: Optional[str] = None

    @field_validator('forma_pagamento')
    @classmethod
    def validar_forma_pagamento(cls, v):
        formas_validas = ['dinheiro', 'pix', 'cartao_credito', 'cartao_debito', 'transferencia', 'boleto']
        if v.lower() not in formas_validas:
            raise ValueError(f'Forma de pagamento deve ser: {", ".join(formas_validas)}')
        return v.lower()

    @field_validator('parcelas')
    @classmethod
    def validar_parcelas(cls, v):
        if v < 1 or v > 12:
            raise ValueError('Parcelas deve ser entre 1 e 12')
        return v

    @field_validator('ultimos_digitos')
    @classmethod
    def validar_ultimos_digitos(cls, v):
        if v is None:
            return v
        digitos = re.sub(r'\D', '', v)
        if len(digitos) != 4:
            raise ValueError('Últimos dígitos deve ter 4 números')
        return digitos


class PagamentoDinheiro(BaseModel):
    """Schema específico para pagamento em dinheiro"""
    pedido_id: int
    valor: float
    valor_pago: float  # Quanto o cliente deu
    observacoes: Optional[str] = None


class PagamentoPix(BaseModel):
    """Schema específico para pagamento PIX"""
    pedido_id: int
    valor: float
    chave_pix: Optional[str] = None
    comprovante: Optional[str] = None
    codigo_transacao: Optional[str] = None
    observacoes: Optional[str] = None


class PagamentoCartao(BaseModel):
    """Schema específico para pagamento com cartão"""
    pedido_id: int
    valor: float
    tipo: str  # credito ou debito
    bandeira_cartao: str
    ultimos_digitos: str
    parcelas: int = 1
    codigo_autorizacao: Optional[str] = None
    nsu: Optional[str] = None
    observacoes: Optional[str] = None

    @field_validator('tipo')
    @classmethod
    def validar_tipo(cls, v):
        if v.lower() not in ['credito', 'debito']:
            raise ValueError('Tipo deve ser: credito ou debito')
        return v.lower()

    @field_validator('parcelas')
    @classmethod
    def validar_parcelas(cls, v):
        if v < 1 or v > 12:
            raise ValueError('Parcelas deve ser entre 1 e 12')
        return v


class PagamentoUpdate(BaseModel):
    """Schema para atualizar pagamento"""
    status: Optional[str] = None
    valor_pago: Optional[float] = None
    comprovante: Optional[str] = None
    codigo_transacao: Optional[str] = None
    codigo_autorizacao: Optional[str] = None
    nsu: Optional[str] = None
    observacoes: Optional[str] = None
    motivo_recusa: Optional[str] = None


class ConfirmarPagamento(BaseModel):
    """Schema para confirmar um pagamento"""
    codigo_transacao: Optional[str] = None
    codigo_autorizacao: Optional[str] = None
    nsu: Optional[str] = None
    comprovante: Optional[str] = None
    observacoes: Optional[str] = None


class EstornarPagamento(BaseModel):
    """Schema para estornar um pagamento"""
    motivo: str
    valor_estorno: Optional[float] = None  # Se None, estorna valor total


class PagamentoOut(BaseModel):
    """Schema de saída do pagamento"""
    id: int
    pedido_id: int
    valor: float
    valor_pago: float
    troco: float
    forma_pagamento: str
    status: str
    bandeira_cartao: Optional[str]
    ultimos_digitos: Optional[str]
    parcelas: int
    chave_pix: Optional[str]
    codigo_pix: Optional[str]
    codigo_transacao: Optional[str]
    codigo_autorizacao: Optional[str]
    nsu: Optional[str]
    data_criacao: datetime
    data_pagamento: Optional[datetime]
    data_estorno: Optional[datetime]
    observacoes: Optional[str]
    motivo_recusa: Optional[str]
    motivo_estorno: Optional[str]
    numero_pedido: Optional[str] = None  # Número do pedido (via relationship)

    class Config:
        from_attributes = True


class PagamentoResumo(BaseModel):
    """Schema resumido para listagens"""
    id: int
    pedido_id: int
    valor: float
    forma_pagamento: str
    status: str
    parcelas: int
    data_criacao: datetime
    data_pagamento: Optional[datetime]
    numero_pedido: Optional[str] = None  # Número do pedido (via relationship)

    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_pedido(cls, pagamento):
        """Cria instância incluindo número do pedido"""
        data = {
            "id": pagamento.id,
            "pedido_id": pagamento.pedido_id,
            "valor": pagamento.valor,
            "forma_pagamento": pagamento.forma_pagamento,
            "status": pagamento.status,
            "parcelas": pagamento.parcelas,
            "data_criacao": pagamento.data_criacao,
            "data_pagamento": pagamento.data_pagamento,
            "numero_pedido": pagamento.pedido.numero_pedido if pagamento.pedido else None
        }
        return cls(**data)


class HistoricoPagamentoOut(BaseModel):
    """Schema de saída do histórico de pagamento"""
    id: int
    pagamento_id: int
    status_anterior: Optional[str]
    status_novo: str
    descricao: Optional[str]
    usuario_id: Optional[int]
    data_alteracao: datetime

    class Config:
        from_attributes = True
