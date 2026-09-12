from collections.abc import Callable

from langchain_core.callbacks import BaseCallbackHandler


class ToolProgressHandler(BaseCallbackHandler):
    """Reporta início/fim de cada tool para atualizar a UI em tempo real."""

    def __init__(self, on_progress: Callable[[str, str, object | None], None]) -> None:
        self.on_progress = on_progress
        self._tool_atual: str | None = None

    def on_tool_start(
        self,
        serialized: dict,
        input_str: str,
        *,
        inputs: dict | None = None,
        **kwargs: object,
    ) -> None:
        nome = serialized.get("name", "tool")
        self._tool_atual = nome
        entrada = inputs if inputs is not None else input_str
        self.on_progress("start", nome, entrada)

    def on_tool_end(self, output: str, **kwargs: object) -> None:
        nome = self._tool_atual or "tool"
        self.on_progress("end", nome, output)
