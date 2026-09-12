from tools.sistema import listar_pacientes_disponiveis, mostrar_ajuda
from tools.paciente import buscar_paciente
from tools.exames import buscar_exames
from tools.medicamentos import buscar_medicamentos
from tools.prontuario import buscar_prontuario
from tools.analise import montar_contexto_paciente
from tools.pqal import preparar_contexto_pqal
from tools.escrita import (
    atualizar_paciente,
    criar_paciente,
    registrar_exame,
    registrar_medicamento,
)

ALL_TOOLS = [
    listar_pacientes_disponiveis,
    mostrar_ajuda,
    buscar_paciente,
    criar_paciente,
    atualizar_paciente,
    buscar_exames,
    registrar_exame,
    buscar_medicamentos,
    registrar_medicamento,
    buscar_prontuario,
    montar_contexto_paciente,
    preparar_contexto_pqal,
]
