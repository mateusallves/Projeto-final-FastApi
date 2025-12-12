from sqlalchemy import Column, Integer, String, Date
from app.data.database  import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    descricao = Column(String)
    data = Column(String)
