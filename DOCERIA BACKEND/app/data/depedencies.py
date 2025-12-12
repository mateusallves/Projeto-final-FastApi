from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.data.database import SessionLocal
from app.services.token_service import verificar_token

# Trocar OAuth2PasswordBearer por HTTPBearer:
bearer_scheme = HTTPBearer(auto_error=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Valida o JWT enviado em Authorization: Bearer <token>
    """
    token = credentials.credentials  # pega só o token, sem o "Bearer"

    payload = verificar_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
