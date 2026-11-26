"""Testes do comando simular e das métricas dos casos de teste."""

import importlib.util
import json
from datetime import date
from pathlib import Path

from carreira_contratos import PlanoEstudos, RegistroProgresso, salvar
from tutor_estudos import cli
from tutor_estudos.calculos import montar_plano
from tutor_estudos.modelos import RascunhoPlano

from conftest import json_rascunho_plano, json_rascunho_progresso


def _carregar_executar_casos():
    caminho = Path(__file__).resolve().parent.parent / "casos_teste" / "executar_casos.py"
    spec = importlib.util.spec_from_file_location("executar_casos", caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_cli_simular_grava_saidas_e_transcricao(fabrica, lacunas_ficticias, curriculo_ficticio, tmp_path, monkeypatch):
    kit = tmp_path / "kit"
    (kit / "exemplos" / "f01").mkdir(parents=True)
    salvar(lacunas_ficticias, kit / "exemplos" / "f01" / "lacunas.json")
    salvar(curriculo_ficticio, kit / "exemplos" / "f01" / "curriculo.json")
    roteiro = tmp_path / "f01.json"
    roteiro.write_text(json.dumps({
        "id_formando": "f01", "lacunas": "exemplos/f01/lacunas.json", "curriculo": "exemplos/f01/curriculo.json",
        "sessoes": [["Tenho 6h por semana."], ["Voltei. Onde paramos?"]],
    }), encoding="utf-8")

    servico, _ = fabrica("Olá!", "Anotado: 6h/semana.", "Paramos em Power BI.",
                         json_rascunho_plano(), json_rascunho_progresso())
    monkeypatch.setattr(cli, "criar_servico", lambda: (servico, None))

    saida = tmp_path / "saidas" / "f01"
    assert cli.main(["simular", "--roteiro", str(roteiro), "--kit", str(kit), "--saida-dir", str(saida)]) == 0
    PlanoEstudos.model_validate(json.loads((saida / "plano_estudos.json").read_text(encoding="utf-8")))
    RegistroProgresso.model_validate(json.loads((saida / "registro_progresso.json").read_text(encoding="utf-8")))
    transcricao = (saida / "transcricao.md").read_text(encoding="utf-8")
    assert "## Sessão 2" in transcricao and "Paramos em Power BI." in transcricao


def test_metricas_do_plano(lacunas_ficticias):
    medir_plano = _carregar_executar_casos().medir_plano
    bom = montar_plano(RascunhoPlano.model_validate_json(json_rascunho_plano()), lacunas_ficticias, "f01", date(2026, 11, 25))
    m = medir_plano(bom, lacunas_ficticias, 6.0)
    assert m["cobre_todas_alta"] and m["somente_lacunas"] and m["prerequisitos_ok"] and m["respeita_disponibilidade"]

    ruim = montar_plano(RascunhoPlano.model_validate_json(json_rascunho_plano(habilidade_extra="Rust", incluir_power_bi=False)),
                        lacunas_ficticias, "f01", date(2026, 11, 25))
    m = medir_plano(ruim, lacunas_ficticias, 10.0)
    assert not m["cobre_todas_alta"] and not m["somente_lacunas"] and not m["respeita_disponibilidade"]
    assert m["topicos_fora_das_lacunas"] == ["Rust"]
