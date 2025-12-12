from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.kit_model import Kit

class KitService:

    def listar(self, db: Session):
        return db.query(Kit).all()

    def buscar(self, db: Session, id: int):
        kit = db.query(Kit).filter(Kit.id == id).first()
        if not kit:
            raise HTTPException(400, "Kit não encontrado.")
        return kit

    def criar(self, db: Session, nome: str, descricao: str, preco: float):
        try:
            novo = Kit(nome=nome, descricao=descricao, preco=preco)
            db.add(novo)
            db.commit()
            db.refresh(novo)
            return novo
        except:
            raise HTTPException(500, "Erro ao criar kit.")

    def editar(self, db: Session, id: int, nome: str, descricao: str, preco: float):
        kit = self.buscar(db, id)
        try:
            kit.nome = nome
            kit.descricao = descricao
            kit.preco = preco
            db.commit()
            db.refresh(kit)
            return kit
        except:
            raise HTTPException(500, "Erro ao atualizar kit.")

    def deletar(self, db: Session, id: int):
        kit = self.buscar(db, id)
        try:
            db.delete(kit)
            db.commit()
        except:
            raise HTTPException(500, "Erro ao remover kit.")
