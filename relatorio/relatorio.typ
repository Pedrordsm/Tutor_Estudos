#import "modelo_ifes.typ": report, box-info, box-tip, box-warning, styled-table

#let figuras-prontas = false
#let provisoria(rotulo) = rect(width: 100%, height: 5cm, stroke: (dash: "dashed", paint: luma(150)), align(center + horizon, text(fill: luma(120))[Figura provisória: #rotulo]))

#show: report.with(
  title: "Ecossistema de Agentes: Módulo 4 — Tutor de estudos",
  subtitle: "Relatório do trabalho prático",
  author: ("Kaio", "Samiya", "Pedro Renã", "Tertuliano", "Heitor"),
  cover-authors: [Kaio (matrícula) \ Samiya (matrícula) \ Pedro Renã (matrícula) \ Tertuliano (matrícula) \ Heitor (matrícula)],
  professor: "Dr. Sérgio Nery Simões",
  course: "Inteligência Artificial",
)

#box-warning(title: "Rascunho")[
  Preencham os nomes completos e as matrículas na capa, troquem cada *[preencher]* pelos números da avaliação e apaguem esta caixa antes de compilar a versão final.
]

= Introdução

O Módulo 4 do ecossistema "Do diploma ao primeiro emprego" transforma as lacunas de um formando em um plano de estudos e atua como professor particular até que ele domine os tópicos. Ele recebe o documento `Lacunas`, produzido pelo Radar de vagas (Módulo 3), e o `Curriculo`, produzido pelo Tutor de currículos (Módulo 2), e produz o `PlanoEstudos` e o `RegistroProgresso`.

O módulo foi implementado em Python com a biblioteca Agno @agno, como um time de três agentes servido pelo AgentOS, com rotas do contrato, linha de comando, memória em SQLite, execução isolada de código e verificação determinística de fidelidade. [preencher: resumo dos principais resultados da avaliação.]

= Arquitetura do módulo

O núcleo é um `Team` do Agno com três agentes especializados, sugeridos no caderno do módulo: o *Planejador* conduz o diagnóstico, monta e adapta o plano; o *Professor* dá as aulas; o *Avaliador* aplica e corrige exercícios. O time coordenador recebe as lacunas e o currículo no estado da sessão (`session_state`), delega cada pedido ao especialista adequado e guarda sessões, histórico e memória num banco SQLite, o que permite retomar a conversa de onde parou (F8).

As saídas não são escritas diretamente pelo time. Ao final da conversa, dois agentes extratores, com saída estruturada (Pydantic), leem a conversa e produzem rascunhos do plano e do progresso. Os rascunhos passam pela verificação de fidelidade em código (`fidelidade.py`); se houver problema (habilidade fora das lacunas, lacuna de prioridade alta sem tópico, pré-requisito inexistente, habilidade adquirida sem evidência), os problemas são devolvidos ao extrator para correção, em até duas tentativas. Só então o código monta os documentos oficiais do contrato, calculando cabeçalho, ordem dos tópicos, data prevista de conclusão e desempenho de cada sessão (`calculos.py`).

A divisão entre código e modelo segue o princípio de cálculo em código do enunciado: o modelo de linguagem explica, propõe exercícios e redige; o código calcula datas, ordem e desempenho, executa e corrige exercícios de Python (testes com `assert` ou funções `test_*`) e de SQL (comparação do resultado com uma consulta de referência num SQLite em memória) e valida todas as saídas contra os modelos do contrato.

A execução de código do formando é isolada: processo separado em modo `-I`, pasta temporária, ambiente sem variáveis do sistema (as chaves de API não chegam ao código), limite de tempo e bloqueio, por análise da árvore sintática, de módulos de sistema e rede e de chamadas como `open`, `eval` e `exec`. As chamadas ao modelo usam novas tentativas com espera exponencial, o que trata o erro HTTP 429.

#figure(
  if figuras-prontas { image("figuras/arquitetura.png", width: 100%) } else { provisoria("arquitetura do módulo") },
  caption: [Arquitetura do módulo.],
) <fig-arquitetura>

#figure(
  kind: table,
  styled-table(
    col-widths: (auto, 1fr, 1fr, auto),
    headers: ([Agente], [Papel], [Tools e recursos], [Saída estruturada]),
    rows: (
      ([Time coordenador], [Delega ao especialista e mantém o contexto da sessão], [Memória e histórico em SQLite, `session_state`], [—]),
      ([Planejador], [Diagnóstico (F1), plano (F2), adaptação (F5), projetos (F6)], [—], [—]),
      ([Professor], [Aulas em sessões (F3)], [—], [—]),
      ([Avaliador], [Exercícios e correção (F4), evidências (F7)], [`executar_codigo_python`, `executar_sql_em_memoria`], [—]),
      ([Extrator do plano], [Extrai o plano da conversa], [Verificação de fidelidade com nova tentativa], [`RascunhoPlano`]),
      ([Extrator do progresso], [Extrai sessões, exercícios e habilidades], [Verificação de evidência com nova tentativa], [`RascunhoProgresso`]),
      ([Corretor estruturado], [Corrige respostas discursivas e objetivas], [—], [`AvaliacaoExercicio`]),
    ),
  ),
  caption: [Agentes do módulo.],
) <tab-agentes>

= Contrato de entradas e saídas

O módulo usa o identificador `tutor_estudos`. As entradas obrigatórias são `Lacunas` e `Curriculo`, lidas e identificadas com o pacote `carreira_contratos` do kit; as saídas são `PlanoEstudos` e `RegistroProgresso`, construídas com os modelos Pydantic do mesmo pacote, o que garante que nada fora do contrato é gravado ou devolvido. A rota `POST /contrato/iniciar` recebe `{"lacunas": ..., "curriculo": ...}` e devolve o identificador da sessão e a primeira mensagem; a conversa continua pelas rotas do AgentOS ou pela interface gráfica; `GET /contrato/resultado/{id_sessao}` devolve `{"plano_estudos": ..., "registro_progresso": ...}`, com erro 404 para sessão inexistente e 422 quando a saída não passa na verificação de fidelidade. Os testes automatizados conferem as rotas e passam as saídas pelo verificador do kit.

#figure(
  kind: table,
  styled-table(
    col-widths: (auto, 1fr, auto, auto),
    headers: ([Formando], [Arquivos de entrada], [Validador], [Verificador]),
    rows: (
      ([f01], [`exemplos/f01/lacunas.json`, `exemplos/f01/curriculo.json`], [[preencher]], [[preencher]]),
      ([f02], [`exemplos/f02/lacunas.json`, `exemplos/f02/curriculo.json`], [[preencher]], [[preencher]]),
      ([f03], [`exemplos/f03/lacunas.json`, `exemplos/f03/curriculo.json`], [[preencher]], [[preencher]]),
    ),
  ),
  caption: [Conformidade das saídas com o contrato.],
) <tab-contrato>

= Funcionalidades implementadas

#figure(
  kind: table,
  styled-table(
    col-widths: (auto, 1fr, auto, 1fr),
    headers: ([Nº], [Funcionalidade], [Situação], [Observação]),
    rows: (
      ([F1], [Diagnóstico inicial com perguntas rápidas], [Completa], [Primeira mensagem da sessão lista as lacunas e pergunta a disponibilidade e o nível.]),
      ([F2], [Plano priorizado com pré-requisitos e datas], [Completa], [Datas calculadas em código; cobertura de prioridade alta verificada.]),
      ([F3], [Aulas em sessões], [Completa], [Agente Professor.]),
      ([F4], [Exercícios com correção, inclusive de código], [Completa], [Python e SQL corrigidos em código; DAX e discursivas pelo modelo.]),
      ([F5], [Adaptação ao desempenho], [[preencher]], [Ajustes registrados em `ajustes_plano`; conferir nos casos A01 e A02.]),
      ([F6], [Sugestão de projetos práticos], [Completa], [Campo `projeto_pratico` dos tópicos.]),
      ([F7], [Progresso com evidências], [Completa], [Habilidade adquirida sem evidência é rejeitada em código.]),
      ([F8], [Memória entre sessões], [Completa], [SQLite; retomada com `--sessao` ou pela interface.]),
    ),
  ),
  caption: [Situação das funcionalidades.],
) <tab-funcionalidades>

= Avaliação experimental

O conjunto tem 36 casos, em `casos_teste/casos.json`, com o resultado esperado de cada um registrado em 26/11/2026, antes da execução. Os casos C01–C20 usam as 20 respostas simuladas do kit, que o grupo classificou antes como corretas (10) ou incorretas (10); os casos P01–P04 pedem planos para os três formandos com disponibilidades diferentes; A01–A02 simulam um formando com baixo desempenho; S01–S06 testam a execução isolada; G01–G04 testam os guardrails de fidelidade e evidência.

As métricas seguem o caderno: *acerto do avaliador* (casos em que o veredito coincide com o gabarito, sobre o total); *qualidade do plano* (fração dos planos que cobrem todas as lacunas de prioridade alta, usam só habilidades das lacunas, respeitam pré-requisitos e têm data de conclusão coerente com a disponibilidade); *adaptação* (fração dos casos em que o plano foi ajustado); e *qualidade das explicações*, por amostragem, com a rubrica de `casos_teste/rubrica_explicacoes.md`. O script `casos_teste/executar_casos.py` executa os casos e calcula as métricas.

#figure(
  kind: table,
  styled-table(
    col-widths: (1fr, auto, auto),
    headers: ([Métrica], [Casos], [Resultado]),
    rows: (
      ([Acerto do avaliador na correção], [20], [[preencher]]),
      ([Planos que cumprem todos os critérios], [4], [[preencher]]),
      ([Adaptação após baixo desempenho], [2], [[preencher]]),
      ([Execução isolada bloqueia código perigoso e laço infinito], [6], [6/6 (100%)]),
      ([Guardrails de fidelidade e evidência], [4], [4/4 (100%)]),
      ([Qualidade das explicações (rubrica, 0 a 10)], [6 aulas], [[preencher]]),
    ),
  ),
  caption: [Resultados da avaliação experimental.],
) <tab-resultados>

[preencher: modelo de linguagem usado (provedor e nome), data da execução e interpretação dos resultados. Opcional, com bônus: repetir com um segundo modelo e comparar.]

= Análise de falhas

Durante o desenvolvimento, com o modelo local `llama3.2` (3B), foram observadas três falhas, registradas em `relatorio/anotacoes_falhas.md`:

- *Chamada incorreta de tool e laço no histórico.* Ao receber uma função do formando, o modelo tratou o nome da função como uma tool, devolveu um JSON cru como resposta e, com esse JSON no histórico da sessão, passou a repeti-lo em todas as mensagens seguintes. Causa provável: suporte fraco a tool calling em modelos pequenos, num contexto com time, delegação e tools. Mitigação: usar modelos com tool calling mais robusto.
- *Restrição numérica violada na saída estruturada.* O extrator preencheu `horas_estimadas = 0` em todos os tópicos, o que gerava erro 500. Mitigação: o erro de validação passou a ser devolvido ao extrator para correção, com resposta 422 se as tentativas se esgotarem, e um teste de regressão.
- *Alucinação de data e de habilidades.* O extrator gravou uma data de 2023 na sessão, criou tópicos de SQL e Python que não estavam nas lacunas de f01 e confundiu a soma das horas com a disponibilidade semanal. Mitigação: a data passou a ser calculada em código e a verificação de fidelidade passou a rejeitar habilidades fora das lacunas e disponibilidade irreal. A auditoria dos casos de teste detectou que as saídas de f01 geradas antes dessa correção ainda continham os tópicos indevidos. [preencher: confirmar que foram geradas novamente com o comando `simular`.]

[preencher: falhas observadas na execução dos casos de teste.]

= Uso de ferramentas de IA no desenvolvimento

[preencher: quais assistentes de IA foram usados (por exemplo, Claude Code), em que partes (estrutura do repositório, código, casos de teste, revisão) e como o resultado foi conferido (testes automatizados, verificador e conferidor do kit, leitura do código por todos os membros).]

= Conclusão

[preencher: o que o módulo faz bem, limitações (exercícios DAX corrigidos só pelo modelo; dependência da qualidade do modelo em tool calling; datas das sessões iguais ao momento da extração), o que o grupo aprendeu e trabalhos futuros.]

#bibliography("referencias.bib", style: "associacao-brasileira-de-normas-tecnicas", title: "Referências")
