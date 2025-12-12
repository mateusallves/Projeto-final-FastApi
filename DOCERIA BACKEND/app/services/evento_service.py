from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.evento_model import Evento

class EventoService:

    def listar(self, db: Session):
        return db.query(Evento).all()

    def buscar(self, db: Session, id: int):
        evento = db.query(Evento).filter(Evento.id == id).first()
        if not evento:
            raise HTTPException(400, "Evento não encontrado.")
        return evento

    def criar(self, db: Session, titulo: str, descricao: str, data: str):
        try:
            novo = Evento(titulo=titulo, descricao=descricao, data=data)
            db.add(novo)
            db.commit()
            db.refresh(novo)
            return novo
        except:
            raise HTTPException(500, "Erro ao criar evento.")

    def editar(self, db: Session, id: int, titulo: str, descricao: str, data: str):
        evento = self.buscar(db, id)
        try:
            evento.titulo = titulo
            evento.descricao = descricao
            evento.data = data
            db.commit()
            db.refresh(evento)
            return evento
        except:
            raise HTTPException(500, "Erro ao atualizar evento.")

    def deletar(self, db: Session, id: int):
        evento = self.buscar(db, id)
        try:
            db.delete(evento)
            db.commit()
        except:
            raise HTTPException(500, "Erro ao excluir evento.")
