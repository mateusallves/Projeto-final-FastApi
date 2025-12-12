from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.produto_model import Produto

class ProdutoService:

    def listar(self, db: Session):
        return db.query(Produto).all()

    def buscar(self, db: Session, id: int):
        produto = db.query(Produto).filter(Produto.id == id).first()
        if not produto:
            raise HTTPException(400, "Produto não encontrado.")
        return produto

    def criar(self, db: Session, nome: str, descricao: str, preco: float, categoria_id: int):
        try:
            novo = Produto(
                nome=nome,
                descricao=descricao,
                preco=preco,
                categoria_id=categoria_id
            )
            db.add(novo)
            db.commit()
            db.refresh(novo)
            return novo
        except Exception:
            raise HTTPException(500, "Erro ao criar produto.")

    def editar(self, db: Session, id: int, nome: str, descricao: str, preco: float, categoria_id: int):
        prod = self.buscar(db, id)
        try:
            prod.nome = nome
            prod.descricao = descricao
            prod.preco = preco
            prod.categoria_id = categoria_id

            db.commit()
            db.refresh(prod)
            return prod
        except:
            raise HTTPException(500, "Erro ao atualizar produto.")

    def deletar(self, db: Session, id: int):
        prod = self.buscar(db, id)
        try:
            db.delete(prod)
            db.commit()
        except:
            raise HTTPException(500, "Erro ao excluir produto.")
