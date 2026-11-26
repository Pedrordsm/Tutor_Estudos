"""Executa os casos de teste do Módulo 4 e calcula as métricas sugeridas no caderno (seção 10).

Uso (na raiz do repositório):
    python casos_teste/executar_casos.py --kit ../kit-ecossistema --sem-llm   # só o que é corrigido em código
    python casos_teste/executar_casos.py --kit ../kit-ecossistema             # tudo, com o modelo do .env

Os resultados esperados estão em casos_teste/casos.json e foram definidos antes da execução.
Os resultados vão para casos_teste/resultados/<rotulo>.json e <rotulo>.md.
"""

import argparse
import json
import math
import re
import unicodedata
from datetime import timedelta
from pathlib import Path

from carreira_contratos import Curriculo, Lacunas, PlanoEstudos, RegistroProgresso, ler_json
from carreira_contratos.verificar import verificar as verificar_contrato

from tutor_estudos.fidelidade import verificar_plano, verificar_progresso
from tutor_estudos.modelos import RascunhoPlano, RascunhoProgresso
from tutor_estudos.sandbox import executar_python_isolado, executar_sql_memoria
from tutor_estudos.servico import ServicoTutor

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent


def _norm(texto: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower().split())


def carregar_entradas(kit: Path, formando: str) -> tuple[Lacunas, Curriculo]:
    lac = Lacunas.model_validate(ler_json(kit / "exemplos" / formando / "lacunas.json"))
    cv = Curriculo.model_validate(ler_json(kit / "exemplos" / formando / "curriculo.json"))
    return lac, cv


# ------------------------------------------------------------------ métricas do plano

def medir_plano(plano: PlanoEstudos, lacunas: Lacunas, horas_informadas: float | None) -> dict:
    nomes_lacunas = {_norm(l.habilidade) for l in lacunas.itens}
    habilidades_plano = [_norm(t.habilidade) for t in plano.topicos]
    altas = {_norm(l.habilidade) for l in lacunas.itens if l.prioridade == "alta"}

    vistos, prereq_ok = set(), True
    for t in sorted(plano.topicos, key=lambda t: t.ordem):
        if any(_norm(p) not in vistos for p in t.prerequisitos):
            prereq_ok = False
        vistos.add(_norm(t.titulo))

    total = sum(t.horas_estimadas for t in plano.topicos)
    fim_esperado = plano.data_inicio + timedelta(days=math.ceil(total / plano.horas_semanais * 7))
    disponibilidade = plano.data_prevista_conclusao == fim_esperado
    if horas_informadas is not None:
        disponibilidade = disponibilidade and math.isclose(plano.horas_semanais, horas_informadas)

    return {
        "cobre_todas_alta": altas <= set(habilidades_plano),
        "somente_lacunas": all(h in nomes_lacunas for h in habilidades_plano),
        "prerequisitos_ok": prereq_ok,
        "respeita_disponibilidade": disponibilidade,
        "topicos_fora_das_lacunas": sorted({t.habilidade for t in plano.topicos if _norm(t.habilidade) not in nomes_lacunas}),
    }


# ------------------------------------------------------------------ blocos de casos

def casos_correcao(casos, respostas, servico) -> list[dict]:
    resultados = []
    for caso in casos:
        r = respostas[caso["resposta"]]
        if servico is not None:
            ex = servico.avaliar_exercicio(
                r["enunciado"], r["tipo"], r["resposta_formando"],
                testes=r.get("testes"), sql_setup=caso.get("sql_setup"), sql_referencia=caso.get("sql_referencia"),
            )
            obtido, como = ex.correto, "modelo" if not (r.get("testes") or caso.get("sql_setup")) else "codigo"
        elif caso.get("sql_setup"):
            obtido, como = ServicoTutor._avaliar_sql(r["enunciado"], r["resposta_formando"], caso["sql_setup"], caso["sql_referencia"]).correto, "codigo"
        elif r.get("testes"):
            obtido, como = executar_python_isolado(r["resposta_formando"], r["testes"], timeout=2).passou, "codigo"
        else:
            continue  # sem modelo não há como corrigir respostas discursivas/objetivas
        resultados.append({"id": caso["id"], "resposta": caso["resposta"], "tipo": r["tipo"], "corrigido_por": como,
                           "esperado": caso["esperado"], "obtido": obtido, "acertou": obtido == caso["esperado"]})
    return resultados


def casos_seguranca(casos) -> list[dict]:
    resultados = []
    for caso in casos:
        if "sql" in caso:
            res = executar_sql_memoria(caso["sql"], "CREATE TABLE clientes (id INTEGER);")
        else:
            res = executar_python_isolado(caso["codigo"], timeout=2)
        obtido = "bloqueado" if res.bloqueado else "tempo_esgotado" if res.timeout else ("executou" if res.passou else "erro")
        resultados.append({"id": caso["id"], "esperado": caso["esperado"], "obtido": obtido, "acertou": obtido == caso["esperado"]})
    return resultados


def casos_guardrails(casos, kit: Path) -> list[dict]:
    lac_f01, _ = carregar_entradas(kit, "f01")
    lac_f02, _ = carregar_entradas(kit, "f02")

    def topico(hab, titulo):
        return {"habilidade": hab, "titulo": titulo, "objetivos": ["Objetivo"], "horas_estimadas": 4.0}

    planos = {
        "G01": (RascunhoPlano.model_validate({"horas_semanais": 6, "topicos": [topico("Power BI", "Modelagem"), topico("Kubernetes", "Pods")]}), lac_f01),
        "G02": (RascunhoPlano.model_validate({"horas_semanais": 6, "topicos": [topico("Django", "Models"), topico("Testes automatizados", "pytest")]}), lac_f02),
    }
    ex_ok = {"enunciado": "Q", "tipo": "objetiva", "resposta_formando": "(b)", "correto": True, "feedback": "Ok"}
    progresso = {
        "G03": RascunhoProgresso.model_validate({"sessoes": [], "habilidades_adquiridas": [{"nome": "SQL", "categoria": "tecnica", "nivel": "basico", "evidencias": []}]}),
        "G04": RascunhoProgresso.model_validate({"sessoes": [{"topico": "SQL", "exercicios": [ex_ok]}],
                                                  "habilidades_adquiridas": [{"nome": "SQL", "categoria": "tecnica", "nivel": "basico", "evidencias": ["Exercício de HAVING resolvido corretamente"]}]}),
    }
    resultados = []
    for caso in casos:
        problemas = verificar_plano(*planos[caso["id"]]) if caso["id"] in planos else verificar_progresso(progresso[caso["id"]])
        obtido = "rejeitado" if problemas else "aceito"
        resultados.append({"id": caso["id"], "esperado": caso["esperado"], "obtido": obtido, "acertou": obtido == caso["esperado"], "problemas": problemas})
    return resultados


def casos_planos(casos, kit: Path, servico) -> list[dict]:
    resultados = []
    for caso in casos:
        lac, cv = carregar_entradas(kit, caso["formando"])
        try:
            plano = servico.planejar(lac, cv, caso["horas_semanais"])
            medido = medir_plano(plano, lac, caso["horas_semanais"])
        except Exception as erro:  # noqa: BLE001 - registrar qualquer falha do modelo como resultado
            medido = {"erro": str(erro)}
        acertou = all(medido.get(k) == v for k, v in caso["esperado"].items())
        resultados.append({"id": caso["id"], "formando": caso["formando"], **medido, "acertou": acertou})
    return resultados


def auditar_saidas(kit: Path, casos_adaptacao) -> tuple[list[dict], list[dict]]:
    """Confere as saídas gravadas em saidas/fXX: contrato (verificador do kit) e fidelidade às lacunas."""
    auditoria, adaptacao = [], []
    for formando in ("f01", "f02", "f03"):
        pasta = RAIZ / "saidas" / formando
        if not (pasta / "plano_estudos.json").exists():
            auditoria.append({"formando": formando, "situacao": "sem saídas"})
            continue
        lac, cv = carregar_entradas(kit, formando)
        plano = PlanoEstudos.model_validate(ler_json(pasta / "plano_estudos.json"))
        prog = RegistroProgresso.model_validate(ler_json(pasta / "registro_progresso.json"))
        rel = verificar_contrato("tutor_estudos", entradas={"Lacunas": lac, "Curriculo": cv},
                                 saidas={"PlanoEstudos": plano, "RegistroProgresso": prog})
        medido = medir_plano(plano, lac, None)
        auditoria.append({"formando": formando, "verificador_ok": not rel.erros, **medido,
                          "sessoes": len(prog.sessoes), "ajustes_plano": len(prog.ajustes_plano)})
        for caso in casos_adaptacao:
            if caso["formando"] == formando:
                obtido = len(prog.ajustes_plano) > 0
                adaptacao.append({"id": caso["id"], "formando": formando, "esperado": True, "obtido": obtido, "acertou": obtido})
    return auditoria, adaptacao


# ------------------------------------------------------------------ relatório

def taxa(itens) -> str:
    if not itens:
        return "—"
    ok = sum(1 for i in itens if i["acertou"])
    return f"{ok}/{len(itens)} ({100 * ok / len(itens):.0f}%)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kit", type=Path, default=RAIZ.parent / "kit-ecossistema")
    parser.add_argument("--sem-llm", action="store_true", help="executa só os casos corrigidos em código")
    args = parser.parse_args()

    casos = json.loads((AQUI / "casos.json").read_text(encoding="utf-8"))
    respostas = {r["id"]: r for r in ler_json(args.kit / "insumos" / "m4_tutor_estudos" / "respostas_simuladas.json")["respostas"]}

    servico, rotulo = None, "sem_llm"
    if not args.sem_llm:
        from tutor_estudos.cli import criar_servico
        servico, cfg = criar_servico()
        rotulo = re.sub(r"[^a-zA-Z0-9]+", "_", cfg.modelo_llm).strip("_")

    res = {
        "rotulo": rotulo,
        "correcao": casos_correcao(casos["correcao"], respostas, servico),
        "seguranca": casos_seguranca(casos["seguranca"]),
        "guardrails": casos_guardrails(casos["guardrails"], args.kit),
        "planos": casos_planos(casos["planos"], args.kit, servico) if servico else [],
    }
    res["auditoria_saidas"], res["adaptacao"] = auditar_saidas(args.kit, casos["adaptacao"])

    metricas = [
        ("Acerto do avaliador na correção (respostas simuladas do kit)", res["correcao"]),
        ("Execução isolada bloqueia código perigoso / laço infinito", res["seguranca"]),
        ("Guardrails de fidelidade e evidência", res["guardrails"]),
        ("Planos que cumprem todos os critérios (alta, lacunas, pré-requisitos, disponibilidade)", res["planos"]),
        ("Adaptação: plano ajustado após baixo desempenho", res["adaptacao"]),
    ]
    linhas = [f"# Resultados dos casos de teste — {rotulo}", "", "| Métrica | Resultado |", "|---|---|"]
    linhas += [f"| {nome} | {taxa(itens)} |" for nome, itens in metricas]
    linhas += ["", "## Auditoria das saídas gravadas em saidas/", "", "| Formando | Situação |", "|---|---|"]
    for a in res["auditoria_saidas"]:
        if "situacao" in a:
            linhas.append(f"| {a['formando']} | {a['situacao']} |")
        else:
            fora = ", ".join(a["topicos_fora_das_lacunas"]) or "nenhum"
            linhas.append(f"| {a['formando']} | verificador {'ok' if a['verificador_ok'] else 'FALHOU'}; "
                          f"cobre alta: {a['cobre_todas_alta']}; tópicos fora das lacunas: {fora}; "
                          f"disponibilidade coerente: {a['respeita_disponibilidade']}; sessões: {a['sessoes']}; ajustes: {a['ajustes_plano']} |")
    erros = [i for bloco in ("correcao", "seguranca", "guardrails", "planos") for i in res[bloco] if not i["acertou"]]
    if erros:
        linhas += ["", "## Casos com resultado diferente do esperado", ""]
        linhas += [f"- {e['id']}: esperado {e.get('esperado')}, obtido {e.get('obtido', e.get('erro'))}" for e in erros]

    destino = AQUI / "resultados"
    destino.mkdir(exist_ok=True)
    (destino / f"{rotulo}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (destino / f"{rotulo}.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("\n".join(linhas))
    print(f"\nResultados gravados em {destino / rotulo}.json/.md")


if __name__ == "__main__":
    main()
