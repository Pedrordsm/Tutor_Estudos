"""Execução isolada de exercícios de código (Python, testes pytest e SQL em memória).

Implementa o guardrail da seção 8 do Caderno M4:
- execução em processo isolado (`python -I`, diretório temporário, ambiente mínimo);
- limite de tempo (timeout);
- sem acesso à rede nem módulos perigosos (verificação AST antes de rodar).
"""

import ast
import json
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path

MODULOS_BLOQUEADOS = frozenset({
    "os", "sys", "subprocess", "shutil", "pathlib", "socket", "http", "urllib",
    "requests", "httpx", "ftplib", "smtplib", "ssl", "ctypes", "multiprocessing",
    "threading", "importlib", "builtins", "pickle", "marshal", "tempfile", "glob",
    "webbrowser", "asyncio", "signal", "resource",
})

CHAMADAS_BLOQUEADAS = frozenset({
    "open", "eval", "exec", "compile", "__import__", "input", "breakpoint",
})


@dataclass(frozen=True)
class ResultadoSandbox:
    passou: bool
    saida: str
    erro: str
    timeout: bool = False
    bloqueado: bool = False


def verificar_seguranca_ast(codigo: str) -> str | None:
    """Analisa a AST do código Python e retorna o motivo de bloqueio, se houver."""
    try:
        arvore = ast.parse(codigo)
    except SyntaxError as e:
        return f"Erro de sintaxe na linha {e.lineno}: {e.msg}"

    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            for alias in no.names:
                raiz = alias.name.split(".")[0]
                if raiz in MODULOS_BLOQUEADOS:
                    return f"Importação bloqueada na sandbox: {raiz}"
        elif isinstance(no, ast.ImportFrom):
            if no.module:
                raiz = no.module.split(".")[0]
                if raiz in MODULOS_BLOQUEADOS:
                    return f"Importação bloqueada na sandbox: {raiz}"
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            if no.func.id in CHAMADAS_BLOQUEADAS:
                return f"Chamada bloqueada na sandbox: {no.func.id}()"
    return None


def _analisar_funcoes_teste(codigo_aluno: str) -> tuple[list[str], list[str]]:
    """Retorna (funcoes_test, funcoes_test_sem_assert) encontradas no código do aluno."""
    arvore = ast.parse(codigo_aluno)
    nomes_teste: list[str] = []
    sem_assert: list[str] = []
    for no in arvore.body:
        if isinstance(no, ast.FunctionDef) and no.name.startswith("test_"):
            nomes_teste.append(no.name)
            tem_assert = any(isinstance(sub, ast.Assert) for sub in ast.walk(no))
            if not tem_assert:
                sem_assert.append(no.name)
    return nomes_teste, sem_assert


def executar_python_isolado(
    codigo_formando: str,
    codigo_testes: str = "",
    timeout: int = 5,
) -> ResultadoSandbox:
    """Executa código Python do formando junto com os testes em subprocesso isolado."""
    erro_seg = verificar_seguranca_ast(codigo_formando)
    if erro_seg:
        bloqueado = "bloqueada" in erro_seg
        return ResultadoSandbox(passou=False, saida="", erro=erro_seg, bloqueado=bloqueado)

    if codigo_testes.strip():
        erro_testes = verificar_seguranca_ast(codigo_testes)
        if erro_testes:
            return ResultadoSandbox(passou=False, saida="", erro=f"Nos testes: {erro_testes}", bloqueado=True)

    funcoes_teste, sem_assert = _analisar_funcoes_teste(codigo_formando)
    if sem_assert:
        return ResultadoSandbox(
            passou=False,
            saida="",
            erro=f"Função de teste sem nenhuma asserção (assert): {', '.join(sem_assert)}.",
        )

    # Quando o formando escreve funções `def test_*()` (estilo pytest, ex.: e12/e13 do kit),
    # o código auxiliar (`codigo_testes`, ex.: `def soma(a, b)`) precisa vir antes e os testes
    # precisam ser invocados explicitamente.
    if funcoes_teste:
        chamadas = "\n".join(f"{nome}()" for nome in funcoes_teste)
        script = f"{codigo_testes}\n\n{codigo_formando}\n\n{chamadas}\n"
    else:
        script = f"{codigo_formando}\n\n{codigo_testes}\n"

    with tempfile.TemporaryDirectory(prefix="tutor_sandbox_") as tmpdir:
        arquivo = Path(tmpdir) / "solucao.py"
        arquivo.write_text(script, encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(arquivo)],
                cwd=tmpdir,
                env={"PYTHONIOENCODING": "utf-8"},
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return ResultadoSandbox(
                passou=False,
                saida="",
                erro=f"Tempo limite excedido ({timeout}s). Verifique se há loop infinito.",
                timeout=True,
            )

    if proc.returncode == 0:
        return ResultadoSandbox(passou=True, saida=proc.stdout.strip(), erro="")
    return ResultadoSandbox(
        passou=False,
        saida=proc.stdout.strip(),
        erro=(proc.stderr or proc.stdout).strip() or f"Processo terminou com código {proc.returncode}.",
    )


def executar_sql_memoria(consulta: str, setup_sql: str) -> ResultadoSandbox:
    """Executa uma consulta SQL somente leitura em um banco SQLite em memória."""
    limpa = consulta.strip().lstrip("(")
    if not limpa.upper().startswith(("SELECT", "WITH")):
        return ResultadoSandbox(
            passou=False,
            saida="",
            erro="Apenas consultas SELECT/WITH são permitidas na sandbox SQL.",
            bloqueado=True,
        )

    con = sqlite3.connect(":memory:")
    try:
        con.executescript(setup_sql)
        cursor = con.execute(consulta)
        colunas = [desc[0] for desc in (cursor.description or [])]
        linhas = cursor.fetchall()
        payload = json.dumps({"colunas": colunas, "linhas": linhas}, ensure_ascii=False)
        return ResultadoSandbox(passou=True, saida=payload, erro="")
    except sqlite3.Error as e:
        return ResultadoSandbox(passou=False, saida="", erro=f"Erro SQL: {e}")
    finally:
        con.close()


# ---------------------------------------------- tools expostas ao agente Agno

def executar_codigo_python(codigo_formando: str, codigo_testes: str = "") -> str:
    """Executa código Python de um exercício em ambiente isolado (sem rede, timeout de 5s) e retorna o resultado em JSON."""
    res = executar_python_isolado(codigo_formando, codigo_testes)
    return json.dumps(asdict(res), ensure_ascii=False)


def executar_sql_em_memoria(consulta_sql: str, setup_tabelas_sql: str) -> str:
    """Executa uma consulta SQL SELECT em um banco SQLite em memória criado a partir de setup_tabelas_sql e retorna o resultado em JSON."""
    res = executar_sql_memoria(consulta_sql, setup_tabelas_sql)
    return json.dumps(asdict(res), ensure_ascii=False)
