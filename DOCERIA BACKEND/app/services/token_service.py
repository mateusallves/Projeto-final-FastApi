from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings


def criar_token(dados: dict):
    """
    Gera um JWT com expiração.
    """
    dados_copia = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_copia.update({"exp": expiracao})

    token_jwt = jwt.encode(dados_copia, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token_jwt


def verificar_token(token: str):
    """
    Valida um JWT e retorna o payload se estiver válido.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
