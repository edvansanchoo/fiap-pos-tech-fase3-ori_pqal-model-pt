# pip install -U langchain langchain-ollama

from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="ori-pqal-pt",
    temperature=0
)

response = llm.invoke(
    """
    Pergunta: Terapia de falta de ar controlada pelo paciente em cuidados paliativos: um novo conceito terapêutico para administração de opióides?
    Contexto:\nA falta de ar é um dos sintomas mais angustiantes experimentados por pacientes com câncer avançado e diagnósticos não oncológicos. Muitas vezes, a gravidade da falta de ar aumenta rapidamente, exigindo um rápido controle dos sintomas. Foram descritas as vias oral, bucal e parenteral de administração de medicamentos controlada pelo fornecedor. Não está claro se os sistemas de terapia controlada pelo paciente (PCT) seriam uma opção de tratamento adicional.\n\nInvestigar se a PCT com opioides intravenosos pode ser um método terapêutico eficaz para reduzir a falta de ar em pacientes com doença avançada. Os objetivos secundários foram estudar a viabilidade e aceitação da PCT com opioides em pacientes com falta de ar refratária.\n\nEste foi um estudo piloto observacional com 18 pacientes internados com doença avançada e falta de ar refratária recebendo PCT com opióides. A falta de ar foi medida em uma escala de avaliação numérica autorreferida. Os escores da Escala de Agitação e Sedação de Richmond, os escores da Escala de Desempenho Paliativo, os sinais vitais e um questionário de satisfação do paciente autodesenvolvido foram usados ​​para medir os desfechos secundários. Foram realizadas análises descritivas e de interferência (teste de Friedman) e análises post hoc (testes de Wilcoxon e correções de Bonferroni).\n\nDezoito dos 815 pacientes (câncer avançado; idade mediana = 57,5 anos [intervalo 36-81]; 77,8% mulheres) receberam controle dos sintomas de falta de ar com PCT com opióides; a dose diária equivalente de morfina no Dia 1 foi mediana = 20,3 mg (5,0-49,6 mg); Dia 2: 13,0 mg (1,0-78,5 mg); Dia 3: 16,0 mg (8,3-47,0 mg). A escala de avaliação numérica da falta de ar atual diminuiu (linha de base: mediana = 5 [intervalo 1-10]; Dia 1: mediana = 4 [intervalo 0-8], P < 0,01; Dia 2: mediana = 4 [intervalo 0-5], P < 0,01). Os parâmetros fisiológicos permaneceram estáveis ​​ao longo do tempo. No dia 3, 12/12 pacientes confirmaram que este modo de aplicação proporcionou alívio da falta de ar.
    """
)

print(response.content)