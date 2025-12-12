from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.data.database import Base
import enum


class StatusPagamento(str, enum.Enum):
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    APROVADO = "aprovado"
    RECUSADO = "recusado"
    ESTORNADO = "estornado"
    CANCELADO = "cancelado"


class FormaPagamento(str, enum.Enum):
    DINHEIRO = "dinheiro"
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    TRANSFERENCIA = "transferencia"
    BOLETO = "boleto"


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Referência ao pedido
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    pedido = relationship("Pedido")
    
    # Valores
    valor = Column(Float, nullable=False)
    valor_pago = Column(Float, default=0.0)  # Valor efetivamente pago
    troco = Column(Float, default=0.0)  # Troco (para dinheiro)
    
    # Forma e status
    forma_pagamento = Column(String, nullable=False)
    status = Column(String, default=StatusPagamento.PENDENTE.value)
    
    # Dados do cartão (quando aplicável)
    bandeira_cartao = Column(String, nullable=True)  # Visa, Mastercard, etc
    ultimos_digitos = Column(String, nullable=True)  # Últimos 4 dígitos
    parcelas = Column(Integer, default=1)
    
    # Dados PIX/Transferência
    chave_pix = Column(String, nullable=True)
    codigo_pix = Column(String, nullable=True)  # Código copia e cola
    comprovante = Column(Text, nullable=True)  # URL ou base64 do comprovante
    
    # Dados do boleto
    codigo_barras = Column(String, nullable=True)
    linha_digitavel = Column(String, nullable=True)
    data_vencimento = Column(String, nullable=True)
    
    # Transação
    codigo_transacao = Column(String, nullable=True, index=True)  # ID da transação externa
    codigo_autorizacao = Column(String, nullable=True)
    nsu = Column(String, nullable=True)  # Número Sequencial Único
    
    # Datas
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_pagamento = Column(DateTime, nullable=True)  # Quando foi efetivamente pago
    data_estorno = Column(DateTime, nullable=True)
    
    # Observações e motivos
    observacoes = Column(Text, nullable=True)
    motivo_recusa = Column(String, nullable=True)
    motivo_estorno = Column(String, nullable=True)


class HistoricoPagamento(Base):
    """Histórico de alterações no pagamento"""
    __tablename__ = "historico_pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    pagamento_id = Column(Integer, ForeignKey("pagamentos.id"), nullable=False)
    
    status_anterior = Column(String, nullable=True)
    status_novo = Column(String, nullable=False)
    
    descricao = Column(String, nullable=True)
    usuario_id = Column(Integer, nullable=True)  # Quem fez a alteração
    
    data_alteracao = Column(DateTime, default=datetime.utcnow)
    
    pagamento = relationship("Pagamento")

