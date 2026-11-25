"""Configuração do módulo lida de variáveis de ambiente e do arquivo .env."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv


class ErroConfiguracao(RuntimeError):
    pass


@dataclass(frozen=True)
class Configuracao:
    modelo_llm: str
    banco_sqlite: Path
    porta: int
    telemetria: bool
    timeout_sandbox: int


def carregar_configuracao() -> Configuracao:
    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path)

    modelo = os.getenv("MODELO_LLM", "").strip()
    if not modelo:
        raise ErroConfiguracao(
            "Defina MODELO_LLM no formato provedor:modelo, por exemplo ollama:llama3.2 "
            "ou anthropic:claude-sonnet-4-5 (veja .env.exemplo)."
        )

    banco = Path(os.getenv("BANCO_SQLITE", "dados/tutor_estudos.db"))
    banco.parent.mkdir(parents=True, exist_ok=True)

    telemetria = os.getenv("AGNO_TELEMETRY", "false").lower() == "true"
    os.environ["AGNO_TELEMETRY"] = "true" if telemetria else "false"

    return Configuracao(
        modelo_llm=modelo,
        banco_sqlite=banco,
        porta=int(os.getenv("PORTA", "7777")),
        telemetria=telemetria,
        timeout_sandbox=int(os.getenv("TIMEOUT_SANDBOX", "5")),
    )
