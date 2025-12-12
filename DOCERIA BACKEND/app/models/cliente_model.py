from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.data.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    telefone = Column(String, nullable=True)
    cpf = Column(String, unique=True, index=True, nullable=True)
    
    # Endereço
    endereco = Column(String, nullable=True)
    numero = Column(String, nullable=True)
    complemento = Column(String, nullable=True)
    bairro = Column(String, nullable=True)
    cidade = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    cep = Column(String, nullable=True)
    
    # Dados adicionais
    data_nascimento = Column(String, nullable=True)  # Para promoções de aniversário
    observacoes = Column(String, nullable=True)
    
    # Controle
    ativo = Column(Boolean, default=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

