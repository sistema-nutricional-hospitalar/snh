"""Router de Notificações — leitura e marcação (US07, US09)."""

from typing import List, Optional
import os
import re

from fastapi import APIRouter, HTTPException, status

from ..dependencies import CurrentUser, CopOuNutriUser
from ...infrastructure.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notificações"])


def _normalizar(r: dict) -> dict:
    """Normaliza um registro do backend para o formato esperado pelo frontend."""
    mensagem = r.get("mensagem", "")

    # Deriva titulo da primeira linha da mensagem
    titulo = mensagem.split("\n")[0].replace("[SNH] ", "").strip() or "Notificação"
    titulo = re.sub(r'Prescrição\s*#[a-f0-9\-]+\s*-\s*', '', titulo).strip()

    # Extrai informações estruturadas
    paciente_nome = None
    setor_nome = None
    prescricao_id = None
    
    match_paciente = re.search(r'Paciente:\s*([^|]+)', mensagem)
    if match_paciente:
        paciente_nome = match_paciente.group(1).strip()
    
    match_setor = re.search(r'Setor:\s*([^\n]+)', mensagem)
    if match_setor:
        setor_nome = match_setor.group(1).strip()
    
    match_prescricao = re.search(r'#([a-f0-9\-]{36})', mensagem)
    if match_prescricao:
        prescricao_id = match_prescricao.group(1)
    
    # Limpa mensagem
    mensagem_limpa = mensagem
    mensagem_limpa = re.sub(r'Paciente:.*\|.*Setor:.*\n', '', mensagem_limpa)
    mensagem_limpa = re.sub(r'\[SNH\]\s*Prescrição\s*#[a-f0-9\-]+\s*-\s*', '', mensagem_limpa)
    mensagem_limpa = re.sub(r'DietaOral', 'Oral', mensagem_limpa)
    mensagem_limpa = re.sub(r'DietaEnteral', 'Enteral', mensagem_limpa)
    mensagem_limpa = re.sub(r'DietaParenteral', 'Parenteral', mensagem_limpa)
    mensagem_limpa = re.sub(r'DietaMista', 'Mista', mensagem_limpa)
    mensagem_limpa = mensagem_limpa.strip()

    # Deriva tipo a partir do conteúdo da mensagem
    msg_lower = mensagem.lower()
    if "nova prescrição" in msg_lower or "prescrição criada" in msg_lower:
        tipo = "novo_paciente"
    elif "alteração de dieta" in msg_lower or "alterada" in msg_lower:
        tipo = "alteracao_dieta"
    elif "encerramento" in msg_lower or "encerrada" in msg_lower:
        tipo = "sistema"
    else:
        tipo = "sistema"

    # Normaliza prioridade
    prioridade_raw = r.get("prioridade", "normal")
    mapa_prioridade = {"normal": "media", "baixa": "baixa", "media": "media", "alta": "alta", "urgente": "urgente"}
    prioridade = mapa_prioridade.get(prioridade_raw, "media")

    return {
        "id":            r.get("id", ""),
        "titulo":        titulo,
        "mensagem":      mensagem_limpa,
        "tipo":          tipo,
        "prioridade":    prioridade,
        "paciente_nome": paciente_nome,
        "setor_nome":    setor_nome,
        "prescricao_id": prescricao_id,
        "setor_id":      r.get("setor_id") or r.get("patient_id"),
        "paciente_id":   r.get("patient_id"),
        "destinatario":  r.get("destinatario"),
        "lida":          r.get("lida", False),
        "criada_em":     r.get("criado_em", r.get("criada_em", "")),
    }

DATA_DIR = os.getenv("SNH_DATA_DIR", "data")


def _get_repo() -> NotificationRepository:
    return NotificationRepository(f"{DATA_DIR}/notifications.json")


@router.get(
    "",
    summary="Listar notificações do usuário (US07)",
)
def listar_notificacoes(
    usuario: CopOuNutriUser,
    apenas_nao_lidas: bool = True,
) -> List[dict]:
    """Retorna notificações do usuário autenticado.

    **US07:** copeiro visualiza notificações de alterações de dieta.
    **Requer:** copeiro, nutricionista ou administrador.
    """
    repo = _get_repo()
    destinatario = usuario.get("email", usuario.get("user_id", ""))

    if apenas_nao_lidas:
        registros = repo.listar_nao_lidas(destinatario)
    else:
        registros = repo.listar_por_destinatario(destinatario)
    return [_normalizar(r) for r in registros]


@router.get(
    "/count",
    summary="Contagem de notificações não lidas",
)
def contar_nao_lidas(usuario: CopOuNutriUser) -> dict:
    """Retorna o número de notificações não lidas.

    Útil para o badge de notificações no frontend.
    """
    repo = _get_repo()
    destinatario = usuario.get("email", usuario.get("user_id", ""))
    return {"nao_lidas": repo.contar_nao_lidas(destinatario)}


@router.patch(
    "/{notif_id}/read",
    summary="Marcar notificação como lida",
    status_code=status.HTTP_200_OK,
)
def marcar_lida(
    notif_id: str,
    usuario: CopOuNutriUser,
) -> dict:
    """Marca uma notificação específica como lida."""
    repo = _get_repo()
    ok = repo.marcar_lida(notif_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notificação não encontrada.")
    return {"sucesso": True, "id": notif_id}


@router.patch(
    "/read-all",
    summary="Marcar todas as notificações como lidas",
    status_code=status.HTTP_200_OK,
)
def marcar_todas_lidas(usuario: CopOuNutriUser) -> dict:
    """Marca todas as notificações não lidas do usuário como lidas."""
    repo = _get_repo()
    destinatario = usuario.get("email", usuario.get("user_id", ""))
    quantidade = repo.marcar_todas_lidas(destinatario)
    return {"sucesso": True, "marcadas": quantidade}