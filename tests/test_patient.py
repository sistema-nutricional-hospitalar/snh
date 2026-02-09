"""
Testes unitários para SetorClinico e Paciente.
Valida o novo comportamento onde Paciente deve ser registrado via SetorClinico.adicionar_paciente.
"""
import pytest
from datetime import datetime
from src.snh_project.core.patient import Paciente, SetorClinico


class TestSetorClinico:
    """Testes para a classe SetorClinico."""

    def test_criar_setor_clinico(self):
        """Valida criação de um SetorClinico."""
        setor = SetorClinico("UTI")
        assert setor.nome == "UTI"
        assert setor.lista_pacientes == {}

    def test_adicionar_paciente_sucesso(self):
        """Valida adição bem-sucedida de um paciente ao setor."""
        setor = SetorClinico("Clínica Geral")
        paciente = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=False
        )
        # O paciente deve estar registrado no setor no leito 1
        assert setor.lista_pacientes[1] == paciente
        assert paciente.nome == "João Silva"

    def test_adicionar_paciente_leito_ocupado(self):
        """Valida que não é possível adicionar dois pacientes no mesmo leito."""
        setor = SetorClinico("Clínica Geral")
        
        # Primeiro paciente no leito 1
        paciente1 = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=False
        )
        
        # Tentativa de adicionar segundo paciente no mesmo leito deve falhar
        with pytest.raises(ValueError, match="Leito 1 já ocupado"):
            paciente2 = Paciente(
                nome="Maria Santos",
                dataNasc="1985-05-20",
                setorClinico=setor,
                leito=1,
                datain=datetime.now(),
                risco=False
            )


class TestPaciente:
    """Testes para a classe Paciente."""

    def test_criar_paciente_com_setor_valido(self):
        """Valida criação de Paciente com um SetorClinico válido."""
        setor = SetorClinico("Clínica Geral")
        paciente = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=False
        )
        assert paciente.nome == "João Silva"
        assert paciente.dataNasc == "1990-01-15"
        assert paciente.setorClinico == "Clínica Geral"
        assert paciente.leito == 1
        assert paciente.risco is False

    def test_criar_paciente_sem_setor_valido(self):
        """Valida que Paciente rejeita string ao invés de SetorClinico."""
        with pytest.raises(TypeError, match="deve ser uma instância de SetorClinico"):
            paciente = Paciente(
                nome="João Silva",
                dataNasc="1990-01-15",
                setorClinico="Clínica Geral",  # ❌ String ao invés de SetorClinico
                leito=1,
                datain=datetime.now(),
                risco=False
            )

    def test_risco_uti_automatico(self):
        """Valida que setorClinico='UTI' força risco=True automaticamente."""
        setor_uti = SetorClinico("UTI")
        paciente = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor_uti,
            leito=1,
            datain=datetime.now(),
            risco=False  # Mesmo passando False, deve retornar True para UTI
        )
        assert paciente.risco is True

    def test_risco_nao_uti(self):
        """Valida que setorClinico != 'UTI' respeita o valor de risco passado."""
        setor = SetorClinico("Clínica Geral")
        paciente = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=True
        )
        assert paciente.risco is True

        # Outro teste com risco=False
        paciente2 = Paciente(
            nome="Maria Santos",
            dataNasc="1985-05-20",
            setorClinico=setor,
            leito=2,
            datain=datetime.now(),
            risco=False
        )
        assert paciente2.risco is False

    def test_propriedades_com_setters(self):
        """Valida que as propriedades aceitam setters."""
        setor = SetorClinico("Clínica Geral")
        paciente = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=False
        )
        
        # Modificar via setter
        paciente.nome = "João Silva Atualizado"
        assert paciente.nome == "João Silva Atualizado"
        
        paciente.dataNasc = "1991-01-15"
        assert paciente.dataNasc == "1991-01-15"
        
        novo_datain = datetime(2026, 2, 10, 10, 0, 0)
        paciente.datain = novo_datain
        assert paciente.datain == novo_datain

    def test_multiplos_pacientes_leitos_diferentes(self):
        """Valida adição de múltiplos pacientes em leitos diferentes do mesmo setor."""
        setor = SetorClinico("Clínica Geral")
        
        paciente1 = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=False
        )
        
        paciente2 = Paciente(
            nome="Maria Santos",
            dataNasc="1985-05-20",
            setorClinico=setor,
            leito=2,
            datain=datetime.now(),
            risco=False
        )
        
        # Ambos devem estar registrados
        assert len(setor.lista_pacientes) == 2
        assert setor.lista_pacientes[1].nome == "João Silva"
        assert setor.lista_pacientes[2].nome == "Maria Santos"
