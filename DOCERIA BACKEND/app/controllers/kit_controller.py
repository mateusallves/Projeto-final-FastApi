from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.depedencies import get_db, get_current_user
from app.services.kit_service import KitService

router = APIRouter(prefix="/kits", tags=["Kits"])
service = KitService()

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return service.listar(db)

@router.get("/{id}")
def buscar(id: int, db: Session = Depends(get_db)):
    return service.buscar(db, id)

@router.post("/")
def criar(nome: str, descricao: str, preco: float, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.criar(db, nome, descricao, preco)

@router.put("/{id}")
def editar(id: int, nome: str, descricao: str, preco: float, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.editar(db, id, nome, descricao, preco)

@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.deletar(db, id)
