"""
Configurações da aplicação com validação de variáveis de ambiente
"""
import os
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Banco de dados
    DATABASE_URL: str = "sqlite:///./doceria.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Ambiente
    ENVIRONMENT: str = "development"  # development, production, testing
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global de configurações
settings = Settings()

# Validação adicional
if settings.ENVIRONMENT == "production":
    if settings.SECRET_KEY == "fallback_secret_key_change_in_production":
        raise ValueError(
            "SECRET_KEY deve ser definida em produção! "
            "Configure a variável de ambiente SECRET_KEY."
        )
    if "*" in settings.CORS_ORIGINS:
        raise ValueError(
            "CORS_ORIGINS não pode conter '*' em produção! "
            "Especifique as origens permitidas."
        )

