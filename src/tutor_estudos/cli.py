"""Linha de comando do Módulo 4: conversar (nova sessão ou retomada) e servir."""

import argparse
import sys
from pathlib import Path

from agno.db.sqlite import SqliteDb
from pydantic import ValidationError

from carreira_contratos import Curriculo, Lacunas, identificar, ler_json, salvar

from .config import ErroConfiguracao, carregar_configuracao
from .servico import ErroFidelidade, ServicoTutor, SessaoInexistente


def ler_entradas(arquivos: list[Path]) -> tuple[Lacunas, Curriculo]:
    """Identifica cada arquivo JSON pelo contrato e devolve Lacunas e Curriculo."""
    lacunas, curriculo = None, None
    for arq in arquivos:
        dados = ler_json(arq)
        tipos = identificar(dados)
        if tipos == ["Lacunas"]:
            lacunas = Lacunas.model_validate(dados)
        elif tipos == ["Curriculo"]:
            curriculo = Curriculo.model_validate(dados)
        else:
            raise ValueError(f"{arq}: esperado Lacunas ou Curriculo, identificado {tipos or 'nenhum modelo'}")
    if lacunas is None:
        raise ValueError("informe um arquivo Lacunas em --entrada")
    if curriculo is None:
        raise ValueError("informe um arquivo Curriculo em --entrada")
    return lacunas, curriculo


def criar_servico() -> tuple[ServicoTutor, object]:
    cfg = carregar_configuracao()
    db = SqliteDb(db_file=str(cfg.banco_sqlite))
    return (
        ServicoTutor(
            cfg.modelo_llm,
            db,
            telemetria=cfg.telemetria,
            timeout_sandbox=cfg.timeout_sandbox,
        ),
        cfg,
    )


def cmd_conversar(args, entrada=input) -> int:
    servico, _ = criar_servico()

    if args.sessao:
        id_sessao = args.sessao
        # Valida se a sessão existe e pede ao tutor para retomar de onde parou (F8)
        mensagem = servico.conversar(
            id_sessao,
            "Estou voltando para continuar meus estudos. Relembre brevemente onde paramos e qual é o próximo passo.",
        )
    else:
        if not args.entrada:
            raise ValueError("informe --entrada com os arquivos Lacunas e Curriculo (ou --sessao para retomar)")
        lacunas, curriculo = ler_entradas(args.entrada)
        id_sessao, mensagem = servico.iniciar(lacunas, curriculo)

    print(
        f"Sessão {id_sessao}.\n"
        "Digite /fim para gerar plano_estudos.json e registro_progresso.json e sair "
        "(use --sessao com este ID depois para retomar).\n"
    )
    print(f"Tutor: {mensagem}")

    while True:
        texto = entrada("\nVocê: ").strip()
        if texto == "/fim":
            break
        if texto:
            resposta = servico.conversar(id_sessao, texto)
            print(f"\nTutor: {resposta}")

    plano, progresso = servico.resultado(id_sessao)
    args.saida_dir.mkdir(parents=True, exist_ok=True)
    arq_plano = args.saida_dir / "plano_estudos.json"
    arq_progresso = args.saida_dir / "registro_progresso.json"
    salvar(plano, arq_plano)
    salvar(progresso, arq_progresso)

    print(f"\nSaídas gravadas em:\n- {arq_plano}\n- {arq_progresso}")
    return 0


def cmd_servir(args) -> int:
    from .servidor import criar_agent_os

    servico, cfg = criar_servico()
    agent_os = criar_agent_os(servico, telemetria=cfg.telemetria)
    agent_os.serve(app=agent_os.get_app(), port=args.porta or cfg.porta)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="tutor-estudos",
        description="Módulo 4 do ecossistema: Tutor de estudos.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_conv = sub.add_parser("conversar", help="inicia ou retoma uma sessão interativa de tutoria no terminal")
    p_conv.add_argument(
        "--entrada",
        nargs="+",
        type=Path,
        default=None,
        help="arquivos Lacunas e Curriculo do formando (obrigatório ao iniciar nova sessão)",
    )
    p_conv.add_argument(
        "--sessao",
        type=str,
        default=None,
        help="ID de uma sessão anterior para retomar de onde parou (F8)",
    )
    p_conv.add_argument(
        "--saida-dir",
        type=Path,
        default=Path("saidas/f01"),
        help="pasta onde plano_estudos.json e registro_progresso.json serão salvos",
    )

    p_serv = sub.add_parser("servir", help="inicia o servidor AgentOS com as rotas do contrato")
    p_serv.add_argument("--porta", type=int, default=None, help="porta do servidor (padrão: PORTA do .env)")

    args = parser.parse_args(argv)
    comandos = {"conversar": cmd_conversar, "servir": cmd_servir}
    try:
        return comandos[args.comando](args)
    except (ErroConfiguracao, SessaoInexistente, ValueError, ValidationError, OSError) as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 2
    except ErroFidelidade as e:
        print(
            "Erro: a saída extraída não passou na verificação de fidelidade:\n- " + "\n- ".join(e.problemas),
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    sys.exit(main())
