from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.data.depedencies import get_db, get_current_user
from app.services.auth_service import AuthService
from app.schemas import LoginSchema, RegisterSchema, TokenResponse, ChangePasswordSchema

router = APIRouter(prefix="/auth", tags=["Autenticação"])
service = AuthService()


@router.post("/register", response_model=dict, summary="Registrar novo usuário")
def register(credentials: RegisterSchema, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    
    - **nome**: Nome completo do usuário (mínimo 3 caracteres)
    - **email**: Email válido do usuário
    - **senha**: Senha (mínimo 6 caracteres, deve conter pelo menos um número)
    """
    return service.registrar(db, credentials.nome, credentials.email, credentials.senha)


@router.post("/login", response_model=TokenResponse, summary="Fazer login")
def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.
    
    - **email**: Email do usuário
    - **senha**: Senha do usuário
    
    Retorna um token de acesso válido por 60 minutos.
    """
    return service.login(db, credentials.email, credentials.senha)


@router.post("/change-password", response_model=dict, summary="Alterar senha")
def change_password(
    credentials: ChangePasswordSchema,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Altera a senha do usuário logado.
    
    - **senha_atual**: Senha atual do usuário
    - **nova_senha**: Nova senha (mínimo 6 caracteres, deve conter pelo menos um número)
    
    Requer autenticação.
    """
    return service.alterar_senha(db, user["id"], credentials.senha_atual, credentials.nova_senha)
