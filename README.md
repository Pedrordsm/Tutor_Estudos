# Módulo 4 — Tutor de estudos

Módulo conversacional do ecossistema de agentes **"Do diploma ao primeiro emprego"** (Inteligência Artificial — IFES Campus Serra · BSI · Prof. Dr. Sérgio Nery Simões).

**Grupo 4:** Kaio, Samiya, Pedro Renã, Tertuliano e Heitor.

Recebe `Lacunas` + `Curriculo`, conduz a tutoria com um **Time Agno** (`Planejador`, `Professor` e `Avaliador`), executa exercícios de código em sandbox isolada e produz `PlanoEstudos` + `RegistroProgresso` no contrato `tutor_estudos`.

## Arquitetura e arquivos

| Arquivo | Responsabilidade |
|---|---|
| `src/tutor_estudos/config.py` | Lê variáveis de ambiente e `.env` (`MODELO_LLM`, `BANCO_SQLITE`, `PORTA`, `TIMEOUT_SANDBOX`, `AGNO_TELEMETRY`). |
| `src/tutor_estudos/modelos.py` | Schemas Pydantic das rotas `/contrato/*`, avaliação de exercícios e rascunhos de extração. |
| `src/tutor_estudos/sandbox.py` | Execução isolada de Python (`assert` e funções `def test_*()`, bloqueio AST de rede/sistema, timeout) e SQL somente leitura em SQLite em memória. |
| `src/tutor_estudos/fidelidade.py` | Verificação determinística de fidelidade (habilidades só das lacunas, cobertura de prioridade alta, pré-requisitos sem ciclo, evidência obrigatória em habilidades adquiridas). |
| `src/tutor_estudos/calculos.py` | Cálculos objetivos em código (data prevista de conclusão, data da sessão, numeração dos tópicos e desempenho de 0 a 1). |
| `src/tutor_estudos/servico.py` | Time Agno com memória em SQLite, retry HTTP 429, extratores com laço de correção, plano direto e correção de exercícios (Python e SQL corrigidos em código). |
| `src/tutor_estudos/servidor.py` | Servidor AgentOS com o time, os agentes e as rotas `POST /contrato/iniciar` e `GET /contrato/resultado/{id_sessao}`. |
| `src/tutor_estudos/cli.py` | Comandos `conversar` (nova sessão ou retomada com `--sessao`), `servir` e `simular` (sessões roteirizadas). |
| `tests/` | Testes automatizados offline com `ModeloRoteirizado` (sem rede nem modelo de linguagem). |
| `casos_teste/` | Casos de teste com resultado esperado, roteiros dos formandos e script de avaliação. |
| `saidas/fXX/` | Saídas geradas com as entradas do kit (`plano_estudos.json`, `registro_progresso.json`, `transcricao.md`). |
| `relatorio/` | Relatório em Typst (modelo do kit) e anotações de falhas. |

## Funcionalidades (caderno do módulo 4)

- **F1:** Diagnóstico inicial a partir de `Lacunas` + `Curriculo` com perguntas rápidas.
- **F2:** `PlanoEstudos` priorizado com pré-requisitos e datas calculadas em código.
- **F3:** Aulas em sessões pelo `Agente Professor`.
- **F4:** Exercícios objetivos, discursivos e de código (sandbox Python/pytest e SQL em memória).
- **F5:** Adaptação do plano ao desempenho, registrada em `ajustes_plano`.
- **F6:** Sugestão de projetos práticos (`projeto_pratico`).
- **F7:** `RegistroProgresso` e `habilidades_adquiridas` só com evidência comprovada.
- **F8:** Memória persistente em SQLite entre sessões (`--sessao` na CLI ou interface do AgentOS).

## Instalação

Requer Python 3.10 ou superior. Com o kit na pasta vizinha `../kit-ecossistema`:

```bash
python -m venv .venv
.venv\Scripts\activate             # Linux/Mac: source .venv/bin/activate
pip install -e "../kit-ecossistema/contratos[entrega]"
pip install -e ".[groq,ollama,anthropic,testes]"
```

## Configuração

Copie `.env.exemplo` para `.env` e escolha o provedor em `MODELO_LLM` (formato `provedor:modelo`):

- **Groq (camada gratuita):** `MODELO_LLM=groq:llama-3.3-70b-versatile` e `GROQ_API_KEY=...`.
- **Ollama (local, gratuito):** `MODELO_LLM=ollama:qwen2.5:7b` (com o Ollama em execução).
- **Anthropic:** `MODELO_LLM=anthropic:claude-sonnet-4-5` e `ANTHROPIC_API_KEY=...`.

> Nunca envie o `.env` para o repositório.

## Execução

Todos os comandos funcionam com `python -m tutor_estudos ...` ou com o atalho `tutor-estudos ...`.

**Conversar no terminal e gerar as saídas** (digite `/fim` para gravar `plano_estudos.json` e `registro_progresso.json`):

```bash
python -m tutor_estudos conversar --entrada ../kit-ecossistema/exemplos/f01/lacunas.json ../kit-ecossistema/exemplos/f01/curriculo.json --saida-dir saidas/f01
python -m tutor_estudos conversar --sessao <ID_DA_SESSAO> --saida-dir saidas/f01   # retomar (F8)
```

**Sessões roteirizadas** (o grupo no papel do formando; gera as saídas e a transcrição):

```bash
python -m tutor_estudos simular --roteiro casos_teste/roteiros/f01.json --kit ../kit-ecossistema --saida-dir saidas/f01
```

**Servidor AgentOS:**

```bash
python -m tutor_estudos servir
```

- Rotas do contrato e documentação interativa: `http://localhost:7777/docs`.
- Interface gráfica: conecte `http://localhost:7777` em `https://os.agno.com` e selecione o time **Tutor de estudos**.

## Verificação e entrega

```bash
carreira-verificar tutor_estudos --entrada ../kit-ecossistema/exemplos/f01/lacunas.json ../kit-ecossistema/exemplos/f01/curriculo.json --saida saidas/f01/plano_estudos.json saidas/f01/registro_progresso.json
carreira-checar-entrega tutor_estudos --kit ../kit-ecossistema
```

## Testes e avaliação

```bash
python -m pytest -q                                                    # testes automatizados (sem modelo)
python casos_teste/executar_casos.py --kit ../kit-ecossistema --sem-llm   # casos corrigidos em código
python casos_teste/executar_casos.py --kit ../kit-ecossistema             # todos os casos, com o modelo do .env
```

Detalhes em [`casos_teste/README.md`](casos_teste/README.md).

## Limitações conhecidas

- Exercícios de linguagens sem runtime na sandbox (como medidas DAX do Power BI) são corrigidos conceitualmente pelo agente avaliador, sem execução.
- Modelos locais muito pequenos (como `llama3.2` 3B) apresentam instabilidade em *tool calling* dentro do `Team` (alucinação de chamada de ferramenta e repetição no histórico) e exigem novas tentativas na extração estruturada; recomenda-se um modelo com suporte robusto a ferramentas (Groq 70B, `qwen2.5:7b` ou Claude). As falhas observadas estão em `relatorio/anotacoes_falhas.md`.
- As datas das sessões no `RegistroProgresso` são as do momento em que o resultado é gerado.
