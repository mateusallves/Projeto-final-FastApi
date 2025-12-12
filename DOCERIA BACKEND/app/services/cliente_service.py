from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.cliente_model import Cliente
from typing import Optional
import logging
import sqlite3
import os
from app.config import settings

logger = logging.getLogger(__name__)


class ClienteService:

    def listar(self, db: Session, skip: int = 0, limit: int = 100, apenas_ativos: bool = True):
        query = db.query(Cliente)
        if apenas_ativos:
            query = query.filter(Cliente.ativo == True)
        return query.offset(skip).limit(limit).all()

    def buscar_por_id(self, db: Session, id: int):
        cliente = db.query(Cliente).filter(Cliente.id == id).first()
        if not cliente:
            raise HTTPException(404, "Cliente não encontrado.")
        return cliente

    def buscar_por_email(self, db: Session, email: str):
        # Busca case-insensitive por email
        return db.query(Cliente).filter(Cliente.email.ilike(email)).first()

    def buscar_por_cpf(self, db: Session, cpf: str):
        if not cpf:
            return None
        return db.query(Cliente).filter(Cliente.cpf == cpf).first()

    def buscar(self, db: Session, termo: str):
        termo_lower = termo.lower()
        # Se o termo parece ser um email (contém @), buscar primeiro por email exato
        if "@" in termo:
            cliente_exato = db.query(Cliente).filter(Cliente.email.ilike(termo)).first()
            if cliente_exato:
                return [cliente_exato]
        
        # Busca geral por nome, email, telefone ou CPF
        clientes = db.query(Cliente).filter(
            (Cliente.nome.ilike(f"%{termo}%")) |
            (Cliente.email.ilike(f"%{termo}%")) |
            (Cliente.telefone.ilike(f"%{termo}%")) |
            (Cliente.cpf.ilike(f"%{termo}%"))
        ).all()
        return clientes

    def _migrate_telefone_if_needed(self):
        """Migra o banco de dados para permitir telefone NULL se necessário"""
        try:
            db_path = settings.DATABASE_URL.replace('sqlite:///', '')
            if not os.path.exists(db_path):
                return False
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se telefone tem NOT NULL
            cursor.execute("PRAGMA table_info(clientes)")
            columns = cursor.fetchall()
            telefone_col = [col for col in columns if col[1] == 'telefone' and col[3] == 1]
            
            if telefone_col:
                logger.info("Migrando banco de dados para permitir telefone NULL...")
                cursor.execute("""
                    CREATE TABLE clientes_new (
                        id INTEGER NOT NULL PRIMARY KEY,
                        nome VARCHAR NOT NULL,
                        email VARCHAR NOT NULL UNIQUE,
                        telefone VARCHAR,
                        cpf VARCHAR UNIQUE,
                        endereco VARCHAR,
                        numero VARCHAR,
                        complemento VARCHAR,
                        bairro VARCHAR,
                        cidade VARCHAR,
                        estado VARCHAR,
                        cep VARCHAR,
                        data_nascimento VARCHAR,
                        observacoes VARCHAR,
                        ativo BOOLEAN,
                        data_cadastro DATETIME,
                        data_atualizacao DATETIME
                    )
                """)
                cursor.execute("INSERT INTO clientes_new SELECT * FROM clientes")
                cursor.execute("DROP TABLE clientes")
                cursor.execute("ALTER TABLE clientes_new RENAME TO clientes")
                cursor.execute("CREATE UNIQUE INDEX ix_clientes_email ON clientes (email)")
                cursor.execute("CREATE INDEX ix_clientes_cpf ON clientes (cpf)")
                cursor.execute("CREATE INDEX ix_clientes_id ON clientes (id)")
                conn.commit()
                logger.info("Migração concluída com sucesso!")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao migrar banco: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def criar(self, db: Session, dados: dict):
        """Cria um novo cliente"""
        # Verifica se email já existe - se existir, retorna o cliente existente
        cliente_existente = self.buscar_por_email(db, dados["email"])
        if cliente_existente:
            logger.info(f"Cliente já existe com email {dados['email']}, retornando cliente existente (ID: {cliente_existente.id})")
            return cliente_existente

        # Verifica se CPF já existe (se fornecido)
        if dados.get("cpf") and self.buscar_por_cpf(db, dados["cpf"]):
            raise HTTPException(400, "CPF já cadastrado.")

        # Remove campos None e strings vazias do dicionário para evitar problemas com constraints do banco
        # Isso é necessário porque o banco pode ainda ter constraints NOT NULL antigas
        logger.info(f"Dados recebidos para criar cliente: {dados}")
        
        dados_limpos = {}
        for k, v in dados.items():
            # Só incluir se não for None e não for string vazia
            if v is not None and v != '':
                dados_limpos[k] = v
        
        logger.info(f"Dados limpos (após remover None/vazios): {dados_limpos}")
        
        # Garantir que campos obrigatórios estejam presentes
        if 'nome' not in dados_limpos or 'email' not in dados_limpos:
            raise HTTPException(400, "Nome e email são obrigatórios")
        
        # Garantir que telefone não esteja no dicionário se for None
        if 'telefone' in dados_limpos and dados_limpos['telefone'] is None:
            del dados_limpos['telefone']
        
        try:
            # Criar objeto Cliente apenas com os campos que temos valores
            # Usar setattr para definir apenas os campos que temos, evitando que SQLAlchemy
            # tente inserir None em campos que não foram passados
            novo_cliente = Cliente()
            for key, value in dados_limpos.items():
                setattr(novo_cliente, key, value)
            
            db.add(novo_cliente)
            db.commit()
            db.refresh(novo_cliente)
            return novo_cliente
        except Exception as e:
            db.rollback()
            error_str = str(e)
            logger.error(f"Erro ao criar cliente: {error_str}", exc_info=True)
            
            # Se o erro for relacionado a constraint NOT NULL em telefone, tentar migração automática
            if "NOT NULL constraint failed" in error_str and "telefone" in error_str:
                logger.warning("Constraint NOT NULL detectada na coluna telefone. Tentando migração automática...")
                if self._migrate_telefone_if_needed():
                    # Tentar novamente após migração
                    try:
                        novo_cliente = Cliente()
                        for key, value in dados_limpos.items():
                            setattr(novo_cliente, key, value)
                        db.add(novo_cliente)
                        db.commit()
                        db.refresh(novo_cliente)
                        logger.info("Cliente criado com sucesso após migração automática")
                        return novo_cliente
                    except Exception as e2:
                        db.rollback()
                        logger.error(f"Erro ao criar cliente após migração: {e2}")
                        raise HTTPException(500, f"Erro ao criar cliente: {str(e2)}")
                else:
                    raise HTTPException(500, f"Erro ao criar cliente: {error_str}. Execute a migração do banco manualmente.")
            
            raise HTTPException(500, f"Erro ao criar cliente: {error_str}")

    def atualizar(self, db: Session, id: int, dados: dict):
        """Atualiza dados de um cliente"""
        cliente = self.buscar_por_id(db, id)

        # Remove campos None do dicionário
        dados_atualizacao = {k: v for k, v in dados.items() if v is not None}

        # Verifica se o novo email já existe (se estiver sendo atualizado)
        if "email" in dados_atualizacao:
            cliente_existente = self.buscar_por_email(db, dados_atualizacao["email"])
            if cliente_existente and cliente_existente.id != id:
                raise HTTPException(400, "Email já cadastrado por outro cliente.")

        # Verifica se o novo CPF já existe (se estiver sendo atualizado)
        if "cpf" in dados_atualizacao:
            cliente_existente = self.buscar_por_cpf(db, dados_atualizacao["cpf"])
            if cliente_existente and cliente_existente.id != id:
                raise HTTPException(400, "CPF já cadastrado por outro cliente.")

        try:
            for key, value in dados_atualizacao.items():
                setattr(cliente, key, value)
            db.commit()
            db.refresh(cliente)
            return cliente
        except Exception as e:
            db.rollback()
            raise HTTPException(500, f"Erro ao atualizar cliente: {str(e)}")

    def desativar(self, db: Session, id: int):
        """Desativa um cliente (soft delete)"""
        cliente = self.buscar_por_id(db, id)
        cliente.ativo = False
        db.commit()
        db.refresh(cliente)
        return cliente

    def reativar(self, db: Session, id: int):
        """Reativa um cliente desativado"""
        cliente = self.buscar_por_id(db, id)
        cliente.ativo = True
        db.commit()
        db.refresh(cliente)
        return cliente

    def deletar(self, db: Session, id: int):
        """Remove permanentemente um cliente"""
        cliente = self.buscar_por_id(db, id)
        db.delete(cliente)
        db.commit()
        return {"message": "Cliente removido permanentemente."}

    def contar(self, db: Session, apenas_ativos: bool = True):
        """Retorna o total de clientes"""
        query = db.query(Cliente)
        if apenas_ativos:
            query = query.filter(Cliente.ativo == True)
        return query.count()

    def aniversariantes_do_mes(self, db: Session, mes: int):
        """Lista clientes que fazem aniversário no mês especificado"""
        # Assumindo que data_nascimento está no formato "YYYY-MM-DD" ou "DD/MM/YYYY"
        clientes = db.query(Cliente).filter(Cliente.ativo == True).all()
        aniversariantes = []
        for cliente in clientes:
            if cliente.data_nascimento:
                try:
                    # Tentar diferentes formatos de data
                    if "/" in cliente.data_nascimento:
                        partes = cliente.data_nascimento.split("/")
                        if len(partes) >= 2 and int(partes[1]) == mes:
                            aniversariantes.append(cliente)
                    elif "-" in cliente.data_nascimento:
                        partes = cliente.data_nascimento.split("-")
                        if len(partes) >= 2 and int(partes[1]) == mes:
                            aniversariantes.append(cliente)
                except:
                    continue
        return aniversariantes
