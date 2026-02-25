import pytest
from datetime import datetime
from src.snh_project.core.setorclin import SetorClinico
from src.snh_project.core.patient import Paciente


class TestSetorClinico:
    """Testes para a classe SetorClinico."""

    def test_criar_setor_clinico(self):
        """Valida criação de um SetorClinico."""
        setor = SetorClinico("UTI")
        assert setor.nome == "UTI"  # ✅ Usa property
        assert setor.quantidade_pacientes == 0  # ✅ Usa property
        assert setor.esta_vazio == True  # ✅ Usa property

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
        # O paciente deve estar registrado no setor
        assert setor.quantidade_pacientes == 1
        assert setor.obter_paciente(1) == paciente  # ✅ Usa método público
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
    
    def test_property_lista_pacientes_retorna_copia(self):
        """Valida que lista_pacientes retorna cópia (encapsulamento)."""
        setor = SetorClinico("UTI")
        paciente = Paciente(
            nome="Teste",
            dataNasc="1990-01-01",
            setorClinico=setor,
            leito=5,
            datain=datetime.now(),
            risco=False
        )
        
        # Obter lista
        lista = setor.lista_pacientes
        
        # Modificar a cópia não deve afetar o original
        lista[999] = "intruso"
        
        assert 999 not in setor  # ✅ Usa __contains__
        assert setor.quantidade_pacientes == 1
    
    def test_leitos_ocupados(self):
        """Valida property leitos_ocupados."""
        setor = SetorClinico("Clínica Geral")
        
        Paciente("P1", "1990-01-01", setor, 3, datetime.now(), False)
        Paciente("P2", "1990-01-01", setor, 1, datetime.now(), False)
        Paciente("P3", "1990-01-01", setor, 5, datetime.now(), False)
        
        assert setor.leitos_ocupados == [1, 3, 5]  # Ordenado
    
    def test_buscar_paciente_por_nome(self):
        """Valida busca de paciente por nome."""
        setor = SetorClinico("UTI")
        paciente = Paciente(
            "João Silva",
            "1990-01-01",
            setor,
            10,
            datetime.now(),
            False
        )
        
        encontrado = setor.buscar_paciente_por_nome("João")
        assert encontrado == paciente
        
        nao_encontrado = setor.buscar_paciente_por_nome("Maria")
        assert nao_encontrado is None


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
        assert paciente.setorClinico == setor  # ✅ OBJETO, não string
        assert isinstance(paciente.setorClinico, SetorClinico)  # ✅ Valida tipo
        assert paciente.setor_nome == "Clínica Geral"  # ✅ Usa property conveniente
        assert paciente.leito == 1
        assert paciente.risco is False

    def test_criar_paciente_sem_setor_valido(self):
        """Valida que Paciente rejeita string ao invés de SetorClinico."""
        with pytest.raises(TypeError, match="deve ser uma instância de SetorClinico"):
            paciente = Paciente(
                nome="João Silva",
                dataNasc="1990-01-15",
                setorClinico="Clínica Geral",  # ❌ String
                leito=1,
                datain=datetime.now(),
                risco=False
            )

    def test_risco_uti_automatico(self):
        """Valida que setor UTI força risco=True automaticamente."""
        setor_uti = SetorClinico("UTI")
        paciente = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor_uti,
            leito=1,
            datain=datetime.now(),
            risco=False  # ✅ Passa False mas será True
        )
        assert paciente.risco is True

    def test_risco_nao_uti(self):
        """Valida que setorClinico != 'UTI' respeita o valor de risco."""
        setor = SetorClinico("Clínica Geral")
        
        paciente_com_risco = Paciente(
            nome="João Silva",
            dataNasc="1990-01-15",
            setorClinico=setor,
            leito=1,
            datain=datetime.now(),
            risco=True
        )
        assert paciente_com_risco.risco is True

        paciente_sem_risco = Paciente(
            nome="Maria Santos",
            dataNasc="1985-05-20",
            setorClinico=setor,
            leito=2,
            datain=datetime.now(),
            risco=False
        )
        assert paciente_sem_risco.risco is False

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
        
        # Modificar nome
        paciente.nome = "João Silva Atualizado"
        assert paciente.nome == "João Silva Atualizado"
        
        # Modificar data de internação
        novo_datain = datetime(2026, 2, 10, 10, 0, 0)
        paciente.datain = novo_datain
        assert paciente.datain == novo_datain

    def test_multiplos_pacientes_leitos_diferentes(self):
        """Valida adição de múltiplos pacientes em leitos diferentes."""
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
        assert setor.quantidade_pacientes == 2
        assert setor.obter_paciente(1).nome == "João Silva"
        assert setor.obter_paciente(2).nome == "Maria Santos"
    
    def test_transferir_paciente_entre_setores(self):
        """Valida transferência de paciente entre setores."""
        uti = SetorClinico("UTI")
        enfermaria = SetorClinico("Enfermaria")
        
        paciente = Paciente(
            nome="Carlos Souza",
            dataNasc="1975-08-10",
            setorClinico=uti,
            leito=3,
            datain=datetime.now(),
            risco=False
        )
        
        # Antes da transferência
        assert uti.quantidade_pacientes == 1
        assert enfermaria.quantidade_pacientes == 0
        assert paciente.risco == True  # UTI
        assert paciente.setorClinico == uti
        
        # Transferir
        paciente.transferir_para_setor(enfermaria, 15)
        
        # Depois da transferência
        assert uti.quantidade_pacientes == 0  # ✅ Removido da UTI
        assert enfermaria.quantidade_pacientes == 1  # ✅ Adicionado na enfermaria
        assert paciente.setorClinico == enfermaria  # ✅ OBJETO atualizado
        assert paciente.setor_nome == "Enfermaria"
        assert paciente.leito == 15
        assert paciente.risco == False  # ✅ Risco recalculado
    
    def test_tempo_internacao(self):
        """Valida cálculo de tempo de internação."""
        setor = SetorClinico("UTI")
        data_antiga = datetime(2026, 1, 1)
        
        paciente = Paciente(
            nome="Teste",
            dataNasc="1990-01-01",
            setorClinico=setor,
            leito=5,
            datain=data_antiga,
            risco=False
        )
        
        dias = paciente.obter_tempo_internacao()
        assert dias > 0  # Pelo menos 1 dia
    
    def test_repr_str(self):
        """Valida métodos __repr__ e __str__."""
        setor = SetorClinico("UTI")
        paciente = Paciente(
            "João",
            "1990-01-01",
            setor,
            10,
            datetime.now(),
            False
        )
        
        repr_str = repr(paciente)
        assert "Paciente" in repr_str
        assert "João" in repr_str
        
        str_str = str(paciente)
        assert "João" in str_str
        assert "UTI" in str_str