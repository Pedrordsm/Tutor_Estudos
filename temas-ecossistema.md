Instituto Federal do Espírito Santo — Campus Serra · Bacharelado em Sistemas de Informação · Inteligência Artificial · Prof. Sérgio Nery Simões

# Trabalho Prático: Ecossistema de Agentes “Do diploma ao primeiro emprego”

*Apresentação dos temas para escolha dos grupos — versão preliminar*

## A proposta

A turma vai construir, em conjunto, um ecossistema de agentes de inteligência artificial que apoia o estudante de Sistemas de Informação na transição da graduação para o mercado de trabalho: da escolha da área de atuação à integração no primeiro emprego. Cada grupo desenvolve um módulo do ecossistema, um sistema de agentes em Python com a biblioteca Agno.

Os módulos se comunicam por contratos de dados: cada um recebe e produz arquivos JSON em formatos definidos pelo professor. Por isso, cada grupo trabalha de forma independente, usando arquivos de entrada fictícios fornecidos no kit do trabalho, sem depender do andamento dos outros grupos. Ao final, os módulos poderão ser encadeados num único sistema.

## O fluxo do ecossistema

**Jornada do formando**

```
1 Orientador de carreira → 2 Tutor de currículos → 3 Radar de vagas → 4 Tutor de estudos → 5 Preparador de entrevistas → 6 Mentor de integração
```

- **1 — Orientador de carreira:** escolhe a área e o cargo
- **2 — Tutor de currículos:** monta o currículo
- **3 — Radar de vagas:** compara currículo e vagas, aponta lacunas
- **4 — Tutor de estudos:** ensina o que falta
- **5 — Preparador de entrevistas:** prepara e simula a entrevista
- **6 — Mentor de integração:** apoia os primeiros dias no emprego

**Módulos laterais (usam o currículo e a vaga escolhida)**

- 7 — Redator de carta de apresentação
- 8 — Revisor de portfólio no GitHub
- 9 — Consultor de perfil no LinkedIn

Documentos que circulam entre os módulos: perfil de carreira, currículo, conjunto de vagas e vaga escolhida, relatório de aderência, lacunas, plano de estudos e progresso, plano de preparação e relatório de entrevista, plano de integração, carta, relatório de portfólio e relatório de perfil.

## Regras gerais

- **Grupos:** formação livre; cada tema tem um número máximo de alunos, indicado na tabela.
- **Duração prevista:** de 3 a 4 semanas.
- **Entregas:** código em repositório privado no GitHub, relatório em Typst (modelo fornecido) e apresentação de 15 minutos com demonstração e arguição.
- **Uso de IA:** recomendado neste trabalho; todos os membros do grupo devem entender e saber explicar o código na arguição.
- **Arquitetura comum:** agentes do Agno servidos pelo AgentOS, execução pela linha de comando e pela interface gráfica do AgentOS.
- **Contratos:** entradas e saídas seguem exatamente os formatos do kit e passam no validador fornecido.
- **Dados fictícios:** nenhum dado pessoal real é usado no desenvolvimento ou nos testes.
- **Fidelidade:** nenhum módulo pode atribuir ao formando informações que ele não forneceu.
- **Avaliação experimental:** cada grupo testa o seu módulo com casos de teste e mede a qualidade dos resultados.

## Os temas

| Nº | Tema | O que o sistema deve fazer | Entrada → Saída | Recursos do Agno | Máx. de alunos |
|---|---|---|---|---|---|
| 1 | **Orientador de carreira**<br>*conversacional* | Conversa com o formando sobre interesses, disciplinas, projetos e preferências; consulta um catálogo de áreas de TI; recomenda de 3 a 5 áreas com compatibilidade e justificativa; responde dúvidas e compara áreas; registra a área, o cargo e o nível escolhidos. | Conversa → perfil de carreira | Base de conhecimento (RAG), memória, saída estruturada | 4 |
| 2 | **Tutor de currículos**<br>*conversacional* | Entrevista o formando e monta o currículo; importa um currículo antigo; um agente revisor aponta frases vagas e sugere melhorias; adapta o currículo a uma vaga; exporta em Markdown e Typst; nunca acrescenta informação que o formando não forneceu. | Conversa (e perfil de carreira) → currículo | Time de agentes, memória, histórico de versões, guardrail de fidelidade | 5 |
| 3 | **Radar de vagas**<br>*processamento* | Lê o currículo e um arquivo com várias vagas; extrai e normaliza os requisitos; calcula em código a nota de aderência de cada vaga; ranqueia e indica a vaga mais adequada; lista as habilidades que faltam, priorizadas; explica o resultado em conversa. | Currículo e vagas → relatório de aderência e lacunas | Workflow, extração estruturada, tools próprias | 5 |
| 4 | **Tutor de estudos**<br>*conversacional* | Recebe as lacunas, faz um diagnóstico e monta um plano de estudos com prazos; dá aulas, aplica e corrige exercícios (inclusive de código, executado em ambiente isolado); ajusta o plano ao desempenho; registra as habilidades adquiridas com evidência. | Lacunas e currículo → plano de estudos e registro de progresso | Time de agentes, memória, execução de código, saída estruturada | 5 |
| 5 | **Preparador de entrevistas**<br>*conversacional* | Modo preparação: analisa a vaga, lista perguntas prováveis, ajuda o formando a montar respostas com as próprias experiências, indica tópicos a revisar. Modo simulação: conduz a entrevista, ajusta a dificuldade e avalia por rubrica, com nota por competência e feedback. | Vaga e currículo → plano de preparação e relatório de entrevista | Time de agentes, memória entre sessões, rubrica, saída estruturada | 5 |
| 6 | **Mentor de integração**<br>*conversacional* | Depois da contratação, compara o perfil do formando com o cargo descrito nos documentos de uma empresa fictícia; monta um plano semanal de integração; explica processos e termos citando o documento de origem; admite quando a resposta não está nos documentos. | Currículo, vaga e documentos da empresa → plano de integração | Base de conhecimento (RAG) com citação, time de agentes, memória | 5 |
| 7 | **Redator de carta de apresentação**<br>*processamento* | Escreve uma carta personalizada para uma vaga, ligando cada requisito a um item real do currículo; um revisor confere fidelidade, tom e tamanho; permite ajustes (mais formal, versão curta, em inglês). | Currículo e vaga → carta de apresentação | Workflow com laço de revisão, saída estruturada | 3 |
| 8 | **Revisor de portfólio no GitHub**<br>*processamento* | Analisa os repositórios do formando (localmente ou pela API do GitHub); verifica em código README, licença, dependências e testes; avalia a qualidade com o modelo; indica os repositórios a destacar, sugere melhorias e gera READMEs. | Lista de repositórios e currículo → relatório de portfólio | Workflow, tools próprias, saída estruturada | 4 |
| 9 | **Consultor de perfil no LinkedIn**<br>*processamento* | A partir do texto do perfil colado pelo formando (sem acesso automatizado ao site), avalia cada seção, aponta divergências com o currículo, sugere palavras-chave e novas versões de título e resumo, e refina as sugestões em conversa. | Texto do perfil e currículo → relatório de perfil | Agentes consultor e verificador, memória, saída estruturada | 3 |

**Conversacional:** o formando interage com o agente em conversa; **processamento:** o módulo recebe arquivos e produz o resultado, com conversa opcional para explicá-lo.

**Fornecido no kit:** pacote de contratos com os formatos de todos os documentos, validador, arquivos de três formandos fictícios, módulo de exemplo com a arquitetura completa e os insumos de cada tema (catálogo de áreas, conjunto de vagas, documentos da empresa fictícia, repositórios de exemplo e perfis).
