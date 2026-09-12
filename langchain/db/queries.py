from datetime import date
from db.connection import get_connection


def _row_to_dict(cursor, row):
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, row))


def calcular_idade(data_nascimento: date) -> int:
    hoje = date.today()
    idade = hoje.year - data_nascimento.year
    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1
    return idade


def buscar_paciente_por_id(paciente_id: int) -> dict | None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, data_nascimento FROM paciente WHERE id = %s",
                (paciente_id,),
            )
            row = cur.fetchone()
            return _row_to_dict(cur, row) if row else None
    finally:
        conn.close()


def buscar_paciente_por_nome(nome: str) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, data_nascimento FROM paciente WHERE nome ILIKE %s ORDER BY id",
                (f"%{nome}%",),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def listar_pacientes() -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome, data_nascimento FROM paciente ORDER BY id")
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_exames(paciente_id: int, limite: int = 5) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, data, tipo, resultado
                FROM exame
                WHERE paciente_id = %s
                ORDER BY data DESC
                LIMIT %s
                """,
                (paciente_id, limite),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_medicamentos_ativos(paciente_id: int) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, medicamento, dose, data_inicio, data_fim
                FROM medicamento
                WHERE paciente_id = %s AND data_fim IS NULL
                ORDER BY data_inicio DESC
                """,
                (paciente_id,),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def buscar_prontuario(paciente_id: int, limite: int = 5) -> list[dict]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, data, descricao
                FROM prontuario
                WHERE paciente_id = %s
                ORDER BY data DESC
                LIMIT %s
                """,
                (paciente_id, limite),
            )
            return [_row_to_dict(cur, row) for row in cur.fetchall()]
    finally:
        conn.close()


def criar_paciente(nome: str, data_nascimento: date) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO paciente (nome, data_nascimento)
                VALUES (%s, %s)
                RETURNING id, nome, data_nascimento
                """,
                (nome.strip(), data_nascimento),
            )
            row = cur.fetchone()
            conn.commit()
            return _row_to_dict(cur, row)
    finally:
        conn.close()


def atualizar_paciente(
    paciente_id: int,
    nome: str | None = None,
    data_nascimento: date | None = None,
) -> dict | None:
    if nome is None and data_nascimento is None:
        return None

    campos = []
    valores = []
    if nome is not None:
        campos.append("nome = %s")
        valores.append(nome.strip())
    if data_nascimento is not None:
        campos.append("data_nascimento = %s")
        valores.append(data_nascimento)

    valores.append(paciente_id)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                UPDATE paciente
                SET {", ".join(campos)}
                WHERE id = %s
                RETURNING id, nome, data_nascimento
                """,
                valores,
            )
            row = cur.fetchone()
            conn.commit()
            return _row_to_dict(cur, row) if row else None
    finally:
        conn.close()


def registrar_exame(
    paciente_id: int,
    tipo: str,
    resultado: str,
    data_exame: date | None = None,
) -> dict:
    data_exame = data_exame or date.today()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO exame (paciente_id, data, tipo, resultado)
                VALUES (%s, %s, %s, %s)
                RETURNING id, paciente_id, data, tipo, resultado
                """,
                (paciente_id, data_exame, tipo.strip(), resultado.strip()),
            )
            row = cur.fetchone()
            conn.commit()
            return _row_to_dict(cur, row)
    finally:
        conn.close()


def registrar_medicamento(
    paciente_id: int,
    medicamento: str,
    dose: str,
    data_inicio: date | None = None,
) -> dict:
    data_inicio = data_inicio or date.today()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO medicamento (paciente_id, medicamento, dose, data_inicio, data_fim)
                VALUES (%s, %s, %s, %s, NULL)
                RETURNING id, paciente_id, medicamento, dose, data_inicio, data_fim
                """,
                (paciente_id, medicamento.strip(), dose.strip(), data_inicio),
            )
            row = cur.fetchone()
            conn.commit()
            return _row_to_dict(cur, row)
    finally:
        conn.close()


def buscar_ultima_consulta(paciente_id: int) -> dict | None:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, paciente_id, data, pressao_sistolica, pressao_diastolica, observacoes
                FROM consulta
                WHERE paciente_id = %s
                ORDER BY data DESC
                LIMIT 1
                """,
                (paciente_id,),
            )
            row = cur.fetchone()
            return _row_to_dict(cur, row) if row else None
    finally:
        conn.close()
