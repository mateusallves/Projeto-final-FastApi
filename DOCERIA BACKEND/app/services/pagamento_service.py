from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime
from typing import Optional
import uuid
from app.models.pagamento_model import Pagamento, HistoricoPagamento, StatusPagamento
from app.models.pedido_model import Pedido, StatusPedido


class PagamentoService:

    def _gerar_codigo_pix(self) -> str:
        """Gera um código PIX simulado"""
        return f"PIX{uuid.uuid4().hex[:20].upper()}"

    def _registrar_historico(self, db: Session, pagamento_id: int, 
                            status_anterior: str, status_novo: str,
                            descricao: str = None, usuario_id: int = None):
        """Registra alteração no histórico"""
        historico = HistoricoPagamento(
            pagamento_id=pagamento_id,
            status_anterior=status_anterior,
            status_novo=status_novo,
            descricao=descricao,
            usuario_id=usuario_id
        )
        db.add(historico)

    def criar(self, db: Session, dados: dict) -> Pagamento:
        """Cria um novo pagamento"""
        pedido_id = dados.get("pedido_id")
        
        # Verifica se pedido existe
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if not pedido:
            raise HTTPException(404, "Pedido não encontrado.")
        
        # Verifica se pedido não está cancelado
        if pedido.status == StatusPedido.CANCELADO.value:
            raise HTTPException(400, "Não é possível criar pagamento para pedido cancelado.")
        
        # Verifica se já existe pagamento aprovado para este pedido
        pagamento_existente = db.query(Pagamento).filter(
            Pagamento.pedido_id == pedido_id,
            Pagamento.status == StatusPagamento.APROVADO.value
        ).first()
        
        if pagamento_existente:
            raise HTTPException(400, "Já existe um pagamento aprovado para este pedido.")
        
        forma_pagamento = dados.get("forma_pagamento")
        valor = dados.get("valor")
        
        try:
            pagamento = Pagamento(
                pedido_id=pedido_id,
                valor=valor,
                forma_pagamento=forma_pagamento,
                status=StatusPagamento.PENDENTE.value,
                bandeira_cartao=dados.get("bandeira_cartao"),
                ultimos_digitos=dados.get("ultimos_digitos"),
                parcelas=dados.get("parcelas", 1),
                chave_pix=dados.get("chave_pix"),
                comprovante=dados.get("comprovante"),
                codigo_transacao=dados.get("codigo_transacao"),
                codigo_autorizacao=dados.get("codigo_autorizacao"),
                nsu=dados.get("nsu"),
                observacoes=dados.get("observacoes")
            )
            
            # Gera código PIX se for pagamento PIX
            if forma_pagamento == "pix":
                pagamento.codigo_pix = self._gerar_codigo_pix()
            
            # Calcula troco se for dinheiro
            if forma_pagamento == "dinheiro":
                valor_pago = dados.get("valor_pago", valor)
                pagamento.valor_pago = valor_pago
                pagamento.troco = max(0, valor_pago - valor)
            
            db.add(pagamento)
            db.flush()
            
            # Registra no histórico
            self._registrar_historico(
                db, pagamento.id, None, StatusPagamento.PENDENTE.value,
                "Pagamento criado"
            )
            
            db.commit()
            db.refresh(pagamento)
            return pagamento
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao criar pagamento: {str(e)}")

    def criar_pagamento_dinheiro(self, db: Session, dados: dict) -> Pagamento:
        """Cria pagamento em dinheiro e já aprova"""
        dados["forma_pagamento"] = "dinheiro"
        pagamento = self.criar(db, dados)
        
        # Dinheiro é aprovado imediatamente
        return self.confirmar(db, pagamento.id)

    def criar_pagamento_pix(self, db: Session, dados: dict) -> Pagamento:
        """Cria pagamento PIX"""
        dados["forma_pagamento"] = "pix"
        return self.criar(db, dados)

    def criar_pagamento_cartao(self, db: Session, dados: dict) -> Pagamento:
        """Cria pagamento com cartão"""
        tipo = dados.pop("tipo", "credito")
        dados["forma_pagamento"] = f"cartao_{tipo}"
        return self.criar(db, dados)

    def buscar_por_id(self, db: Session, id: int) -> Pagamento:
        """Busca pagamento por ID"""
        from sqlalchemy.orm import joinedload
        pagamento = db.query(Pagamento).options(joinedload(Pagamento.pedido)).filter(Pagamento.id == id).first()
        if not pagamento:
            raise HTTPException(404, "Pagamento não encontrado.")
        return pagamento

    def buscar_por_pedido(self, db: Session, pedido_id: int) -> list[Pagamento]:
        """Busca todos os pagamentos de um pedido"""
        return db.query(Pagamento).filter(
            Pagamento.pedido_id == pedido_id
        ).order_by(Pagamento.data_criacao.desc()).all()

    def buscar_por_cliente(self, db: Session, cliente_id: int, skip: int = 0, limit: int = 100) -> list[Pagamento]:
        """Busca todos os pagamentos de pedidos de um cliente"""
        from app.models.cliente_model import Cliente
        from sqlalchemy.orm import joinedload
        
        # Verifica se cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
        if not cliente:
            raise HTTPException(404, "Cliente não encontrado.")
        
        # Busca pagamentos através dos pedidos do cliente, carregando relacionamento
        return db.query(Pagamento).options(joinedload(Pagamento.pedido)).join(Pedido).filter(
            Pedido.cliente_id == cliente_id
        ).order_by(Pagamento.data_criacao.desc()).offset(skip).limit(limit).all()

    def pagamento_aprovado_pedido(self, db: Session, pedido_id: int) -> Optional[Pagamento]:
        """Retorna o pagamento aprovado de um pedido, se existir"""
        return db.query(Pagamento).filter(
            Pagamento.pedido_id == pedido_id,
            Pagamento.status == StatusPagamento.APROVADO.value
        ).first()

    def listar(self, db: Session, skip: int = 0, limit: int = 100,
               status: Optional[str] = None, forma_pagamento: Optional[str] = None):
        """Lista pagamentos com filtros"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(Pagamento).options(joinedload(Pagamento.pedido))
        
        if status:
            query = query.filter(Pagamento.status == status)
        
        if forma_pagamento:
            query = query.filter(Pagamento.forma_pagamento == forma_pagamento)
        
        return query.order_by(Pagamento.data_criacao.desc()).offset(skip).limit(limit).all()

    def confirmar(self, db: Session, id: int, dados: dict = None) -> Pagamento:
        """Confirma/aprova um pagamento"""
        pagamento = self.buscar_por_id(db, id)
        
        if pagamento.status == StatusPagamento.APROVADO.value:
            raise HTTPException(400, "Pagamento já está aprovado.")
        
        if pagamento.status in [StatusPagamento.CANCELADO.value, StatusPagamento.ESTORNADO.value]:
            raise HTTPException(400, "Não é possível confirmar este pagamento.")
        
        try:
            status_anterior = pagamento.status
            pagamento.status = StatusPagamento.APROVADO.value
            pagamento.data_pagamento = datetime.utcnow()
            pagamento.valor_pago = pagamento.valor_pago or pagamento.valor
            
            # Atualiza dados adicionais se fornecidos
            if dados:
                if dados.get("codigo_transacao"):
                    pagamento.codigo_transacao = dados["codigo_transacao"]
                if dados.get("codigo_autorizacao"):
                    pagamento.codigo_autorizacao = dados["codigo_autorizacao"]
                if dados.get("nsu"):
                    pagamento.nsu = dados["nsu"]
                if dados.get("comprovante"):
                    pagamento.comprovante = dados["comprovante"]
                if dados.get("observacoes"):
                    pagamento.observacoes = dados["observacoes"]
            
            # Registra no histórico
            self._registrar_historico(
                db, pagamento.id, status_anterior, StatusPagamento.APROVADO.value,
                "Pagamento confirmado/aprovado"
            )
            
            # Confirma o pedido se estiver pendente
            pedido = db.query(Pedido).filter(Pedido.id == pagamento.pedido_id).first()
            if pedido and pedido.status == StatusPedido.PENDENTE.value:
                pedido.status = StatusPedido.CONFIRMADO.value
            
            db.commit()
            db.refresh(pagamento)
            return pagamento
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao confirmar pagamento: {str(e)}")

    def recusar(self, db: Session, id: int, motivo: str) -> Pagamento:
        """Recusa um pagamento"""
        pagamento = self.buscar_por_id(db, id)
        
        if pagamento.status != StatusPagamento.PENDENTE.value:
            raise HTTPException(400, "Só é possível recusar pagamentos pendentes.")
        
        try:
            status_anterior = pagamento.status
            pagamento.status = StatusPagamento.RECUSADO.value
            pagamento.motivo_recusa = motivo
            
            self._registrar_historico(
                db, pagamento.id, status_anterior, StatusPagamento.RECUSADO.value,
                f"Pagamento recusado: {motivo}"
            )
            
            db.commit()
            db.refresh(pagamento)
            return pagamento
            
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao recusar pagamento: {str(e)}")

    def estornar(self, db: Session, id: int, dados: dict) -> Pagamento:
        """Estorna um pagamento aprovado"""
        pagamento = self.buscar_por_id(db, id)
        
        if pagamento.status != StatusPagamento.APROVADO.value:
            raise HTTPException(400, "Só é possível estornar pagamentos aprovados.")
        
        motivo = dados.get("motivo")
        if not motivo:
            raise HTTPException(400, "Motivo do estorno é obrigatório.")
        
        try:
            status_anterior = pagamento.status
            pagamento.status = StatusPagamento.ESTORNADO.value
            pagamento.motivo_estorno = motivo
            pagamento.data_estorno = datetime.utcnow()
            
            self._registrar_historico(
                db, pagamento.id, status_anterior, StatusPagamento.ESTORNADO.value,
                f"Pagamento estornado: {motivo}"
            )
            
            db.commit()
            db.refresh(pagamento)
            return pagamento
            
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao estornar pagamento: {str(e)}")

    def cancelar(self, db: Session, id: int) -> Pagamento:
        """Cancela um pagamento pendente"""
        pagamento = self.buscar_por_id(db, id)
        
        if pagamento.status != StatusPagamento.PENDENTE.value:
            raise HTTPException(400, "Só é possível cancelar pagamentos pendentes.")
        
        try:
            status_anterior = pagamento.status
            pagamento.status = StatusPagamento.CANCELADO.value
            
            self._registrar_historico(
                db, pagamento.id, status_anterior, StatusPagamento.CANCELADO.value,
                "Pagamento cancelado"
            )
            
            db.commit()
            db.refresh(pagamento)
            return pagamento
            
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao cancelar pagamento: {str(e)}")

    def historico(self, db: Session, pagamento_id: int) -> list[HistoricoPagamento]:
        """Retorna o histórico de um pagamento"""
        return db.query(HistoricoPagamento).filter(
            HistoricoPagamento.pagamento_id == pagamento_id
        ).order_by(HistoricoPagamento.data_alteracao.desc()).all()

    def estatisticas(self, db: Session, data_inicio: Optional[str] = None, 
                    data_fim: Optional[str] = None):
        """Retorna estatísticas de pagamentos"""
        query = db.query(Pagamento)
        
        if data_inicio:
            query = query.filter(func.date(Pagamento.data_criacao) >= data_inicio)
        if data_fim:
            query = query.filter(func.date(Pagamento.data_criacao) <= data_fim)
        
        pagamentos = query.all()
        
        # Estatísticas gerais
        total = len(pagamentos)
        aprovados = [p for p in pagamentos if p.status == StatusPagamento.APROVADO.value]
        pendentes = [p for p in pagamentos if p.status == StatusPagamento.PENDENTE.value]
        recusados = [p for p in pagamentos if p.status == StatusPagamento.RECUSADO.value]
        estornados = [p for p in pagamentos if p.status == StatusPagamento.ESTORNADO.value]
        
        valor_aprovado = sum(p.valor for p in aprovados)
        valor_estornado = sum(p.valor for p in estornados)
        
        # Por forma de pagamento
        por_forma = {}
        for p in aprovados:
            forma = p.forma_pagamento
            if forma not in por_forma:
                por_forma[forma] = {"quantidade": 0, "valor": 0.0}
            por_forma[forma]["quantidade"] += 1
            por_forma[forma]["valor"] += p.valor
        
        return {
            "total_pagamentos": total,
            "aprovados": len(aprovados),
            "pendentes": len(pendentes),
            "recusados": len(recusados),
            "estornados": len(estornados),
            "valor_total_aprovado": round(valor_aprovado, 2),
            "valor_total_estornado": round(valor_estornado, 2),
            "valor_liquido": round(valor_aprovado - valor_estornado, 2),
            "por_forma_pagamento": por_forma
        }

    def contar(self, db: Session, status: Optional[str] = None) -> int:
        """Conta pagamentos"""
        query = db.query(Pagamento)
        if status:
            query = query.filter(Pagamento.status == status)
        return query.count()

