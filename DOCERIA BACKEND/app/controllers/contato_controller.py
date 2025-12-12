from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.depedencies import get_db
from app.services.contato_service import ContatoService
from app.schemas import ContatoCreate, ContatoOut

router = APIRouter(prefix="/contato", tags=["Contato"])
service = ContatoService()


@router.post("/", response_model=ContatoOut)
def enviar(contato: ContatoCreate, db: Session = Depends(get_db)):
    c = service.criar(db, contato.dict())
    return c
