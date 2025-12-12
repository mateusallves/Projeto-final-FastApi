from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from fastapi import HTTPException
from datetime import datetime, date
from typing import Optional
from app.models.pedido_model import Pedido, ItemPedido, StatusPedido
from app.models.produto_model import Produto
from app.models.kit_model import Kit
from app.models.cliente_model import Cliente


class PedidoService:

    def gerar_numero_pedido(self, db: Session) -> str:
        """Gera número único do pedido no formato PED-ANO-SEQUENCIAL"""
        ano = datetime.now().year
        
        # Busca o último pedido do ano
        ultimo = db.query(Pedido).filter(
            Pedido.numero_pedido.like(f"PED-{ano}-%")
        ).order_by(Pedido.id.desc()).first()
        
        if ultimo:
            # Extrai o número sequencial e incrementa
            try:
                seq = int(ultimo.numero_pedido.split("-")[-1]) + 1
            except:
                seq = 1
        else:
            seq = 1
        
        return f"PED-{ano}-{seq:04d}"

    def criar(self, db: Session, dados: dict) -> Pedido:
        """Cria um novo pedido"""
        # Verifica se cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == dados["cliente_id"]).first()
        if not cliente:
            raise HTTPException(404, "Cliente não encontrado.")
        
        if not cliente.ativo:
            raise HTTPException(400, "Cliente está inativo.")
        
        # Verifica se há itens
        itens_dados = dados.pop("itens", [])
        if not itens_dados:
            raise HTTPException(400, "Pedido deve ter pelo menos um item.")
        
        # Se usar endereço do cliente
        usar_endereco_cliente = dados.pop("usar_endereco_cliente", True)
        if usar_endereco_cliente and dados.get("tipo_entrega") == "entrega":
            dados["endereco_entrega"] = dados.get("endereco_entrega") or cliente.endereco
            dados["numero_entrega"] = dados.get("numero_entrega") or cliente.numero
            dados["complemento_entrega"] = dados.get("complemento_entrega") or cliente.complemento
            dados["bairro_entrega"] = dados.get("bairro_entrega") or cliente.bairro
            dados["cidade_entrega"] = dados.get("cidade_entrega") or cliente.cidade
            dados["estado_entrega"] = dados.get("estado_entrega") or cliente.estado
            dados["cep_entrega"] = dados.get("cep_entrega") or cliente.cep
        
        try:
            # Cria o pedido
            numero_pedido = self.gerar_numero_pedido(db)
            pedido = Pedido(
                numero_pedido=numero_pedido,
                cliente_id=dados["cliente_id"],
                status=StatusPedido.PENDENTE.value,
                tipo_entrega=dados.get("tipo_entrega", "entrega"),
                data_entrega=dados.get("data_entrega"),
                hora_entrega=dados.get("hora_entrega"),
                endereco_entrega=dados.get("endereco_entrega"),
                numero_entrega=dados.get("numero_entrega"),
                complemento_entrega=dados.get("complemento_entrega"),
                bairro_entrega=dados.get("bairro_entrega"),
                cidade_entrega=dados.get("cidade_entrega"),
                estado_entrega=dados.get("estado_entrega"),
                cep_entrega=dados.get("cep_entrega"),
                forma_pagamento=dados.get("forma_pagamento"),
                troco_para=dados.get("troco_para"),
                desconto=dados.get("desconto", 0.0),
                taxa_entrega=dados.get("taxa_entrega", 0.0),
                observacoes=dados.get("observacoes")
            )
            
            db.add(pedido)
            db.flush()  # Para obter o ID do pedido
            
            # Adiciona os itens
            subtotal = 0.0
            for item_dado in itens_dados:
                item = self._criar_item_pedido(db, pedido.id, item_dado)
                subtotal += item.subtotal
            
            # Atualiza totais
            pedido.subtotal = subtotal
            pedido.total = subtotal - pedido.desconto + pedido.taxa_entrega
            
            db.commit()
            db.refresh(pedido)
            
            # Cria pagamento automaticamente se forma_pagamento foi informada
            # Fazemos após o commit para evitar problemas de transação
            if dados.get("forma_pagamento"):
                try:
                    from app.models.pagamento_model import Pagamento, StatusPagamento
                    from app.services.pagamento_service import PagamentoService
                    
                    pagamento_service = PagamentoService()
                    pagamento_data = {
                        "pedido_id": pedido.id,
                        "valor": pedido.total,
                        "forma_pagamento": dados.get("forma_pagamento"),
                        "observacoes": f"Pagamento criado automaticamente para pedido {pedido.numero_pedido}"
                    }
                    
                    # Se for dinheiro, aprova automaticamente
                    if dados.get("forma_pagamento") == "dinheiro":
                        if dados.get("troco_para"):
                            pagamento_data["valor_pago"] = dados.get("troco_para")
                        else:
                            pagamento_data["valor_pago"] = pedido.total
                        pagamento_service.criar_pagamento_dinheiro(db, pagamento_data)
                    # Se for PIX, cria pendente
                    elif dados.get("forma_pagamento") == "pix":
                        pagamento_service.criar_pagamento_pix(db, pagamento_data)
                    # Outros métodos ficam pendentes
                    else:
                        pagamento_service.criar(db, pagamento_data)
                except Exception as e:
                    # Log do erro mas não falha o pedido
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Erro ao criar pagamento automático para pedido {pedido.id}: {e}")
            
            return pedido
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao criar pedido: {str(e)}")

    def _criar_item_pedido(self, db: Session, pedido_id: int, item_dado: dict) -> ItemPedido:
        """Cria um item do pedido"""
        produto_id = item_dado.get("produto_id")
        kit_id = item_dado.get("kit_id")
        quantidade = item_dado.get("quantidade", 1)
        
        if not produto_id and not kit_id:
            raise HTTPException(400, "Item deve ter um produto_id ou kit_id.")
        
        if produto_id and kit_id:
            raise HTTPException(400, "Item deve ter apenas produto_id OU kit_id, não ambos.")
        
        # Busca produto ou kit
        if produto_id:
            produto = db.query(Produto).filter(Produto.id == produto_id).first()
            if not produto:
                raise HTTPException(404, f"Produto {produto_id} não encontrado.")
            nome_item = produto.nome
            descricao_item = produto.descricao
            preco_unitario = produto.preco
        else:
            kit = db.query(Kit).filter(Kit.id == kit_id).first()
            if not kit:
                raise HTTPException(404, f"Kit {kit_id} não encontrado.")
            nome_item = kit.nome
            descricao_item = kit.descricao
            preco_unitario = kit.preco
        
        subtotal = preco_unitario * quantidade
        
        item = ItemPedido(
            pedido_id=pedido_id,
            produto_id=produto_id,
            kit_id=kit_id,
            nome_item=nome_item,
            descricao_item=descricao_item,
            quantidade=quantidade,
            preco_unitario=preco_unitario,
            subtotal=subtotal,
            observacoes=item_dado.get("observacoes")
        )
        
        db.add(item)
        return item

    def listar(self, db: Session, skip: int = 0, limit: int = 100, 
               status: Optional[str] = None, cliente_id: Optional[int] = None):
        """Lista pedidos com filtros"""
        query = db.query(Pedido)
        
        if status:
            query = query.filter(Pedido.status == status)
        
        if cliente_id:
            query = query.filter(Pedido.cliente_id == cliente_id)
        
        return query.order_by(Pedido.data_pedido.desc()).offset(skip).limit(limit).all()

    def buscar_por_id(self, db: Session, id: int) -> Pedido:
        """Busca pedido por ID"""
        pedido = db.query(Pedido).filter(Pedido.id == id).first()
        if not pedido:
            raise HTTPException(404, "Pedido não encontrado.")
        return pedido

    def buscar_por_numero(self, db: Session, numero: str) -> Pedido:
        """Busca pedido por número"""
        pedido = db.query(Pedido).filter(Pedido.numero_pedido == numero).first()
        if not pedido:
            raise HTTPException(404, "Pedido não encontrado.")
        return pedido

    def atualizar_status(self, db: Session, id: int, novo_status: str) -> Pedido:
        """Atualiza o status do pedido"""
        pedido = self.buscar_por_id(db, id)
        
        # Validações de transição de status
        status_atual = pedido.status
        
        # Não permite alterar pedido cancelado
        if status_atual == StatusPedido.CANCELADO.value:
            raise HTTPException(400, "Não é possível alterar status de pedido cancelado.")
        
        # Não permite alterar pedido entregue
        if status_atual == StatusPedido.ENTREGUE.value:
            raise HTTPException(400, "Não é possível alterar status de pedido já entregue.")
        
        try:
            pedido.status = novo_status
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao atualizar status: {str(e)}")

    def cancelar(self, db: Session, id: int, motivo: Optional[str] = None) -> Pedido:
        """Cancela um pedido"""
        pedido = self.buscar_por_id(db, id)
        
        # Não permite cancelar pedido já entregue
        if pedido.status == StatusPedido.ENTREGUE.value:
            raise HTTPException(400, "Não é possível cancelar pedido já entregue.")
        
        # Não permite cancelar pedido já cancelado
        if pedido.status == StatusPedido.CANCELADO.value:
            raise HTTPException(400, "Pedido já está cancelado.")
        
        try:
            pedido.status = StatusPedido.CANCELADO.value
            if motivo:
                pedido.observacoes = f"{pedido.observacoes or ''}\n[CANCELADO] {motivo}".strip()
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao cancelar pedido: {str(e)}")

    def atualizar(self, db: Session, id: int, dados: dict) -> Pedido:
        """Atualiza dados do pedido"""
        pedido = self.buscar_por_id(db, id)
        
        # Não permite editar pedido cancelado ou entregue
        if pedido.status in [StatusPedido.CANCELADO.value, StatusPedido.ENTREGUE.value]:
            raise HTTPException(400, "Não é possível editar pedido cancelado ou entregue.")
        
        # Remove campos None
        dados_atualizacao = {k: v for k, v in dados.items() if v is not None}
        
        try:
            for key, value in dados_atualizacao.items():
                if hasattr(pedido, key):
                    setattr(pedido, key, value)
            
            # Recalcula total se necessário
            if 'desconto' in dados_atualizacao or 'taxa_entrega' in dados_atualizacao:
                pedido.total = pedido.subtotal - pedido.desconto + pedido.taxa_entrega
            
            db.commit()
            db.refresh(pedido)
            return pedido
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao atualizar pedido: {str(e)}")

    def pedidos_do_dia(self, db: Session, data: Optional[str] = None):
        """Lista pedidos de uma data específica"""
        if data:
            data_filtro = data
        else:
            data_filtro = date.today().isoformat()
        
        pedidos = db.query(Pedido).filter(
            func.date(Pedido.data_pedido) == data_filtro
        ).order_by(Pedido.data_pedido.desc()).all()
        
        return pedidos

    def pedidos_por_status(self, db: Session, status: str):
        """Lista pedidos por status"""
        return db.query(Pedido).filter(
            Pedido.status == status
        ).order_by(Pedido.data_pedido.desc()).all()

    def pedidos_pendentes(self, db: Session):
        """Lista pedidos pendentes (não entregues e não cancelados)"""
        status_ativos = [
            StatusPedido.PENDENTE.value,
            StatusPedido.CONFIRMADO.value,
            StatusPedido.EM_PREPARO.value,
            StatusPedido.PRONTO.value,
            StatusPedido.SAIU_ENTREGA.value
        ]
        return db.query(Pedido).filter(
            Pedido.status.in_(status_ativos)
        ).order_by(Pedido.data_pedido.asc()).all()

    def estatisticas(self, db: Session, data_inicio: Optional[str] = None, data_fim: Optional[str] = None):
        """Retorna estatísticas dos pedidos"""
        query = db.query(Pedido)
        
        if data_inicio:
            query = query.filter(func.date(Pedido.data_pedido) >= data_inicio)
        if data_fim:
            query = query.filter(func.date(Pedido.data_pedido) <= data_fim)
        
        pedidos = query.all()
        
        total_pedidos = len(pedidos)
        pedidos_entregues = len([p for p in pedidos if p.status == StatusPedido.ENTREGUE.value])
        pedidos_cancelados = len([p for p in pedidos if p.status == StatusPedido.CANCELADO.value])
        pedidos_pendentes = len([p for p in pedidos if p.status not in [StatusPedido.ENTREGUE.value, StatusPedido.CANCELADO.value]])
        
        valor_total = sum(p.total for p in pedidos if p.status != StatusPedido.CANCELADO.value)
        ticket_medio = valor_total / pedidos_entregues if pedidos_entregues > 0 else 0
        
        return {
            "total_pedidos": total_pedidos,
            "pedidos_entregues": pedidos_entregues,
            "pedidos_cancelados": pedidos_cancelados,
            "pedidos_pendentes": pedidos_pendentes,
            "valor_total": round(valor_total, 2),
            "ticket_medio": round(ticket_medio, 2)
        }

    def pedidos_cliente(self, db: Session, cliente_id: int):
        """Lista todos os pedidos de um cliente"""
        return db.query(Pedido).filter(
            Pedido.cliente_id == cliente_id
        ).order_by(Pedido.data_pedido.desc()).all()

    def contar(self, db: Session, status: Optional[str] = None) -> int:
        """Conta pedidos"""
        query = db.query(Pedido)
        if status:
            query = query.filter(Pedido.status == status)
        return query.count()

