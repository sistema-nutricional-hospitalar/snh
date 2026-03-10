"""
Testes para o módulo de autenticação JWT.

Cobertura: geração de token, verificação válida, token expirado,
           token adulterado, payload preservado.
"""

import time
from datetime import datetime, timedelta, timezone

import pytest
import jwt

from src.snh_project.api.auth import (
    criar_token,
    verificar_token,
    SECRET_KEY,
    ALGORITHM,
)


# =============================================================================
# GERAÇÃO DE TOKEN
# =============================================================================

class TestCriarToken:

    def test_criar_token_retorna_string(self):
        """criar_token deve retornar uma string não vazia."""
        token = criar_token({"user_id": "u-1", "tipo": "nutricionista"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_possui_tres_partes_jwt(self):
        """Token JWT válido deve ter 3 partes separadas por ponto."""
        token = criar_token({"user_id": "u-1"})
        partes = token.split(".")
        assert len(partes) == 3

    def test_payload_preservado_no_token(self):
        """Dados incluídos no payload devem ser recuperáveis após decodificação."""
        token = criar_token({"user_id": "abc-123", "tipo": "copeiro", "nome": "João"})
        payload = verificar_token(token)
        assert payload["user_id"] == "abc-123"
        assert payload["tipo"] == "copeiro"
        assert payload["nome"] == "João"

    def test_token_inclui_campo_exp(self):
        """Token deve incluir campo de expiração 'exp'."""
        token = criar_token({"user_id": "u-1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_token_inclui_campo_iat(self):
        """Token deve incluir campo de emissão 'iat'."""
        token = criar_token({"user_id": "u-1"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "iat" in payload

    def test_dois_tokens_diferentes_para_mesmo_payload(self):
        """Tokens gerados em momentos diferentes devem ser distintos."""
        payload = {"user_id": "u-1"}
        token1 = criar_token(payload)
        time.sleep(0.01)
        token2 = criar_token(payload)
        # iat difere, então tokens são diferentes
        assert token1 != token2


# =============================================================================
# VERIFICAÇÃO DE TOKEN
# =============================================================================

class TestVerificarToken:

    def test_verificar_token_valido_retorna_payload(self):
        """verificar_token com token válido deve retornar o payload."""
        token = criar_token({"user_id": "u-99", "tipo": "administrador"})
        payload = verificar_token(token)
        assert payload is not None
        assert payload["user_id"] == "u-99"

    def test_verificar_token_invalido_retorna_none(self):
        """Token com assinatura inválida deve retornar None."""
        assert verificar_token("token.invalido.aqui") is None

    def test_verificar_token_adulterado_retorna_none(self):
        """Token com payload alterado deve falhar na verificação."""
        token = criar_token({"user_id": "u-1", "tipo": "copeiro"})
        # Adulterar a segunda parte (payload)
        partes = token.split(".")
        partes[1] = partes[1][:-2] + "XX"
        token_adulterado = ".".join(partes)
        assert verificar_token(token_adulterado) is None

    def test_verificar_token_vazio_retorna_none(self):
        """String vazia como token deve retornar None."""
        assert verificar_token("") is None

    def test_verificar_token_expirado_retorna_none(self):
        """Token com expiração no passado deve retornar None."""
        payload_expirado = {
            "user_id": "u-1",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
        }
        token_expirado = jwt.encode(payload_expirado, SECRET_KEY, algorithm=ALGORITHM)
        assert verificar_token(token_expirado) is None

    def test_verificar_token_assinado_com_outra_chave_retorna_none(self):
        """Token assinado com chave diferente da do sistema deve ser rejeitado."""
        token_falso = jwt.encode(
            {"user_id": "hacker", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "chave-errada-do-atacante",
            algorithm=ALGORITHM,
        )
        assert verificar_token(token_falso) is None
