from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.data.database  import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True)
    descricao = Column(String)
    preco = Column(Float)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))

    categoria = relationship("Categoria")
