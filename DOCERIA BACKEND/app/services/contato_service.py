from sqlalchemy.orm import Session
from app.models.contato_model import Contato


class ContatoService:
    def criar(self, db: Session, contato_data: dict):
        contato = Contato(**contato_data)
        db.add(contato)
        db.commit()
        db.refresh(contato)
        return contato
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.contato_model import Contato


class ContatoService:

    def listar(self, db: Session):
        return db.query(Contato).all()

    def criar(self, db: Session, nome: str, email: str, telefone: str, mensagem: str):
        try:
            novo = Contato(
                nome=nome,
                email=email,
                telefone=telefone,
                mensagem=mensagem
            )
            db.add(novo)
            db.commit()
            db.refresh(novo)
            return novo
        except:
            raise HTTPException(500, "Erro ao enviar contato.")
