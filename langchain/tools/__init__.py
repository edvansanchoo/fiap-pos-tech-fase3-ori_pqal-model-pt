from tools.paciente import buscar_paciente
from tools.exames import buscar_exames
from tools.medicamentos import buscar_medicamentos
from tools.prontuario import buscar_prontuario
from tools.analise import analisar_paciente

ALL_TOOLS = [
    buscar_paciente,
    buscar_exames,
    buscar_medicamentos,
    buscar_prontuario,
    analisar_paciente,
]
