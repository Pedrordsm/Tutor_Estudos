# Módulo 4 — Tutor de estudos

Módulo conversacional do ecossistema de agentes **"Do diploma ao primeiro emprego"** (Inteligência Artificial — IFES Campus Serra).

Recebe `Lacunas` + `Curriculo`, conduz a tutoria com um **Time Agno** (`Planejador`, `Professor` e `Avaliador`), executa exercícios de código em sandbox isolada e produz `PlanoEstudos` + `RegistroProgresso` no contrato `tutor_estudos`.

## Arquitetura e arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/tutor_estudos/config.py` | Lê variáveis de ambiente e `.env` (`MODELO_LLM`, `BANCO_SQLITE`, `PORTA`, `TIMEOUT_SANDBOX`, `AGNO_TELEMETRY`). |
| `src/tutor_estudos/modelos.py` | Schemas Pydantic das rotas `/contrato/*`, avaliação de exercícios e rascunhos de extração. |
| `src/tutor_estudos/sandbox.py` | Execução isolada de Python (incluindo `assert` e funções `def test_*()` estilo pytest, bloqueio AST de rede/sistema e timeout) e SQL somente leitura em SQLite em memória. |
| `src/tutor_estudos/fidelidade.py` | Verificação determinística de fidelidade e guardrails (habilidades dentro das lacunas, cobertura de prioridade alta, pré-requisitos sem ciclo, evidência obrigatória em habilidades adquiridas). |
| `src/tutor_estudos/calculos.py` | Cálculos objetivos em código (data prevista de conclusão, data real da sessão, numeração de tópicos e desempenho 0..1). |
| `src/tutor_estudos/servico.py` | Time Agno (`Planejador`, `Professor`, `Avaliador`) com memória em SQLite, retry HTTP 429, extratores com loop de correção (`fidelidade.py`) e avaliação unitária de exercícios. |
| `src/tutor_estudos/servidor.py` | Servidor AgentOS expondo o time, os agentes e as rotas `POST /contrato/iniciar` e `GET /contrato/resultado/{id_sessao}`. |
| `src/tutor_estudos/cli.py` | Comandos `conversar` (nova sessão ou retomada com `--sessao`) e `servir`. |
| `tests/` | Testes automatizados offline usando `ModeloRoteirizado` (sem acesso à rede). |

## Funcionalidades cobertas (Caderno M4)

- **F1:** Diagnóstico inicial a partir de `Lacunas` + `Curriculo` com perguntas rápidas.
- **F2:** `PlanoEstudos` priorizado com pré-requisitos e datas calculadas em código.
- **F3:** Aulas didáticas em sessões pelo `Agente Professor`.
- **F4:** Exercícios objetivos, discursivos e de código (sandbox isolada Python/pytest + SQL em memória).
- **F5:** Adaptação do plano ao desempenho e registro em `ajustes_plano`.
- **F6:** Sugestão de projetos práticos (`projeto_pratico`).
- **F7:** `RegistroProgresso` e `habilidades_adquiridas` somente com evidência comprovada.
- **F8:** Memória persistente em SQLite entre sessões (`--sessao` na CLI ou interface do AgentOS).

## Instalação

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -e caminho\do\kit\contratos
pip install -e ".[ollama,anthropic,testes]"
```

## Configuração

Copie `.env.exemplo` para `.env` e escolha o provedor:

- **Ollama (local / gratuito):** `MODELO_LLM=ollama:llama3.2` (com Ollama em execução).
- **Anthropic (Claude):** `MODELO_LLM=anthropic:claude-sonnet-4-5` e `ANTHROPIC_API_KEY=...`.

> Nunca envie o `.env` para o repositório.

## Execução

### Conversar no terminal e gerar saídas

```cmd
python -m tutor_estudos conversar --entrada ..\kit-ecossistema-alunos-v1.0\kit-ecossistema\exemplos\f01\lacunas.json ..\kit-ecossistema-alunos-v1.0\kit-ecossistema\exemplos\f01\curriculo.json --saida-dir saidas\f01
```

Digite `/fim` para gravar `plano_estudos.json` e `registro_progresso.json`. Para continuar a mesma sessão depois (F8):

```cmd
python -m tutor_estudos conversar --sessao <ID_DA_SESSAO> --saida-dir saidas\f01
```

### Subir o servidor AgentOS

```cmd
python -m tutor_estudos servir
```

Documentação interativa em `http://localhost:7777/docs` e painel gráfico em `os.agno.com` apontando para `http://localhost:7777`.

### Verificar conformidade com o contrato

```cmd
python -m carreira_contratos.verificar tutor_estudos --entrada ..\kit-ecossistema-alunos-v1.0\kit-ecossistema\exemplos\f01\lacunas.json ..\kit-ecossistema-alunos-v1.0\kit-ecossistema\exemplos\f01\curriculo.json --saida saidas\f01\plano_estudos.json saidas\f01\registro_progresso.json
```

## Testes automatizados

```cmd
python -m pytest -v
```

## Limitações conhecidas

- Exercícios de linguagens sem runtime local na sandbox (como medidas DAX do Power BI) são corrigidos conceitualmente pelo agente avaliador, sem execução.
- Modelos locais menores (ex.: `llama3.2` 3B) podem exigir mais tentativas na extração estruturada quando comparados a modelos maiores (ex.: Claude).
