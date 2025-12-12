from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.depedencies import get_db, get_current_user
from app.services.produto_service import ProdutoService
from app.schemas import ProdutoCreate, ProdutoOut

router = APIRouter(prefix="/produtos", tags=["Produtos"])
service = ProdutoService()

@router.get("/", responses={
    200: {"description": "Lista de produtos retornada com sucesso"},
    500: {"description": "Erro interno"}
})
def listar(db: Session = Depends(get_db)):
    return service.listar(db)

@router.get("/{id}", responses={
    200: {"description": "Produto encontrado"},
    400: {"description": "Produto não encontrado"},
})
def buscar(id: int, db: Session = Depends(get_db)):
    return service.buscar(db, id)

@router.post("/", responses={
    200: {"description": "Produto criado com sucesso"},
    500: {"description": "Erro ao criar produto"}
})
def criar(
    payload: ProdutoCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.criar(db, payload.nome, payload.descricao, payload.preco, payload.categoria_id)

@router.put("/{id}", responses={
    200: {"description": "Produto atualizado com sucesso"},
    400: {"description": "Produto não encontrado"},
    500: {"description": "Erro interno"}
})
def editar(
    id: int,
    payload: ProdutoCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return service.editar(db, id, payload.nome, payload.descricao, payload.preco, payload.categoria_id)

@router.delete("/{id}", responses={
    200: {"description": "Produto removido"},
    400: {"description": "Produto não encontrado"},
    500: {"description": "Erro interno"}
})
def deletar(id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return service.deletar(db, id)
