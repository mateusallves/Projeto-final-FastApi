import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.data.database import Base, engine
from app.config import settings
from app.controllers import (
    auth_controller,
    categoria_controller,
    contato_controller,
    produto_controller,
    kit_controller,
    evento_controller,
    cliente_controller,
    pedido_controller,
    pagamento_controller,
)

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API Doceria",
    description="API para sistema de doceria Doce Encanto",
    version="1.0.0"
)

# Configurar CORS com origens específicas
# Em desenvolvimento, permite todas as origens (incluindo file://)
cors_origins = ["*"] if settings.ENVIRONMENT == "development" else settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

logger.info(f"Aplicacao iniciada em modo {settings.ENVIRONMENT}")
logger.info(f"CORS configurado para origens: {settings.CORS_ORIGINS}")

Base.metadata.create_all(bind=engine)

# Rotas públicas
app.include_router(auth_controller.router)
app.include_router(categoria_controller.router)
app.include_router(contato_controller.router)

# Rotas de produtos e catálogo
app.include_router(produto_controller.router)
app.include_router(kit_controller.router)
app.include_router(evento_controller.router)

# Rotas de clientes
app.include_router(cliente_controller.router)

# Rotas de pedidos
app.include_router(pedido_controller.router)

# Rotas de pagamentos
app.include_router(pagamento_controller.router)
