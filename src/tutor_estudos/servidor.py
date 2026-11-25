"""Servidor AgentOS do Módulo 4, com o Time de agentes e as rotas do contrato."""

from agno.os import AgentOS
from fastapi import FastAPI, HTTPException

from .modelos import EntradaContrato, SaidaContrato, SessaoIniciada
from .servico import ErroFidelidade, ServicoTutor, SessaoInexistente


def criar_agent_os(servico: ServicoTutor, telemetria: bool = False) -> AgentOS:
    base = FastAPI(title="Módulo 4: Tutor de estudos", version="0.2.0")

    @base.post("/contrato/iniciar", response_model=SessaoIniciada, tags=["Contrato"])
    def iniciar(entrada: EntradaContrato) -> SessaoIniciada:
        id_sessao, mensagem = servico.iniciar(entrada.lacunas, entrada.curriculo)
        return SessaoIniciada(id_sessao=id_sessao, mensagem=mensagem)

    @base.get("/contrato/resultado/{id_sessao}", response_model=SaidaContrato, tags=["Contrato"])
    def resultado(id_sessao: str) -> SaidaContrato:
        try:
            plano, progresso = servico.resultado(id_sessao)
        except SessaoInexistente:
            raise HTTPException(
                status_code=404,
                detail="Sessão não encontrada ou não iniciada por /contrato/iniciar.",
            )
        except ErroFidelidade as e:
            raise HTTPException(
                status_code=422,
                detail={"erro": "fidelidade", "problemas": e.problemas},
            )
        return SaidaContrato(plano_estudos=plano, registro_progresso=progresso)

    return AgentOS(
        id="tutor-estudos",
        name="Módulo 4: Tutor de estudos",
        teams=[servico.time],
        agents=[servico.planejador, servico.professor, servico.avaliador],
        base_app=base,
        telemetry=telemetria,
    )
