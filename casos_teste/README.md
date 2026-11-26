# Casos de teste — Módulo 4 (Tutor de estudos)

Os resultados esperados estão em [`casos.json`](casos.json) e foram **definidos antes da execução** do sistema (registro em 26/11/2026), como pede o enunciado (seção 4).

| Bloco | Casos | Origem | Métrica (caderno, seção 10) | Corrigido por |
|---|---|---|---|---|
| Correção | C01–C20 | 20 respostas simuladas do kit (`insumos/m4_tutor_estudos/respostas_simuladas.json`); gabarito do grupo | Acerto do avaliador = casos em que o veredito do sistema coincide com o gabarito / total | Código (sandbox Python e SQL em memória) em C07, C08, C12–C16; modelo nos demais |
| Planos | P01–P04 | Lacunas e currículos de f01, f02 e f03 do kit, com disponibilidades diferentes | Plano cobre todas as lacunas de prioridade alta, só usa habilidades das lacunas, respeita pré-requisitos e a disponibilidade (data de conclusão coerente com horas totais / horas semanais) | Código, sobre o plano gerado pelo modelo |
| Adaptação | A01–A02 | Roteiros f01 e f03 (o formando erra e pede revisão) | O `RegistroProgresso` registra ajuste no plano | Código, sobre as saídas de `simular` |
| Segurança | S01–S06 | Próprios | Código perigoso é bloqueado e laço infinito é interrompido | Código |
| Guardrails | G01–G04 | Próprios | Plano com habilidade inventada, sem lacuna alta ou habilidade sem evidência é rejeitado | Código |

A qualidade das explicações é avaliada por amostragem com a [rubrica](rubrica_explicacoes.md), lendo as transcrições em `saidas/fXX/transcricao.md`.

## Como executar

Na raiz do repositório, com o kit na pasta vizinha `../kit-ecossistema`:

```bash
# 1) Só o que é corrigido em código (não precisa de chave de API)
python casos_teste/executar_casos.py --kit ../kit-ecossistema --sem-llm

# 2) Gera as saídas dos três formandos (duas sessões cada, roteiros em casos_teste/roteiros/)
python -m tutor_estudos simular --roteiro casos_teste/roteiros/f01.json --kit ../kit-ecossistema --saida-dir saidas/f01
python -m tutor_estudos simular --roteiro casos_teste/roteiros/f02.json --kit ../kit-ecossistema --saida-dir saidas/f02
python -m tutor_estudos simular --roteiro casos_teste/roteiros/f03.json --kit ../kit-ecossistema --saida-dir saidas/f03

# 3) Todos os casos, com o modelo configurado no .env (MODELO_LLM)
python casos_teste/executar_casos.py --kit ../kit-ecossistema
```

Cada execução grava `resultados/<modelo>.json` (detalhe de cada caso) e `resultados/<modelo>.md` (tabela de métricas e auditoria das saídas). Para a comparação entre dois modelos (bônus), troque `MODELO_LLM` no `.env` e rode o passo 3 de novo: cada modelo gera o seu arquivo.
