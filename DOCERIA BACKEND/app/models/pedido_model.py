from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.database import Base
import enum


class StatusPedido(str, enum.Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    EM_PREPARO = "em_preparo"
    PRONTO = "pronto"
    SAIU_ENTREGA = "saiu_entrega"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class TipoEntrega(str, enum.Enum):
    ENTREGA = "entrega"
    RETIRADA = "retirada"


class FormaPagamento(str, enum.Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    TRANSFERENCIA = "transferencia"


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    numero_pedido = Column(String, unique=True, index=True)  # Ex: PED-2024-0001
    
    # Cliente
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cliente = relationship("Cliente")
    
    # Status e tipo
    status = Column(String, default=StatusPedido.PENDENTE.value)
    tipo_entrega = Column(String, default=TipoEntrega.ENTREGA.value)
    
    # Datas
    data_pedido = Column(DateTime, default=datetime.utcnow)
    data_entrega = Column(String, nullable=True)  # Data desejada para entrega
    hora_entrega = Column(String, nullable=True)  # Hora desejada
    
    # Endereço de entrega (pode ser diferente do cadastro do cliente)
    endereco_entrega = Column(String, nullable=True)
    numero_entrega = Column(String, nullable=True)
    complemento_entrega = Column(String, nullable=True)
    bairro_entrega = Column(String, nullable=True)
    cidade_entrega = Column(String, nullable=True)
    estado_entrega = Column(String, nullable=True)
    cep_entrega = Column(String, nullable=True)
    
    # Valores
    subtotal = Column(Float, default=0.0)
    desconto = Column(Float, default=0.0)
    taxa_entrega = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    
    # Pagamento
    forma_pagamento = Column(String, nullable=True)
    troco_para = Column(Float, nullable=True)  # Se pagamento em dinheiro
    
    # Observações
    observacoes = Column(Text, nullable=True)
    
    # Controle
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com itens
    itens = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    
    # Produto ou Kit (um dos dois deve ser preenchido)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=True)
    kit_id = Column(Integer, ForeignKey("kits.id"), nullable=True)
    
    # Dados do item no momento do pedido (para histórico)
    nome_item = Column(String, nullable=False)
    descricao_item = Column(String, nullable=True)
    
    # Quantidade e valores
    quantidade = Column(Integer, default=1)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    # Personalizações/Observações do item
    observacoes = Column(Text, nullable=True)
    
    # Relacionamentos
    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")
    kit = relationship("Kit")

