"""
Serializadores: convertem objetos de domínio ↔ dicionários JSON.

Cada função é pura (sem efeitos colaterais) e responsável por um único tipo.
Princípio SRP: cada função serializa/desserializa apenas uma entidade.

IMPORTANTE sobre reconstrução:
- Paciente: requer objeto SetorClinico já instanciado (passa setor como argumento)
- Prescricao: requer Paciente, Dieta e NotificadorService já instanciados
- DietaEnteral: requer setor_clinico (SetorClinico) para ser criada via factory
"""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.base import Dieta
from ..core.diets import DietaEnteral, DietaMista, DietaOral, DietaParenteral, ItemCardapio
from ..core.patient import Paciente
from ..core.prescription import HistoricoAlteracao, Prescricao
from ..core.setorclin import SetorClinico
from ..core.user import (
    Administrador,
    Copeiro,
    Enfermeiro,
    Medico,
    Nutricionista,
    StatusUsuario,
    TipoUsuario,
    Usuario,
)
from ..services.factory import DietaFactory
from ..services.notifier import NotificadorService


# =============================================================================
# UTILITÁRIOS DE DATA
# =============================================================================

def _parse_datetime(valor: str) -> datetime:
    """Converte string para datetime com mensagem de erro clara.

    Aceita DD/MM/YYYY, DD.MM.YYYY e ISO YYYY-MM-DD[THH:MM:SS].

    Raises:
        ValueError: Se o formato for irreconhecível.
    """
    v = valor.strip()
    partes = v.split("T", 1)
    data_str = partes[0]
    hora_str = partes[1] if len(partes) > 1 else None

    for sep in ("/", "."):
        if sep in data_str:
            segmentos = data_str.split(sep)
            if len(segmentos) == 3 and len(segmentos[0]) <= 2:
                data_str = f"{segmentos[2]}-{segmentos[1].zfill(2)}-{segmentos[0].zfill(2)}"
            break

    iso = f"{data_str}T{hora_str}" if hora_str else data_str
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        raise ValueError(
            f"Formato de data inválido: '{valor}'. "
            "Use YYYY-MM-DD, DD/MM/YYYY ou DD.MM.YYYY."
        )

def _parse_leito(valor):
    """Converte leito para int se possível, mantém string caso contrário (ex: 'A', 'B')."""
    try:
        return int(valor)
    except (ValueError, TypeError):
        return str(valor).strip() if valor is not None else 1


# =============================================================================
# HASH DE SENHA
# =============================================================================

def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 da senha para armazenamento seguro.

    Args:
        senha: Senha em texto puro.

    Returns:
        Hash hexadecimal da senha.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Verifica se a senha confere com o hash armazenado.

    Args:
        senha: Senha em texto puro fornecida pelo usuário.
        hash_armazenado: Hash SHA-256 previamente salvo.

    Returns:
        True se a senha confere, False caso contrário.
    """
    return hash_senha(senha) == hash_armazenado


# =============================================================================
# SETOR CLÍNICO
# =============================================================================

def setor_to_dict(setor: SetorClinico, id_: str) -> Dict[str, Any]:
    """Serializa um SetorClinico para dicionário.

    Args:
        setor: Objeto SetorClinico a serializar.
        id_: UUID string do registro.

    Returns:
        Dicionário com os dados do setor.
    """
    return {
        "id": id_,
        "nome": setor.nome,
    }


def dict_to_setor(d: Dict[str, Any]) -> SetorClinico:
    """Reconstrói um SetorClinico a partir de dicionário.

    Args:
        d: Dicionário com campo 'nome'.

    Returns:
        Instância de SetorClinico.
    """
    return SetorClinico(nome=d["nome"])


# =============================================================================
# ITEM DE CARDÁPIO
# =============================================================================

def item_to_dict(item: ItemCardapio) -> Dict[str, Any]:
    """Serializa um ItemCardapio para dicionário."""
    return {
        "nome": item.nome,
        "quantidade_gramas": item.quantidade_gramas,
        "restricoes": item.restricoes,
    }


def dict_to_item(d: Dict[str, Any]) -> ItemCardapio:
    """Reconstrói um ItemCardapio a partir de dicionário."""
    return ItemCardapio(
        nome=d["nome"],
        quantidade_gramas=float(d["quantidade_gramas"]),
        restricoes=d.get("restricoes", []),
    )


# =============================================================================
# DIETA
# =============================================================================

def dieta_to_dict(dieta: Dieta) -> Dict[str, Any]:
    """Serializa qualquer subclasse de Dieta para dicionário.

    Armazena o tipo e os parâmetros necessários para recriação via DietaFactory.

    Args:
        dieta: Instância de DietaOral, DietaEnteral, DietaParenteral ou DietaMista.

    Returns:
        Dicionário com 'tipo', 'dados' (params do construtor) e 'itens'.
    """
    itens_serializados = [item_to_dict(i) for i in dieta.itens]
    base = {
        "ativa": dieta.ativo,
        "criado_em": dieta.criado_em.isoformat(),
        "usuario_responsavel": dieta.usuario_responsavel,
        "itens": itens_serializados,
    }

    if isinstance(dieta, DietaOral):
        return {
            **base,
            "tipo": "oral",
            "dados": {
                "textura": dieta.textura,
                "numero_refeicoes": dieta._numero_refeicoes,
                "tipo_refeicao": dieta._tipo_refeicao,
                "descricao": dieta.descricao,
                "usuario_responsavel": dieta.usuario_responsavel,
                # Oral não tem calorias calculáveis pelo modelo — depende do cardápio
                "calorias": None,
            },
        }

    if isinstance(dieta, DietaEnteral):
        # Estimativa: 4 kcal/g é o valor calórico típico de fórmulas enterais
        _gramas_dia = dieta._quantidade_gramas_por_porção * dieta.porcoes_diarias
        _calorias_enteral = round(_gramas_dia * 4)
        return {
            **base,
            "tipo": "enteral",
            "dados": {
                "setor_clinico": "__reconstruct__",  # substituído na reconstrução
                "via_infusao": dieta.via_infusao,
                "velocidade_ml_h": dieta.velocidade_ml_h,
                "quantidade_gramas_por_porção": dieta._quantidade_gramas_por_porção,
                "porcoes_diarias": dieta.porcoes_diarias,
                "tipo_equipo": dieta.tipo_equipo,
                "descricao": dieta.descricao,
                "usuario_responsavel": dieta.usuario_responsavel,
                # Estimativa calórica: gramas totais/dia × 4 kcal/g
                "calorias": _calorias_enteral,
            },
        }

    if isinstance(dieta, DietaParenteral):
        # NPT padrão: ~1 kcal/ml (concentração calórica típica de soluções parenterais)
        _calorias_parenteral = round(dieta.volume_ml_dia * 1.0)
        return {
            **base,
            "tipo": "parenteral",
            "dados": {
                "tipo_acesso": dieta.tipo_acesso,
                "volume_ml_dia": dieta.volume_ml_dia,
                "composicao": dieta.composicao,
                "velocidade_ml_h": dieta.velocidade_ml_h,
                "descricao": dieta.descricao,
                "usuario_responsavel": dieta.usuario_responsavel,
                # Estimativa calórica: volume_ml/dia × 1 kcal/ml (NPT padrão)
                "calorias": _calorias_parenteral,
            },
        }

    if isinstance(dieta, DietaMista):
        componentes_serializados = []
        _calorias_mista = 0
        for comp_dieta, comp_percentual in dieta.componentes:
            comp_dict = dieta_to_dict(comp_dieta)
            componentes_serializados.append({
                "dieta": comp_dict,
                "percentual": comp_percentual,
            })
            # Soma ponderada das calorias de cada componente
            cal_comp = comp_dict.get("dados", {}).get("calorias") or 0
            _calorias_mista += cal_comp * (comp_percentual / 100)
        return {
            **base,
            "tipo": "mista",
            "dados": {
                "componentes_raw": componentes_serializados,
                "descricao": dieta.descricao,
                "usuario_responsavel": dieta.usuario_responsavel,
                "calorias": round(_calorias_mista) if _calorias_mista else None,
            },
        }

    raise ValueError(f"Tipo de dieta desconhecido para serialização: {type(dieta).__name__}")


def dict_to_dieta(d: Dict[str, Any], setor: Optional[SetorClinico] = None) -> Dieta:
    """Reconstrói uma Dieta a partir de dicionário.

    Args:
        d: Dicionário serializado com 'tipo' e 'dados'.
        setor: Objeto SetorClinico (obrigatório para DietaEnteral e DietaMista com enteral).

    Returns:
        Instância da subclasse de Dieta correspondente.
    """
    tipo = d["tipo"]
    dados = dict(d["dados"])  # cópia para não alterar original
    itens_raw = d.get("itens", [])

    # DietaEnteral precisa do setor_clinico como objeto
    if tipo == "enteral":
        if setor is None:
            raise ValueError("DietaEnteral requer objeto SetorClinico para reconstrução.")
        dados["setor_clinico"] = setor

    # DietaMista: reconstrói componentes recursivamente
    if tipo == "mista":
        componentes_reconstruidos = []
        for comp_raw in dados.get("componentes_raw", []):
            dieta_comp = dict_to_dieta(comp_raw["dieta"], setor=setor)
            componentes_reconstruidos.append({
                "dieta": dieta_comp,
                "percentual": comp_raw["percentual"],
            })
        dados = {
            "componentes": componentes_reconstruidos,
            "descricao": dados.get("descricao", "Dieta Mista"),
            "usuario_responsavel": dados.get("usuario_responsavel", "sistema"),
        }

    dieta = DietaFactory.criar_dieta(tipo, dados)

    # Restaura itens do cardápio
    for item_raw in itens_raw:
        dieta.adicionar_item(dict_to_item(item_raw))

    return dieta


# =============================================================================
# HISTÓRICO DE ALTERAÇÃO
# =============================================================================

def historico_to_dict(h: HistoricoAlteracao) -> Dict[str, Any]:
    """Serializa um HistoricoAlteracao para dicionário."""
    return {
        "data_hora": h.data_hora.isoformat(),
        "tipo_alteracao": h.tipo_alteracao,
        "descricao": h.descricao,
        "usuario": h.usuario,
    }


# =============================================================================
# PACIENTE
# =============================================================================

def paciente_to_dict(paciente: Paciente, id_: str, setor_id: str) -> Dict[str, Any]:
    """Serializa um Paciente para dicionário.

    Args:
        paciente: Objeto Paciente a serializar.
        id_: UUID string do registro.
        setor_id: UUID do SetorClinico associado.

    Returns:
        Dicionário com todos os dados do paciente.
    """
    return {
        "id": id_,
        "nome": paciente.nome,
        "data_nasc": str(paciente.dataNasc),
        "setor_id": setor_id,
        "leito": paciente.leito,
        "data_internacao": paciente.datain.isoformat(),
        "risco": paciente.risco,
        "criado_em": paciente.criado_em.isoformat(),
        "atualizado_em": paciente.atualizado_em.isoformat(),
    }


def dict_to_paciente(d: Dict[str, Any], setor: SetorClinico) -> Paciente:
    """Reconstrói um Paciente a partir de dicionário.

    Args:
        d: Dicionário com os dados do paciente.
        setor: Objeto SetorClinico já instanciado.

    Returns:
        Instância de Paciente (auto-registrada no setor).
    """
    return Paciente(
        nome=d["nome"],
        dataNasc=d["data_nasc"],
        setorClinico=setor,
        leito=_parse_leito(d["leito"]),
        datain=_parse_datetime(d["data_internacao"]),
        risco=bool(d["risco"]),
    )


# =============================================================================
# USUÁRIO
# =============================================================================

def usuario_to_dict(usuario: Usuario, id_: str, senha_hash: str) -> Dict[str, Any]:
    """Serializa um Usuario para dicionário.

    Args:
        usuario: Objeto Usuario (qualquer subclasse).
        id_: UUID string do registro.
        senha_hash: Hash SHA-256 da senha.

    Returns:
        Dicionário com dados do usuário e campos extras por tipo.
    """
    base = {
        "id": id_,
        "nome": usuario.nome,
        "cpf": usuario.cpf,
        "email": usuario.email,
        "tipo": usuario.tipo.value,
        "status": usuario.status.value,
        "senha_hash": senha_hash,
        "criado_em": usuario.criado_em.isoformat(),
        "dados_extras": {},
    }

    if isinstance(usuario, Nutricionista):
        base["dados_extras"] = {"crn": usuario.crn}
    elif isinstance(usuario, Medico):
        base["dados_extras"] = {"crm": usuario.crm, "especialidade": usuario.especialidade}
    elif isinstance(usuario, Enfermeiro):
        base["dados_extras"] = {"coren": usuario.coren, "setor": usuario.setor}
    elif isinstance(usuario, Copeiro):
        base["dados_extras"] = {"turno": usuario.turno}

    return base


def dict_to_usuario(d: Dict[str, Any]) -> Usuario:
    """Reconstrói um Usuario a partir de dicionário.

    Args:
        d: Dicionário com dados do usuário.

    Returns:
        Instância da subclasse de Usuario correspondente.
    """
    tipo = d["tipo"]
    extras = d.get("dados_extras", {})

    mapa = {
        "nutricionista": lambda: Nutricionista(
            nome=d["nome"], cpf=d["cpf"], email=d["email"],
            crn=extras.get("crn", "000"),
        ),
        "medico": lambda: Medico(
            nome=d["nome"], cpf=d["cpf"], email=d["email"],
            crm=extras.get("crm", "000"),
            especialidade=extras.get("especialidade", ""),
        ),
        "enfermeiro": lambda: Enfermeiro(
            nome=d["nome"], cpf=d["cpf"], email=d["email"],
            coren=extras.get("coren", "000"),
            setor=extras.get("setor", ""),
        ),
        "copeiro": lambda: Copeiro(
            nome=d["nome"], cpf=d["cpf"], email=d["email"],
            turno=extras.get("turno", "manhã"),
        ),
        "administrador": lambda: Administrador(
            nome=d["nome"], cpf=d["cpf"], email=d["email"],
        ),
    }

    factory_fn = mapa.get(tipo)
    if factory_fn is None:
        raise ValueError(f"Tipo de usuário desconhecido: '{tipo}'")

    usuario = factory_fn()

    # Restaura status se não for ATIVO
    status = d.get("status", "ativo")
    if status == "inativo" and usuario.status.value != "inativo":
        usuario.inativar()
    elif status == "bloqueado" and usuario.status.value != "bloqueado":
        usuario.bloquear()

    return usuario


# =============================================================================
# PRESCRIÇÃO
# =============================================================================

def prescricao_to_dict(
    prescricao: Prescricao,
    id_: str,
    patient_id: str,
    setor_id: str,
) -> Dict[str, Any]:
    """Serializa uma Prescricao para dicionário.

    Args:
        prescricao: Objeto Prescricao a serializar.
        id_: UUID string do registro.
        patient_id: UUID do Paciente associado.
        setor_id: UUID do SetorClinico (necessário para DietaEnteral).

    Returns:
        Dicionário completo da prescrição com histórico.
    """
    return {
        "id": id_,
        "patient_id": patient_id,
        "setor_id": setor_id,
        "dieta": dieta_to_dict(prescricao.dieta),
        "historico": [historico_to_dict(h) for h in prescricao.historico],
        "ativa": prescricao.ativa,
        "criado_em": prescricao.criado_em.isoformat(),
        "atualizado_em": prescricao.atualizado_em.isoformat(),
        "usuario_responsavel": prescricao.usuario_responsavel,
    }