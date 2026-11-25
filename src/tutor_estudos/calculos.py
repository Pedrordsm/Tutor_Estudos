"""Cálculos determinísticos feitos em código (datas, ordem e desempenho)."""

import math
from datetime import date, datetime, timedelta, timezone

from carreira_contratos import (
    Exercicio,
    Lacunas,
    PlanoEstudos,
    RegistroProgresso,
    SessaoEstudo,
    TopicoEstudo,
    novo_cabecalho,
)

from .modelos import RascunhoPlano, RascunhoProgresso

MODULO = "tutor_estudos"


def calcular_data_conclusao(data_inicio: date, total_horas: float, horas_semanais: float) -> date:
    """Calcula a data prevista de conclusão com base na carga horária total e semanal."""
    if total_horas <= 0 or horas_semanais <= 0:
        return data_inicio
    dias = math.ceil((total_horas / horas_semanais) * 7)
    return data_inicio + timedelta(days=dias)


def calcular_desempenho(exercicios: list[Exercicio]) -> float:
    """Calcula o desempenho (0.0 a 1.0) a partir dos exercícios corrigidos na sessão."""
    corrigidos = [e for e in exercicios if e.correto is not None]
    if not corrigidos:
        return 0.0
    acertos = sum(1 for e in corrigidos if e.correto)
    return round(acertos / len(corrigidos), 2)


def montar_plano(
    rascunho: RascunhoPlano,
    lacunas: Lacunas,
    id_formando: str,
    data_inicio: date | None = None,
) -> PlanoEstudos:
    """Converte um rascunho verificado em PlanoEstudos oficial com ordem e datas calculadas."""
    inicio = data_inicio or date.today()

    topicos: list[TopicoEstudo] = [
        TopicoEstudo(
            ordem=idx,
            habilidade=t.habilidade,
            titulo=t.titulo,
            objetivos=t.objetivos,
            prerequisitos=t.prerequisitos,
            horas_estimadas=t.horas_estimadas,
            atividades=t.atividades,
            projeto_pratico=t.projeto_pratico,
            situacao=t.situacao,
        )
        for idx, t in enumerate(rascunho.topicos, start=1)
    ]

    total_horas = sum(t.horas_estimadas for t in topicos)
    conclusao = calcular_data_conclusao(inicio, total_horas, rascunho.horas_semanais)

    return PlanoEstudos(
        cabecalho=novo_cabecalho(MODULO, id_formando),
        horas_semanais=rascunho.horas_semanais,
        data_inicio=inicio,
        data_prevista_conclusao=conclusao,
        topicos=topicos,
    )


def montar_progresso(
    rascunho: RascunhoProgresso,
    id_formando: str,
    agora: datetime | None = None,
) -> RegistroProgresso:
    """Converte um rascunho verificado em RegistroProgresso oficial com data real e desempenho calculado."""
    momento = agora or datetime.now(timezone.utc).astimezone()

    sessoes = [
        SessaoEstudo(
            data=momento,
            topico=s.topico,
            resumo_explicacao=s.resumo_explicacao,
            exercicios=s.exercicios,
            desempenho=calcular_desempenho(s.exercicios),
        )
        for s in rascunho.sessoes
    ]

    return RegistroProgresso(
        cabecalho=novo_cabecalho(MODULO, id_formando),
        sessoes=sessoes,
        habilidades_adquiridas=rascunho.habilidades_adquiridas,
        ajustes_plano=rascunho.ajustes_plano,
    )
