from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.depedencies import get_db, get_current_user
from app.services.categoria_service import CategoriaService
from app.schemas import CategoriaCreate, CategoriaOut

router = APIRouter(prefix="/categorias", tags=["Categorias"])
service = CategoriaService()


@router.get("/", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    return service.listar(db)


@router.post("/", response_model=CategoriaOut)
def criar(payload: CategoriaCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.criar(db, payload.nome)


@router.delete("/{id}")
def deletar(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return service.deletar(db, id)
