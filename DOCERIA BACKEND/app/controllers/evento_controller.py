from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.depedencies import get_db, get_current_user
from app.services.evento_service import EventoService

router = APIRouter(prefix="/eventos", tags=["Eventos"])
service = EventoService()

@router.get("/")
def listar(db: Session = Depends(get_db)):
    return service.listar(db)

@router.get("/{id}")
def buscar(id: int, db: Session = Depends(get_db)):
    return service.buscar(db, id)

@router.post("/")
def criar(titulo: str, descricao: str, data: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.criar(db, titulo, descricao, data)

@router.put("/{id}")
def editar(id: int, titulo: str, descricao: str, data: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.editar(db, id, titulo, descricao, data)

@router.delete("/{id}")
def deletar(id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.deletar(db, id)
