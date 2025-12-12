from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.data.depedencies import get_db, get_current_user
from app.services.pedido_service import PedidoService
from app.schemas import (
    PedidoCreate, 
    PedidoUpdate, 
    PedidoOut, 
    PedidoResumo,
    AtualizarStatusPedido
)

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])
service = PedidoService()


@router.get("/", response_model=list[PedidoResumo], responses={
    200: {"description": "Lista de pedidos retornada com sucesso"}
})
def listar(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Limite de registros"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista todos os pedidos com filtros opcionais"""
    return service.listar(db, skip, limit, status, cliente_id)


@router.get("/pendentes", response_model=list[PedidoResumo], responses={
    200: {"description": "Lista de pedidos pendentes"}
})
def listar_pendentes(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista pedidos pendentes (não entregues e não cancelados)"""
    return service.pedidos_pendentes(db)


@router.get("/hoje", response_model=list[PedidoResumo], responses={
    200: {"description": "Lista de pedidos do dia"}
})
def listar_hoje(
    data: Optional[str] = Query(None, description="Data no formato YYYY-MM-DD (opcional, padrão: hoje)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista pedidos de uma data específica (padrão: hoje)"""
    return service.pedidos_do_dia(db, data)


@router.get("/estatisticas", responses={
    200: {"description": "Estatísticas dos pedidos"}
})
def estatisticas(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retorna estatísticas dos pedidos"""
    return service.estatisticas(db, data_inicio, data_fim)


@router.get("/total", responses={
    200: {"description": "Total de pedidos"}
})
def contar(
    status: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retorna o total de pedidos"""
    total = service.contar(db, status)
    return {"total": total}


@router.get("/cliente/{cliente_id}", response_model=list[PedidoResumo], responses={
    200: {"description": "Pedidos do cliente"}
})
def listar_por_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista todos os pedidos de um cliente"""
    return service.pedidos_cliente(db, cliente_id)


@router.get("/numero/{numero}", response_model=PedidoOut, responses={
    200: {"description": "Pedido encontrado"},
    404: {"description": "Pedido não encontrado"}
})
def buscar_por_numero(
    numero: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Busca um pedido pelo número (ex: PED-2024-0001)"""
    return service.buscar_por_numero(db, numero)


@router.get("/{id}", response_model=PedidoOut, responses={
    200: {"description": "Pedido encontrado"},
    404: {"description": "Pedido não encontrado"}
})
def buscar_por_id(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Busca um pedido pelo ID"""
    return service.buscar_por_id(db, id)


@router.post("/", response_model=PedidoOut, responses={
    200: {"description": "Pedido criado com sucesso"},
    400: {"description": "Dados inválidos"},
    404: {"description": "Cliente ou produto não encontrado"}
})
def criar(
    payload: PedidoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cria um novo pedido"""
    return service.criar(db, payload.model_dump())


@router.put("/{id}", response_model=PedidoOut, responses={
    200: {"description": "Pedido atualizado com sucesso"},
    400: {"description": "Não é possível editar este pedido"},
    404: {"description": "Pedido não encontrado"}
})
def atualizar(
    id: int,
    payload: PedidoUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Atualiza dados de um pedido"""
    return service.atualizar(db, id, payload.model_dump(exclude_unset=True))


@router.patch("/{id}/status", response_model=PedidoOut, responses={
    200: {"description": "Status atualizado com sucesso"},
    400: {"description": "Não é possível alterar status deste pedido"},
    404: {"description": "Pedido não encontrado"}
})
def atualizar_status(
    id: int,
    payload: AtualizarStatusPedido,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Atualiza o status de um pedido"""
    return service.atualizar_status(db, id, payload.status)


@router.patch("/{id}/confirmar", response_model=PedidoOut, responses={
    200: {"description": "Pedido confirmado"}
})
def confirmar(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Confirma um pedido pendente"""
    return service.atualizar_status(db, id, "confirmado")


@router.patch("/{id}/preparar", response_model=PedidoOut, responses={
    200: {"description": "Pedido em preparo"}
})
def iniciar_preparo(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marca pedido como em preparo"""
    return service.atualizar_status(db, id, "em_preparo")


@router.patch("/{id}/pronto", response_model=PedidoOut, responses={
    200: {"description": "Pedido pronto"}
})
def marcar_pronto(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marca pedido como pronto"""
    return service.atualizar_status(db, id, "pronto")


@router.patch("/{id}/sair-entrega", response_model=PedidoOut, responses={
    200: {"description": "Pedido saiu para entrega"}
})
def sair_entrega(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marca pedido como saiu para entrega"""
    return service.atualizar_status(db, id, "saiu_entrega")


@router.patch("/{id}/entregar", response_model=PedidoOut, responses={
    200: {"description": "Pedido entregue"}
})
def entregar(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Marca pedido como entregue"""
    return service.atualizar_status(db, id, "entregue")


@router.patch("/{id}/cancelar", response_model=PedidoOut, responses={
    200: {"description": "Pedido cancelado"},
    400: {"description": "Não é possível cancelar este pedido"}
})
def cancelar(
    id: int,
    motivo: Optional[str] = Query(None, description="Motivo do cancelamento"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cancela um pedido"""
    return service.cancelar(db, id, motivo)

