CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE paciente (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    data_nascimento DATE NOT NULL
);

CREATE TABLE prontuario (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data TIMESTAMP NOT NULL,
    descricao TEXT NOT NULL,
    embedding vector(384)
);

CREATE TABLE exame (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data DATE NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    resultado TEXT NOT NULL
);

CREATE TABLE medicamento (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    medicamento VARCHAR(255) NOT NULL,
    dose VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE
);

CREATE TABLE consulta (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES paciente(id),
    data TIMESTAMP NOT NULL,
    pressao_sistolica INTEGER,
    pressao_diastolica INTEGER,
    observacoes TEXT
);

INSERT INTO paciente (nome, data_nascimento) VALUES
    ('João Silva', '1958-03-15'),
    ('Maria Santos', '1972-07-22'),
    ('Pedro Oliveira', '1990-11-08');

INSERT INTO consulta (paciente_id, data, pressao_sistolica, pressao_diastolica, observacoes) VALUES
    (1, '2026-09-10 14:30:00', 145, 90, 'Paciente relata fadiga leve.'),
    (2, '2026-09-05 10:00:00', 120, 80, 'Consulta de rotina.'),
    (3, '2026-08-28 09:15:00', 118, 76, 'Sem queixas.');

INSERT INTO medicamento (paciente_id, medicamento, dose, data_inicio, data_fim) VALUES
    (1, 'Medicamento A', '10mg', '2026-06-01', NULL),
    (1, 'Losartana', '50mg', '2025-01-10', '2026-05-31'),
    (2, 'Metformina', '850mg', '2026-03-01', NULL);

INSERT INTO exame (paciente_id, data, tipo, resultado) VALUES
    (1, '2026-09-08', 'Glicemia', '132 mg/dL'),
    (1, '2026-08-20', 'Glicemia', '95 mg/dL'),
    (1, '2026-09-01', 'Hemograma', 'Hemoglobina: 13.8 g/dL'),
    (2, '2026-09-02', 'Hemoglobina glicada', '6.2%'),
    (3, '2026-08-15', 'Colesterol total', '190 mg/dL');

INSERT INTO prontuario (paciente_id, data, descricao) VALUES
    (1, '2026-09-10 14:45:00', 'Paciente com hipertensão controlada parcialmente. Orientado sobre dieta.'),
    (1, '2026-08-20 11:00:00', 'Retorno ambulatorial. Glicemia dentro da normalidade.'),
    (2, '2026-09-05 10:30:00', 'Diabetes tipo 2 em acompanhamento. Adesão ao tratamento adequada.');
