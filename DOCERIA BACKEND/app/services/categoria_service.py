from app.models.categoria_model import Categoria
from sqlalchemy.orm import Session

class CategoriaService:

    def listar(self, db: Session):
        return db.query(Categoria).all()

    def criar(self, db: Session, nome: str):
        cat = Categoria(nome=nome)
        db.add(cat)
        db.commit()
        db.refresh(cat)
        return cat

    def deletar(self, db: Session, id: int):
        db.query(Categoria).filter(Categoria.id == id).delete()
        db.commit()
