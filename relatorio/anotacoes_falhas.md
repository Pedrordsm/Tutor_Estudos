# Anotações de Falhas Observadas (Material para o Relatório — Fase 4)

Registro de falhas concretas observadas durante os testes do **Módulo 4 (`tutor_estudos`)** com o modelo local `ollama:llama3.2` (3B), para compor a seção de **Análise de falhas** e a **comparação entre modelos** no relatório final.

---

## Falha 1 — Chamada incorreta de tool (alucinação) e loop no histórico

- **Data:** 25/11/2026
- **Modelo:** `ollama:llama3.2` (3B)
- **Contexto:** Conversa pela interface gráfica (`os.agno.com`) com o `Team` `tutor-estudos-time` (Planejador, Professor e Avaliador com tools da sandbox).
- **O que aconteceu:**
  1. Ao propor um exercício de código, o agente instruiu o usuário a "executar o código na sandbox isolada" em vez de pedir o código no chat para ele mesmo chamar a tool `executar_codigo_python`.
  2. Quando o usuário enviou a função `def area_circulo(r): return math.pi * (r**2)`, o `llama3.2` alucinou que `area_circulo` era o nome de uma tool disponível e emitiu um JSON cru como resposta de texto.
  3. Esse JSON entrou no histórico da sessão no SQLite e fez o modelo entrar em **loop**, repetindo a mesma saída para todas as mensagens seguintes.

### Trecho real observado
```text
Usuário:
import math
def area_circulo(r):
    return math.pi * (r**2)

Agente:
{"name": "area_circulo", "parameters": {"r": "5"}}

Usuário: onde paramos?
Agente: {"name": "area_circulo", "parameters": {"r": "5"}}

Usuário: /fim
Agente: {"name":"area_circulo","parameters":{"r":5}}

Usuário: me ensine
Agente: {"name":"area_circulo","parameters":{"r":5}}
```

- **Causa raiz:** Limitação de *tool calling* em modelos locais muito pequenos (3B) sob contexto composto (Time + delegação entre 3 membros + tools da sandbox), agravada pela contaminação do histórico da sessão.
- **Mitigação / comparação:** Usar modelos com suporte mais robusto a *tool calling* (ex.: Claude via `anthropic:claude-sonnet-4-5`, Groq 70B ou `ollama:qwen2.5:7b`) e comparar o comportamento nos mesmos cenários na Fase 4.

---

## Falha 2 — Violação de restrição numérica na saída estruturada (`horas_estimadas = 0`)

- **Data:** 25/11/2026
- **Modelo:** `ollama:llama3.2` (3B)
- **Contexto:** Chamada `GET /contrato/resultado/{id_sessao}` via Swagger (`/docs`).
- **O que aconteceu:** O `extrator_plano` gerou JSON sintaticamente válido com 6 tópicos, mas preencheu `horas_estimadas: 0` em todos eles, disparando 6 erros de validação Pydantic (`Input should be greater than 0`) e HTTP 500 na primeira versão.
- **Mitigação implementada em código:**
  - Captura de `ValidationError` dentro do loop `_gerar_verificado()` em `src/tutor_estudos/servico.py`, reenviando os erros exatos de volta ao extrator para autocorreção (e devolvendo HTTP 422 limpo caso esgote as tentativas).
  - Reforço explícito nas instruções do `extrator_plano` indicando valores positivos (`4.0`, `6.0`, `8.0`, nunca `0`).
  - Adicionado teste de regressão `test_retry_quando_llm_devolve_horas_zero` em `tests/test_modulo.py`.

---

## Falha 3 — Alucinação de data, habilidades fora das lacunas e extração indevida de exercício

- **Data:** 25/11/2026
- **Modelo:** `ollama:llama3.2` (3B)
- **Contexto:** Primeira geração de `saidas/f01/plano_estudos.json` e `saidas/f01/registro_progresso.json` (antes da camada `fidelidade.py`).
- **O que aconteceu:**
  1. **Data alucinada:** o extrator gravou `"data": "2023-03-01T10:00:00Z"` na sessão de estudo (ano 2023).
  2. **Habilidades fora das lacunas:** incluiu tópicos de `SQL` e `Python` no plano de `f01`, embora as lacunas de `f01` fossem apenas `Power BI` e `Apache Airflow`, além de somar as horas dos tópicos (`37.0`) no campo `horas_semanais`.
  3. **Falso exercício:** classificou a mensagem de despedida do tutor (*"Você tem certeza de que quer sair dessa aula..."*) como um `Exercicio` discursivo com `correto: null`.
- **Mitigação implementada em código:**
  - Remoção do campo `data` de `RascunhoSessao`; a data real da sessão passou a ser gerada exclusivamente em código Python (`src/tutor_estudos/calculos.py`).
  - Criação da verificação determinística `src/tutor_estudos/fidelidade.py` (`verificar_plano` e `verificar_progresso`) com loop de correção automática em `servico.py`, rejeitando habilidades fora de `Lacunas`, `horas_semanais` irreais e habilidades adquiridas sem evidência real.
