from sqlalchemy import Column, Integer, String, Float
from app.data.database  import Base

class Kit(Base):
    __tablename__ = "kits"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    descricao = Column(String)
    preco = Column(Float)
