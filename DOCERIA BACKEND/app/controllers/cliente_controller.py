from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.data.depedencies import get_db, get_current_user
from app.services.cliente_service import ClienteService
from app.schemas import ClienteCreate, ClienteUpdate, ClienteOut, ClienteResumo

router = APIRouter(prefix="/clientes", tags=["Clientes"])
service = ClienteService()


@router.get("/", response_model=list[ClienteResumo], responses={
    200: {"description": "Lista de clientes retornada com sucesso"}
})
def listar(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    apenas_ativos: bool = Query(True, description="Filtrar apenas clientes ativos"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista todos os clientes com paginação"""
    return service.listar(db, skip, limit, apenas_ativos)


@router.get("/buscar", response_model=list[ClienteResumo], responses={
    200: {"description": "Clientes encontrados"}
})
def buscar(
    q: str = Query(..., min_length=2, description="Termo de busca (nome, email, telefone ou CPF)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Busca clientes por nome, email, telefone ou CPF"""
    return service.buscar(db, q)

@router.get("/por-email", response_model=ClienteOut, responses={
    200: {"description": "Cliente encontrado"},
    404: {"description": "Cliente não encontrado"}
})
def buscar_por_email(
    email: str = Query(..., description="Email do cliente"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Busca um cliente pelo email exato"""
    cliente = service.buscar_por_email(db, email)
    if not cliente:
        from fastapi import HTTPException
        raise HTTPException(404, "Cliente não encontrado.")
    return cliente


@router.get("/aniversariantes/{mes}", response_model=list[ClienteResumo], responses={
    200: {"description": "Lista de aniversariantes do mês"}
})
def aniversariantes(
    mes: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista clientes que fazem aniversário no mês especificado (1-12)"""
    if mes < 1 or mes > 12:
        from fastapi import HTTPException
        raise HTTPException(400, "Mês deve estar entre 1 e 12")
    return service.aniversariantes_do_mes(db, mes)


@router.get("/total", responses={
    200: {"description": "Total de clientes"}
})
def contar(
    apenas_ativos: bool = Query(True),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retorna o total de clientes cadastrados"""
    total = service.contar(db, apenas_ativos)
    return {"total": total}


@router.get("/{id}", response_model=ClienteOut, responses={
    200: {"description": "Cliente encontrado"},
    404: {"description": "Cliente não encontrado"}
})
def buscar_por_id(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Busca um cliente pelo ID"""
    return service.buscar_por_id(db, id)


@router.post("/", response_model=ClienteOut, responses={
    200: {"description": "Cliente criado com sucesso"},
    400: {"description": "Email ou CPF já cadastrado"},
    500: {"description": "Erro ao criar cliente"}
})
def criar(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cadastra um novo cliente"""
    # Usar exclude_none=True para não enviar campos None ao banco
    # Isso evita problemas com constraints NOT NULL antigas
    return service.criar(db, payload.model_dump(exclude_none=True))


@router.put("/{id}", response_model=ClienteOut, responses={
    200: {"description": "Cliente atualizado com sucesso"},
    400: {"description": "Email ou CPF já em uso por outro cliente"},
    404: {"description": "Cliente não encontrado"}
})
def atualizar(
    id: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Atualiza dados de um cliente"""
    return service.atualizar(db, id, payload.model_dump(exclude_unset=True))


@router.patch("/{id}/desativar", responses={
    200: {"description": "Cliente desativado com sucesso"},
    404: {"description": "Cliente não encontrado"}
})
def desativar(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Desativa um cliente (soft delete)"""
    return service.desativar(db, id)


@router.patch("/{id}/reativar", responses={
    200: {"description": "Cliente reativado com sucesso"},
    404: {"description": "Cliente não encontrado"}
})
def reativar(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Reativa um cliente desativado"""
    return service.reativar(db, id)


@router.delete("/{id}", responses={
    200: {"description": "Cliente removido permanentemente"},
    404: {"description": "Cliente não encontrado"}
})
def deletar(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Remove permanentemente um cliente (usar com cuidado!)"""
    return service.deletar(db, id)

