"""
Aplicação FastAPI principal do SNH.

Monta todos os routers, configura CORS e middleware de tratamento de erros.
Execute com:
    uvicorn src.snh_project.api.app:app --reload --port 8000

Acesse a documentação interativa em:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import auth, patients, prescriptions, reports, notifications, users

# =============================================================================
# INSTÂNCIA PRINCIPAL
# =============================================================================

app = FastAPI(
    title="SNH — Sistema Nutricional Hospitalar",
    description=(
        "API REST para gestão de prescrições dietéticas hospitalares.\n\n"
        "**Autenticação:** use `POST /auth/login` para obter um Bearer token "
        "e clique em **Authorize** no topo da página para autenticar."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# =============================================================================
# CORS — permite requisições do frontend (localhost:3000)
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js dev
        "http://localhost:5173",   # Vite dev (alternativo)
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# TRATAMENTO GLOBAL DE ERROS
# =============================================================================

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Captura erros não tratados e retorna JSON estruturado."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor.",
            "tipo": type(exc).__name__,
        },
    )

# =============================================================================
# ROUTERS
# =============================================================================

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(prescriptions.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(users.router)

# =============================================================================
# ENDPOINTS UTILITÁRIOS
# =============================================================================

@app.get("/", tags=["Status"], summary="Health check")
def root() -> dict:
    """Verifica se a API está no ar."""
    return {
        "status": "online",
        "sistema": "SNH — Sistema Nutricional Hospitalar",
        "versao": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Status"], summary="Health check detalhado")
def health() -> dict:
    """Retorna status detalhado da API."""
    import os
    from pathlib import Path
    data_dir = os.getenv("SNH_DATA_DIR", "data")
    arquivos = {
        f: Path(f"{data_dir}/{f}").exists()
        for f in ["patients.json", "prescriptions.json", "users.json", "setores.json", "notifications.json"]
    }
    return {
        "status": "healthy",
        "data_dir": data_dir,
        "arquivos_json": arquivos,
    }
