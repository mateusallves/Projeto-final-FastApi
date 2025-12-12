from sqlalchemy import Column, Integer, String, Text
from app.data.database import Base


class Contato(Base):
    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    email = Column(String, index=True)
    telefone = Column(String, nullable=True)
    numero_pessoas = Column(Integer, nullable=True)
    tipo_evento = Column(String, nullable=True)
    data = Column(String, nullable=True)
    local = Column(String, nullable=True)
    observacao = Column(Text, nullable=True)
