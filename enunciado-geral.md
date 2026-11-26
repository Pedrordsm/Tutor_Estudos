INTELIGÊNCIA ARTIFICIAL

# Trabalho Prático: Ecossistema de Agentes “Do diploma ao primeiro emprego”

## Enunciado geral

**Prof. Dr. Sérgio Nery Simões**

IFES — Campus Serra | 2026

---

## Sumário

1. A proposta ........................................................ 1
2. Como os módulos se conectam ..................................... 2
3. Requisitos comuns a todos os módulos ............................ 3
   - 3.1. Arquitetura .................................................. 3
   - 3.2. Requisitos técnicos .......................................... 4
   - 3.3. Princípios ................................................... 4
4. Avaliação experimental ........................................... 4
5. O kit do trabalho ................................................ 5
6. Checklist e conferência da entrega ............................... 5
7. Entregas e calendário ............................................ 6

---

## 1. A proposta

A turma vai construir, em conjunto, um ecossistema de agentes de inteligência artificial que apoia o estudante de Sistemas de Informação na transição da graduação para o mercado de trabalho: da escolha da área de atuação à integração no primeiro emprego. Cada grupo desenvolve um dos seis módulos do ecossistema, um sistema de agentes em Python com a biblioteca Agno.

Este enunciado traz o que vale para todos os grupos. O que é específico de cada módulo está no caderno do módulo e na ficha de contrato do módulo, que fica no kit do trabalho.

```
                                        ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
                                          conjunto de vagas do kit   [ConjuntoVagas]
                                        └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
                                                    ¦
                                                    ▼
┌─────────────────────┐                ┌─────────────────────┐                ┌─────────────────────┐                ┌─────────────────────┐
│ MÓDULO 1        (1) │ [PerfilCarreira]│ MÓDULO 2        (2) │  [Curriculo]   │ MÓDULO 3        (3) │  [Lacunas]     │ MÓDULO 4        (4) │
│ Orientador de       │ ──────────────►│ Tutor de            │ ─────────────► │ Radar de vagas      │  [Curriculo]   │ Tutor de            │
│ carreira            │                │ currículos          │                │                     │ ─────────────► │ estudos             │
│ conversacional + RAG│                │ conversacional      │                │ processamento       │                │ conversacional      │
└─────────────────────┘                └─────────────────────┘                └──────────┬──────────┘                └─────────────────────┘
                                                                                         │
                                                         [VagaAlvo] [Curriculo]          │
                                              ┌──────────────────────────────────────────┤
                                              │  vaga escolhida no ranking e currículo   │
                                              ▼                                          ▼
 ┌──────────────────────────┐      ┌─────────────────────┐                ┌─────────────────────┐        ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
 │ Legenda                  │      │ MÓDULO 5        (5) │                │ MÓDULO 6        (6) │          documentos da empresa
 │ ────── envio de documento│      │ Preparador de       │                │ Mentor de           │ ◄─ ─ ─ ─  fictícia (Vértice)
 │ - - -  insumo do kit     │      │ entrevistas         │                │ integração          │        └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
 │ [Nome] documento JSON    │      │ conversacional      │                │ conversacional + RAG│
 └──────────────────────────┘      └─────────────────────┘                └─────────────────────┘
```

*Figura 1: Fluxo de documentos entre os módulos do ecossistema.*

| Nº | Módulo | O que o sistema deve fazer | Entrada → Saída |
|---|---|---|---|
| 1 | Orientador de carreira | Conversa com o formando sobre interesses, disciplinas, projetos e preferências; consulta um catálogo de áreas de TI; recomenda de 3 a 5 áreas com justificativa; registra a área, o cargo e o nível escolhidos. | Conversa → PerfilCarreira |
| 2 | Tutor de currículos | Entrevista o formando e monta o currículo; importa um currículo antigo; um revisor aponta frases vagas; adapta o currículo a uma vaga; exporta em Markdown e Typst; nunca acrescenta informação não fornecida. | Conversa (PerfilCarreira e VagaAlvo opcionais) → Curriculo |
| 3 | Radar de vagas | Lê o currículo e um conjunto de vagas; extrai e normaliza os requisitos; calcula em código a aderência de cada vaga; indica a vaga mais adequada; lista as habilidades que faltam, priorizadas. | Curriculo + ConjuntoVagas → RelatorioAderencia + Lacunas |
| 4 | Tutor de estudos | Recebe as lacunas e monta um plano de estudos com prazos; dá aulas, aplica e corrige exercícios, inclusive de código; ajusta o plano ao desempenho; registra as habilidades adquiridas com evidência. | Lacunas + Curriculo → PlanoEstudos + RegistroProgresso |
| 5 | Preparador de entrevistas | Prepara o formando para a entrevista de uma vaga (perguntas prováveis, respostas com as próprias experiências, tópicos a revisar) e simula a entrevista, com avaliação por rubrica. | VagaAlvo (+ Curriculo) → PlanoPreparacaoEntrevista + RelatorioEntrevista |
| 6 | Mentor de integração | Depois da contratação, compara o perfil com o cargo descrito nos documentos da empresa, monta um plano semanal de integração e explica processos citando a fonte. | Curriculo + VagaAlvo + documentos da empresa → PlanoIntegracao |

*Tabela 1: Os seis módulos do ecossistema.*

## 2. Como os módulos se conectam

Os módulos se comunicam por documentos JSON com formato fixo, os contratos de dados. Cada módulo recebe documentos de entrada e produz documentos de saída, como mostram as setas da Figura 1. Durante o desenvolvimento, nenhum grupo depende de outro: as entradas vêm dos arquivos fictícios do kit. Se todos os grupos seguirem os contratos à risca, os módulos poderão ser encadeados depois sem adaptações.

Cada grupo usa apenas os documentos marcados na coluna do seu módulo na Tabela 2.

| Documento | M1 | M2 | M3 | M4 | M5 | M6 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `PerfilCarreira` | S | (E) | (E) | | | |
| `Curriculo` | | S | E | E | (E) | E |
| `ConjuntoVagas` | | | E | | | |
| `VagaAlvo` | | (E) | | | E | E |
| `RelatorioAderencia` | | | S | | | |
| `Lacunas` | | | S | E | | |
| `PlanoEstudos` | | | | S | | |
| `RegistroProgresso` | | | | S | | |
| `PlanoPreparacaoEntrevista` | | | | | S | |
| `RelatorioEntrevista` | | | | | S | |
| `PlanoIntegracao` | | | | | | S |

*Tabela 2: Documentos usados por módulo. E: entrada obrigatória; (E): entrada opcional; S: saída.*

Todo documento começa com um campo `cabecalho`, que identifica a versão do contrato, o módulo que gerou o documento, a data e hora de geração e o formando. Os campos de cada documento estão descritos na ficha de contrato do módulo.

Nas rotas do contrato, o corpo da requisição é um objeto JSON cujas chaves são os nomes dos documentos de entrada em minúsculas com sublinhado (por exemplo, `curriculo`, `vaga_alvo` e `conjunto_vagas`), mais `id_formando` quando nenhum documento de entrada é enviado. Quando o módulo produz mais de um documento, a resposta segue a mesma convenção (por exemplo, `relatorio_aderencia` e `lacunas`).

## 3. Requisitos comuns a todos os módulos

### 3.1. Arquitetura

- Os agentes, times e workflows do módulo são construídos com o Agno e servidos pelo AgentOS, o servidor do Agno.
- O módulo acrescenta ao AgentOS as rotas do contrato. Módulos de processamento expõem `POST /contrato/executar`, que recebe as entradas e devolve as saídas. Módulos conversacionais expõem `POST /contrato/iniciar`, que recebe as entradas e devolve o identificador da sessão, e `GET /contrato/resultado/{id_sessao}`, que devolve as saídas construídas a partir da conversa; a conversa acontece pelas rotas padrão do AgentOS ou pela interface gráfica.
- O módulo também funciona pela linha de comando, com os comandos `executar` (processamento), `conversar` (conversa no terminal) e `servir` (inicia o servidor).
- A interface gráfica é a do AgentOS: o painel os.agno.com, conectado ao servidor local, ou a Agent UI, de código aberto, executada pelo próprio grupo.
- Sessões, memória e histórico ficam num banco SQLite.

O módulo de exemplo do kit implementa toda essa arquitetura e serve de ponto de partida.

### 3.2. Requisitos técnicos

- A versão do Agno e das demais dependências é fixada no arquivo de dependências do projeto.
- Provedor e modelo de linguagem são configurados por variáveis de ambiente; o módulo funciona com pelo menos um provedor de camada gratuita.
- Chaves de API ficam em variáveis de ambiente: o repositório tem um arquivo `.env.exemplo`, e o `.env` fica fora dele.
- O módulo trata o erro de limite de requisições (HTTP 429), aguardando e tentando novamente.
- Toda saída é validada pelos modelos do contrato antes de ser gravada ou devolvida, e as saídas passam no validador e no verificador do kit.

### 3.3. Princípios

- **Fidelidade:** nenhum módulo pode atribuir ao formando informações que ele não forneceu (experiências, habilidades, níveis, resultados).
- **Dados fictícios:** nenhum dado pessoal real é usado no desenvolvimento ou nos testes.
- **Cálculo em código:** valores objetivos (notas de aderência, contagens, datas) são calculados por código; o modelo de linguagem extrai, redige e explica.
- **Transparência:** as recomendações vêm acompanhadas de justificativa, e as explicações baseadas em documentos citam a fonte.

## 4. Avaliação experimental

Além de funcionar, o módulo deve ser avaliado experimentalmente. Cada grupo monta um conjunto de pelo menos 20 casos de teste, a partir dos insumos do kit e de casos próprios, e define o resultado esperado de cada caso antes de executar o sistema. Os resultados são medidos com as métricas sugeridas no caderno do módulo, e o relatório analisa as falhas observadas, como alucinações, chamadas incorretas de tools e saídas incoerentes.

Opcionalmente, com bônus na nota, o grupo pode executar os mesmos casos de teste com dois modelos de linguagem diferentes (por exemplo, dois provedores gratuitos, ou um provedor gratuito e um modelo local) e comparar os resultados.

## 5. O kit do trabalho

| Pasta | Conteúdo |
|---|---|
| `fichas/` | A ficha de contrato de cada módulo, com as entradas, as saídas e os campos dos documentos usados. |
| `contratos/` | O pacote Python `carreira_contratos`, com os modelos dos documentos, o validador `carreira-validar` e o verificador `carreira-verificar`. |
| `esquemas/` | O JSON Schema de cada documento. |
| `exemplos/` | Documentos de três formandos fictícios, usados como entrada, e um exemplo de cada documento de saída. |
| `insumos/` | Arquivos de apoio de cada módulo, como o catálogo de áreas, o conjunto de vagas, a rubrica de entrevista e os documentos de uma empresa fictícia. |
| `modulo_exemplo/` | Um módulo mínimo com a arquitetura completa. |
| `relatorio/` | O modelo do relatório em Typst. |
| `checklists/` | O checklist de cada módulo, para copiar para o repositório como `CHECKLIST.md`. |
| `documentos/` | Este enunciado e os cadernos dos módulos, em PDF; cada caderno termina com o checklist do módulo. |

*Tabela 3: Conteúdo do kit do trabalho.*

> **Primeiros passos**
>
> 1. Ler este enunciado, o caderno do módulo, que termina com o checklist, e a ficha de contrato do módulo.
> 2. Instalar o pacote de contratos e rodar o validador e o verificador com os arquivos de exemplo.
> 3. Executar o módulo de exemplo e estudar a sua estrutura.
> 4. Criar o repositório privado do grupo no GitHub a partir dessa estrutura, copiar o checklist do módulo como `CHECKLIST.md` e começar pelo agente principal do módulo.

## 6. Checklist e conferência da entrega

Cada grupo recebe um checklist do seu módulo, com as tarefas em ordem, organizadas em quatro fases com datas, e um critério **Pronto quando** para cada tarefa. O checklist é a última seção do caderno do módulo, em página própria para poder ser impresso, e está também no kit, em `checklists/`, como arquivo Markdown: copiem-no para a raiz do repositório como `CHECKLIST.md` e marquem as tarefas à medida que forem concluídas.

| Fase | Data | Objetivo |
|---|---|---|
| 1 | 20/11/2026 (meta sugerida) | Preparar o ambiente e fazer o agente principal responder. |
| 2 | **27/11/2026** (apresentação parcial) | Contrato funcionando, saídas do formando f01 e demonstração parcial. |
| 3 | 04/12/2026 (meta sugerida) | Todas as funcionalidades, testes automatizados e saídas de f02 e f03. |
| 4 | **11/12/2026** (entrega final) | Avaliação experimental, relatório e apresentação. |

*Tabela 4: Fases do checklist.*

O repositório entregue segue esta estrutura; o código do módulo pode ser organizado como o grupo preferir:

```text
README.md         instalação, execução e limitações
pyproject.toml    ou requirements.txt, com o Agno fixado
.env.exemplo      variáveis de ambiente, sem as chaves
.gitignore        com a linha .env
CHECKLIST.md      o checklist do módulo, marcado
saidas/f01/       saídas geradas com as entradas do kit
saidas/f02/       (o mesmo para f02)
saidas/f03/       (o mesmo para f03)
casos_teste/      casos de teste e resultados esperados
relatorio/        relatorio.typ e relatorio.pdf
```

Antes de entregar, rodem o conferidor de entrega na pasta do repositório. Ele confere sozinho os arquivos obrigatórios, as chaves fora do repositório, as saídas dos três formandos, o tamanho do relatório e o progresso do checklist, e mostra ✅ ou ❌ em cada item, com uma dica para cada ❌:

```bash
pip install -e "caminho/do/kit/contratos[entrega]"
carreira-checar-entrega MODULO --kit caminho/do/kit
```

Troquem `MODULO` pelo identificador do módulo, que está na ficha de contrato (por exemplo, `radar_vagas`), e `caminho/do/kit` pelo caminho da pasta do kit.

## 7. Entregas e calendário

| Data | Entrega |
|---|---|
| **27/11/2026** | Apresentação do estado parcial: cada grupo mostra o módulo funcionando até onde conseguiu chegar e recebe considerações e sugestões de melhoria. |
| **11/12/2026** | Entrega final: código no repositório privado do grupo no GitHub, com acesso para o professor; relatório em Typst, feito a partir do modelo do kit, com até 12 páginas sem contar capa, sumário e referências; apresentação de 15 minutos com demonstração e arguição. |

*Tabela 5: Calendário do trabalho.*

O uso de assistentes de IA é recomendado neste trabalho. Todos os membros do grupo devem entender e saber explicar o código na arguição, e o relatório tem uma seção sobre as ferramentas de IA usadas.
