"""Verificação determinística de fidelidade e consistência das saídas do Módulo 4.

Segue o mesmo padrão do `fidelidade.py` do módulo de exemplo: devolve uma lista
de problemas encontrados; lista vazia significa saída fiel e coerente. Quando há
problemas, o `ServicoTutor` pede ao extrator para corrigir antes de desistir.
"""

import unicodedata

from carreira_contratos import Lacunas

from .modelos import RascunhoPlano, RascunhoProgresso

LIMITE_HORAS_SEMANAIS = 80.0


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


def verificar_plano(rascunho: RascunhoPlano, lacunas: Lacunas) -> list[str]:
    """Confere se o plano cobre as lacunas prioritárias, não inventa habilidades e respeita pré-requisitos."""
    problemas: list[str] = []

    if rascunho.horas_semanais > LIMITE_HORAS_SEMANAIS:
        problemas.append(
            f"horas_semanais={rascunho.horas_semanais} é irreal (máximo {LIMITE_HORAS_SEMANAIS}); "
            "não confunda o total de horas do plano com a disponibilidade semanal."
        )

    habilidades_lacunas = {_normalizar(l.habilidade) for l in lacunas.itens}
    if habilidades_lacunas:
        for t in rascunho.topicos:
            if _normalizar(t.habilidade) not in habilidades_lacunas:
                permitidas = ", ".join(l.habilidade for l in lacunas.itens)
                problemas.append(
                    f"O tópico \"{t.titulo}\" trabalha a habilidade \"{t.habilidade}\", "
                    f"que não está nas lacunas do formando ({permitidas})."
                )

    cobertas = {_normalizar(t.habilidade) for t in rascunho.topicos}
    for l in lacunas.itens:
        if l.prioridade == "alta" and _normalizar(l.habilidade) not in cobertas:
            problemas.append(f"A lacuna de prioridade alta \"{l.habilidade}\" não tem nenhum tópico no plano.")

    # Pré-requisitos devem existir e aparecer ANTES do tópico que depende deles (sem ciclos)
    vistos: set[str] = set()
    for t in rascunho.topicos:
        for pre in t.prerequisitos:
            if _normalizar(pre) not in vistos:
                problemas.append(
                    f"O pré-requisito \"{pre}\" do tópico \"{t.titulo}\" não aparece em nenhum tópico anterior do plano."
                )
        vistos.add(_normalizar(t.titulo))

    for t in rascunho.topicos:
        if not t.objetivos and not t.atividades:
            problemas.append(f"O tópico \"{t.titulo}\" precisa ter pelo menos objetivos ou atividades preenchidos.")

    return problemas


def verificar_progresso(rascunho: RascunhoProgresso) -> list[str]:
    """Confere guardrails de evidência e consistência dos exercícios nas sessões."""
    problemas: list[str] = []

    tem_exercicio_correto = any(
        ex.correto is True for s in rascunho.sessoes for ex in s.exercicios
    )

    for hab in rascunho.habilidades_adquiridas:
        evidencias_validas = [e for e in hab.evidencias if e.strip()]
        if not evidencias_validas:
            problemas.append(
                f"A habilidade adquirida \"{hab.nome}\" não tem evidência registrada; "
                "remova-a ou cite o exercício/projeto concluído."
            )
        elif not tem_exercicio_correto and not any("projeto" in e.lower() for e in evidencias_validas):
            problemas.append(
                f"A habilidade \"{hab.nome}\" foi marcada como adquirida sem nenhum exercício corrigido "
                "como correto nas sessões nem evidência de projeto concluído."
            )

    for s in rascunho.sessoes:
        for ex in s.exercicios:
            if ex.correto is not None and not (ex.resposta_formando and ex.resposta_formando.strip()):
                problemas.append(
                    f"Na sessão \"{s.topico}\", há exercício marcado com correto={ex.correto} sem resposta_formando."
                )

    return problemas
