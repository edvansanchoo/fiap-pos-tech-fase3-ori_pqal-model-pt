from pydantic import BaseModel, Field, model_validator


_CHAVES_PACIENTE = (
    "paciente_id",
    "id_paciente",
    "nome_ou_id",
    "id",
    "patient_id",
    "paciente",
    "nome",
    "name",
    "input",
    "query",
    "value",
)


def _valor_paciente(data: object) -> str | None:
    if isinstance(data, str):
        return data.strip()
    if isinstance(data, int):
        return str(data)
    if isinstance(data, dict):
        for key in _CHAVES_PACIENTE:
            value = data.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
        if len(data) == 1:
            value = next(iter(data.values()))
            if value is not None and str(value).strip():
                return str(value).strip()
    return None


class PacienteIdInput(BaseModel):
    paciente_id: str = Field(description="ID numérico do paciente")

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data: object) -> object:
        valor = _valor_paciente(data)
        if valor is not None:
            return {"paciente_id": valor}
        return data


class BuscarPacienteInput(BaseModel):
    nome_ou_id: str = Field(description="Nome parcial ou ID numérico do paciente")

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data: object) -> object:
        valor = _valor_paciente(data)
        if valor is not None:
            return {"nome_ou_id": valor}
        return data


class BuscarExamesInput(PacienteIdInput):
    limite: str = Field(default="", description="Quantidade máxima de exames")


class BuscarProntuarioInput(PacienteIdInput):
    limite: str = Field(default="", description="Quantidade máxima de entradas")


class CriarPacienteInput(BaseModel):
    nome: str = Field(description="Nome completo do paciente")
    data_nascimento: str = Field(description="Data de nascimento (YYYY-MM-DD ou DD/MM/YYYY)")


class AtualizarPacienteInput(BaseModel):
    paciente_id: str = Field(description="ID numérico do paciente")
    nome: str = Field(default="", description="Novo nome (opcional)")
    data_nascimento: str = Field(default="", description="Nova data de nascimento (opcional)")

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data: object) -> object:
        if isinstance(data, dict):
            pid = _valor_paciente(data)
            if pid is not None:
                data = dict(data)
                data["paciente_id"] = pid
        return data


class RegistrarExameInput(BaseModel):
    paciente_id: str = Field(description="ID numérico do paciente")
    tipo: str = Field(description="Tipo do exame, ex: Glicemia")
    resultado: str = Field(description="Resultado do exame")
    data: str = Field(default="", description="Data do exame (opcional, padrão hoje)")

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data: object) -> object:
        if isinstance(data, dict):
            pid = _valor_paciente(data)
            if pid is not None:
                data = dict(data)
                data["paciente_id"] = pid
        return data


class RegistrarMedicamentoInput(BaseModel):
    paciente_id: str = Field(description="ID numérico do paciente")
    medicamento: str = Field(description="Nome do medicamento")
    dose: str = Field(description="Dose, ex: 10mg")
    data_inicio: str = Field(default="", description="Data de início (opcional, padrão hoje)")

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data: object) -> object:
        if isinstance(data, dict):
            pid = _valor_paciente(data)
            if pid is not None:
                data = dict(data)
                data["paciente_id"] = pid
        return data


class TextoInput(BaseModel):
    texto: str = Field(description="Texto completo da pergunta do usuário")

    @model_validator(mode="before")
    @classmethod
    def normalizar(cls, data: object) -> object:
        if isinstance(data, str):
            return {"texto": data.strip()}
        if isinstance(data, dict):
            for key in ("texto", "input", "pergunta", "query"):
                value = data.get(key)
                if value is not None and str(value).strip():
                    return {"texto": str(value).strip()}
        return data
