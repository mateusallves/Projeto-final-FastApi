from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.data.depedencies import get_db, get_current_user
from app.services.pagamento_service import PagamentoService
from app.schemas import (
    PagamentoCreate,
    PagamentoDinheiro,
    PagamentoPix,
    PagamentoCartao,
    PagamentoUpdate,
    ConfirmarPagamento,
    EstornarPagamento,
    PagamentoOut,
    PagamentoResumo,
    HistoricoPagamentoOut
)

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])
service = PagamentoService()


@router.get("/", response_model=list[PagamentoResumo], responses={
    200: {"description": "Lista de pagamentos"}
})
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    forma_pagamento: Optional[str] = Query(None, description="Filtrar por forma de pagamento"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista todos os pagamentos com filtros"""
    return service.listar(db, skip, limit, status, forma_pagamento)


@router.get("/estatisticas", responses={
    200: {"description": "Estatísticas de pagamentos"}
})
def estatisticas(
    data_inicio: Optional[str] = Query(None, description="Data início (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data fim (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retorna estatísticas de pagamentos"""
    return service.estatisticas(db, data_inicio, data_fim)


@router.get("/total", responses={
    200: {"description": "Total de pagamentos"}
})
def contar(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Conta total de pagamentos"""
    total = service.contar(db, status)
    return {"total": total}


@router.get("/pedido/{pedido_id}", response_model=list[PagamentoResumo], responses={
    200: {"description": "Pagamentos do pedido"}
})
def listar_por_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista todos os pagamentos de um pedido"""
    return service.buscar_por_pedido(db, pedido_id)


@router.get("/cliente/{cliente_id}", response_model=list[PagamentoResumo], responses={
    200: {"description": "Pagamentos do cliente"}
})
def listar_por_cliente(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Lista todos os pagamentos de pedidos de um cliente"""
    pagamentos = service.buscar_por_cliente(db, cliente_id, skip, limit)
    # Adiciona número do pedido a cada pagamento
    return [
        PagamentoResumo(
            id=p.id,
            pedido_id=p.pedido_id,
            valor=p.valor,
            forma_pagamento=p.forma_pagamento,
            status=p.status,
            parcelas=p.parcelas,
            data_criacao=p.data_criacao,
            data_pagamento=p.data_pagamento,
            numero_pedido=p.pedido.numero_pedido if p.pedido else None
        )
        for p in pagamentos
    ]


@router.get("/pedido/{pedido_id}/aprovado", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento aprovado do pedido"},
    404: {"description": "Nenhum pagamento aprovado encontrado"}
})
def pagamento_aprovado(
    pedido_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retorna o pagamento aprovado de um pedido"""
    from fastapi import HTTPException
    pagamento = service.pagamento_aprovado_pedido(db, pedido_id)
    if not pagamento:
        raise HTTPException(404, "Nenhum pagamento aprovado encontrado para este pedido.")
    return pagamento


@router.get("/{id}", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento encontrado"},
    404: {"description": "Pagamento não encontrado"}
})
def buscar_por_id(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Busca um pagamento pelo ID"""
    pagamento = service.buscar_por_id(db, id)
    # Adiciona número do pedido
    return PagamentoOut(
        id=pagamento.id,
        pedido_id=pagamento.pedido_id,
        valor=pagamento.valor,
        valor_pago=pagamento.valor_pago,
        troco=pagamento.troco,
        forma_pagamento=pagamento.forma_pagamento,
        status=pagamento.status,
        bandeira_cartao=pagamento.bandeira_cartao,
        ultimos_digitos=pagamento.ultimos_digitos,
        parcelas=pagamento.parcelas,
        chave_pix=pagamento.chave_pix,
        codigo_pix=pagamento.codigo_pix,
        codigo_transacao=pagamento.codigo_transacao,
        codigo_autorizacao=pagamento.codigo_autorizacao,
        nsu=pagamento.nsu,
        data_criacao=pagamento.data_criacao,
        data_pagamento=pagamento.data_pagamento,
        data_estorno=pagamento.data_estorno,
        observacoes=pagamento.observacoes,
        motivo_recusa=pagamento.motivo_recusa,
        motivo_estorno=pagamento.motivo_estorno,
        numero_pedido=pagamento.pedido.numero_pedido if pagamento.pedido else None
    )


@router.get("/{id}/historico", response_model=list[HistoricoPagamentoOut], responses={
    200: {"description": "Histórico do pagamento"}
})
def historico(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Retorna o histórico de alterações de um pagamento"""
    return service.historico(db, id)


@router.post("/", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento criado"},
    400: {"description": "Dados inválidos ou pagamento já existe"},
    404: {"description": "Pedido não encontrado"}
})
def criar(
    payload: PagamentoCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cria um novo pagamento (genérico)"""
    return service.criar(db, payload.model_dump())


@router.post("/dinheiro", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento em dinheiro criado e aprovado"}
})
def criar_dinheiro(
    payload: PagamentoDinheiro,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cria pagamento em dinheiro (já aprovado automaticamente)"""
    return service.criar_pagamento_dinheiro(db, payload.model_dump())


@router.post("/pix", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento PIX criado"}
})
def criar_pix(
    payload: PagamentoPix,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cria pagamento PIX (código PIX gerado automaticamente)"""
    return service.criar_pagamento_pix(db, payload.model_dump())


@router.post("/cartao", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento com cartão criado"}
})
def criar_cartao(
    payload: PagamentoCartao,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cria pagamento com cartão de crédito ou débito"""
    return service.criar_pagamento_cartao(db, payload.model_dump())


@router.patch("/{id}/confirmar", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento confirmado/aprovado"},
    400: {"description": "Não é possível confirmar este pagamento"}
})
def confirmar(
    id: int,
    payload: ConfirmarPagamento = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Confirma/aprova um pagamento pendente"""
    dados = payload.model_dump() if payload else None
    return service.confirmar(db, id, dados)


@router.patch("/{id}/recusar", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento recusado"},
    400: {"description": "Não é possível recusar este pagamento"}
})
def recusar(
    id: int,
    motivo: str = Query(..., description="Motivo da recusa"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Recusa um pagamento pendente"""
    return service.recusar(db, id, motivo)


@router.patch("/{id}/estornar", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento estornado"},
    400: {"description": "Não é possível estornar este pagamento"}
})
def estornar(
    id: int,
    payload: EstornarPagamento,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Estorna um pagamento aprovado"""
    return service.estornar(db, id, payload.model_dump())


@router.patch("/{id}/cancelar", response_model=PagamentoOut, responses={
    200: {"description": "Pagamento cancelado"},
    400: {"description": "Não é possível cancelar este pagamento"}
})
def cancelar(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Cancela um pagamento pendente"""
    return service.cancelar(db, id)

