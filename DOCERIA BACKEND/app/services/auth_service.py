import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
import bcrypt
from app.models.user_model import User
from app.models.cliente_model import Cliente
from app.services.token_service import criar_token

logger = logging.getLogger(__name__)


class AuthService:

    def registrar(self, db: Session, nome: str, email: str, senha: str):
        logger.info(f"Tentativa de registro para email: {email}")
        
        try:
            existe = db.query(User).filter(User.email == email).first()
            if existe:
                logger.warning(f"Tentativa de registro com email já cadastrado: {email}")
                raise HTTPException(status_code=400, detail="Email já cadastrado.")

            # Hash da senha usando bcrypt diretamente
            senha_bytes = senha.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')
            
            user = User(nome=nome, email=email, senha=hashed)

            db.add(user)
            db.commit()
            db.refresh(user)

            # Criar cliente automaticamente associado ao usuário
            # Verificar se cliente já existe (pode ter sido criado anteriormente)
            cliente_existente = db.query(Cliente).filter(Cliente.email == email).first()
            if cliente_existente:
                logger.info(f"Cliente já existe para email: {email} (Cliente ID: {cliente_existente.id})")
            else:
                try:
                    cliente = Cliente(
                        nome=nome,
                        email=email,
                        telefone=None,
                        ativo=True
                    )
                    db.add(cliente)
                    db.commit()
                    db.refresh(cliente)
                    logger.info(f"Cliente criado automaticamente para usuário: {email} (Cliente ID: {cliente.id})")
                except Exception as e:
                    # Se falhar ao criar cliente, loga mas não impede o registro do usuário
                    logger.error(f"Erro ao criar cliente automaticamente para {email}: {e}", exc_info=True)
                    db.rollback()
                    # Não faz rollback do usuário, apenas loga o erro

            logger.info(f"Usuário registrado com sucesso: {email} (ID: {user.id})")
            return {"message": "Usuário criado com sucesso."}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao registrar usuário {email}: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro ao criar usuário.")

    def login(self, db: Session, email: str, senha: str):
        logger.info(f"Tentativa de login para email: {email}")
        
        try:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                logger.warning(f"Tentativa de login com email não encontrado: {email}")
                raise HTTPException(status_code=401, detail="Credenciais inválidas.")
            
            # Verificar senha usando bcrypt diretamente
            senha_bytes = senha.encode('utf-8')
            senha_hash_bytes = user.senha.encode('utf-8')
            
            if not bcrypt.checkpw(senha_bytes, senha_hash_bytes):
                logger.warning(f"Tentativa de login com senha incorreta para email: {email}")
                raise HTTPException(status_code=401, detail="Credenciais inválidas.")

            token = criar_token({"id": user.id, "email": user.email})
            logger.info(f"Login bem-sucedido para email: {email} (ID: {user.id})")
            return {"access_token": token, "token_type": "bearer"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer login para {email}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Erro ao processar login.")

    def alterar_senha(self, db: Session, user_id: int, senha_atual: str, nova_senha: str):
        """Altera a senha do usuário"""
        logger.info(f"Tentativa de alteração de senha para usuário ID: {user_id}")
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"Usuário não encontrado para alteração de senha: ID {user_id}")
                raise HTTPException(status_code=404, detail="Usuário não encontrado.")
            
            # Verificar senha atual
            senha_atual_bytes = senha_atual.encode('utf-8')
            senha_hash_bytes = user.senha.encode('utf-8')
            
            if not bcrypt.checkpw(senha_atual_bytes, senha_hash_bytes):
                logger.warning(f"Senha atual incorreta para alteração de senha: ID {user_id}")
                raise HTTPException(status_code=401, detail="Senha atual incorreta.")
            
            # Validar nova senha
            if len(nova_senha) < 6:
                raise HTTPException(status_code=400, detail="A nova senha deve ter pelo menos 6 caracteres.")
            
            # Hash da nova senha
            nova_senha_bytes = nova_senha.encode('utf-8')
            salt = bcrypt.gensalt()
            nova_senha_hash = bcrypt.hashpw(nova_senha_bytes, salt).decode('utf-8')
            
            # Atualizar senha
            user.senha = nova_senha_hash
            db.commit()
            db.refresh(user)
            
            logger.info(f"Senha alterada com sucesso para usuário ID: {user_id}")
            return {"message": "Senha alterada com sucesso."}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao alterar senha para usuário ID {user_id}: {e}", exc_info=True)
            db.rollback()
            raise HTTPException(status_code=500, detail="Erro ao alterar senha.")
