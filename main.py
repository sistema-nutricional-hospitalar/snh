"""
Ponto de entrada do SNH — Script de demonstração e teste do Dia 1.

Execute com: python main.py
Isso demonstra que a camada de persistência + controllers funcionam
sem necessidade de API ou frontend.
"""

import sys
import os

# Garante que o src está no path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from snh_project.controllers import (
    PatientController,
    PrescriptionController,
    RelatorioController,
    UserController,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def demo():
    """Demonstra o sistema funcionando de ponta a ponta."""
    print("=" * 60)
    print("  SNH — Sistema Nutricional Hospitalar")
    print("  Demo de Persistência + Controllers (Dia 1)")
    print("=" * 60)

    # ----------------------------------------------------------------
    # 1. Autenticação
    # ----------------------------------------------------------------
    print("\n[1] Autenticação")
    user_ctrl = UserController(data_dir=DATA_DIR)

    admin = user_ctrl.autenticar("admin@hospital.com", "admin123")
    nutri = user_ctrl.autenticar("nutricionista@hospital.com", "nutri123")
    falha = user_ctrl.autenticar("admin@hospital.com", "senha_errada")

    print(f"  Admin autenticado: {admin['nome'] if admin else 'FALHOU'}")
    print(f"  Nutricionista autenticada: {nutri['nome'] if nutri else 'FALHOU'}")
    print(f"  Login inválido: {'BLOQUEADO (correto)' if falha is None else 'ERRO'}")

    # ----------------------------------------------------------------
    # 2. Cadastro de paciente
    # ----------------------------------------------------------------
    print("\n[2] Cadastro de Paciente")
    patient_ctrl = PatientController(data_dir=DATA_DIR)

    paciente_dados = {
        "nome": "Maria Silva",
        "data_nasc": "1975-05-20",
        "setor_nome": "Enfermaria Geral",
        "leito": 5,
        "data_internacao": "2024-03-01T08:00:00",
        "risco": False,
    }

    try:
        paciente = patient_ctrl.cadastrar(paciente_dados, usuario_responsavel="nutri001")
        print(f"  Paciente cadastrado: {paciente['nome']} | ID: {paciente['id'][:8]}...")
        patient_id = paciente["id"]
    except ValueError as e:
        print(f"  ERRO: {e}")
        # Usa paciente existente se já houver
        lista = patient_ctrl.listar()
        if lista:
            patient_id = lista[0]["id"]
            print(f"  Usando paciente existente: {lista[0]['nome']}")
        else:
            return

    # ----------------------------------------------------------------
    # 3. Listagem por setor
    # ----------------------------------------------------------------
    print("\n[3] Listagem de Pacientes por Setor")
    pacientes_enf = patient_ctrl.listar(setor_nome="Enfermaria Geral")
    print(f"  Pacientes na Enfermaria Geral: {len(pacientes_enf)}")
    for p in pacientes_enf:
        print(f"    - {p['nome']} | Leito {p['leito']}")

    # ----------------------------------------------------------------
    # 4. Prescrição de dieta
    # ----------------------------------------------------------------
    print("\n[4] Prescrição de Dieta Oral")
    prescription_ctrl = PrescriptionController(data_dir=DATA_DIR)

    try:
        prescricao = prescription_ctrl.prescrever(
            patient_id=patient_id,
            tipo_dieta="oral",
            dados_dieta={
                "textura": "normal",
                "numero_refeicoes": 3,
                "tipo_refeicao": "almoço",
                "descricao": "Dieta hipocalórica",
            },
            usuario_responsavel="Dra. Ana",
        )
        print(f"  Prescrição criada: {prescricao['dieta_tipo']} | ID: {prescricao['id'][:8]}...")
        prescription_id = prescricao["id"]
    except Exception as e:
        print(f"  ERRO ao prescrever: {e}")
        lista_p = prescription_ctrl.listar_por_paciente(patient_id)
        if lista_p:
            prescription_id = lista_p[0]["id"]
        else:
            return

    # ----------------------------------------------------------------
    # 5. Alteração de dieta
    # ----------------------------------------------------------------
    print("\n[5] Alteração de Dieta")
    try:
        alterada = prescription_ctrl.alterar_dieta(
            prescription_id=prescription_id,
            tipo_dieta="oral",
            dados_dieta={
                "textura": "pastosa",
                "numero_refeicoes": 5,
                "tipo_refeicao": "desjejum",
                "descricao": "Alterado para dieta pastosa",
            },
            usuario_responsavel="Dra. Ana",
        )
        print(f"  Dieta alterada. Total alterações: {alterada['total_alteracoes']}")
    except Exception as e:
        print(f"  ERRO ao alterar: {e}")

    # ----------------------------------------------------------------
    # 6. Histórico
    # ----------------------------------------------------------------
    print("\n[6] Histórico de Alterações")
    historico = prescription_ctrl.obter_historico(prescription_id)
    print(f"  {len(historico)} registro(s) no histórico:")
    for h in historico:
        print(f"    [{h['data_hora'][:19]}] {h['tipo_alteracao']} — {h['usuario']}")

    # ----------------------------------------------------------------
    # 7. Relatório
    # ----------------------------------------------------------------
    print("\n[7] Relatório de Dietas")
    relatorio_ctrl = RelatorioController(data_dir=DATA_DIR)
    relatorio = relatorio_ctrl.gerar_relatorio_dietas()
    print(f"  Total de prescrições: {relatorio['total']}")
    print(f"  Por tipo: {relatorio.get('resumo_por_tipo', {})}")

    print("\n" + "=" * 60)
    print("  ✅ Dia 1 completo — persistência + controllers funcionando!")
    print("  Próximo passo: rodar 'python main.py' para ver tudo acima.")
    print("  Para testar via HTTP: aguarde o Dia 2 (FastAPI).")
    print("=" * 60)


if __name__ == "__main__":
    demo()
