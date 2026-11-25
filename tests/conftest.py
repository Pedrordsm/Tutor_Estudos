"""Fixtures de teste com modelo roteirizado (sem acesso à rede ou LLM real)."""

import json
from dataclasses import dataclass, field

import pytest
from agno.db.sqlite import SqliteDb
from agno.models.base import Model
from agno.models.response import ModelResponse

from carreira_contratos import Curriculo, Lacunas, novo_cabecalho
from carreira_contratos.modelos import DadosPessoais, Habilidade, Lacuna
from tutor_estudos.servico import ServicoTutor


@dataclass
class ModeloRoteirizado(Model):
    id: str = "roteirizado"
    name: str = "ModeloRoteirizado"
    provider: str = "teste"
    respostas: list = field(default_factory=list)
    chamadas: int = 0

    def invoke(self, *args, **kwargs):
        self.chamadas += 1
        texto = self.respostas.pop(0) if self.respostas else "Sem resposta roteirizada."
        return ModelResponse(role="assistant", content=texto)

    async def ainvoke(self, *args, **kwargs):
        return self.invoke()

    def invoke_stream(self, *args, **kwargs):
        yield self.invoke()

    async def ainvoke_stream(self, *args, **kwargs):
        yield self.invoke()

    def _parse_provider_response(self, response, **kwargs):
        return response

    def _parse_provider_response_delta(self, response):
        return response


@pytest.fixture
def curriculo_ficticio() -> Curriculo:
    return Curriculo(
        cabecalho=novo_cabecalho("tutor_curriculos", "f01"),
        dados_pessoais=DadosPessoais(
            nome="Ana Silva",
            email="ana.ficticio@exemplo.edu.br",
            cidade="Serra",
        ),
        habilidades=[
            Habilidade(nome="Power BI", categoria="ferramenta", nivel="basico", evidencias=["Disciplina de BI"]),
            Habilidade(nome="SQL", categoria="tecnica", nivel="intermediario", evidencias=["Monitoria de BD"]),
        ],
    )


@pytest.fixture
def lacunas_ficticias() -> Lacunas:
    return Lacunas(
        cabecalho=novo_cabecalho("radar_vagas", "f01"),
        id_vaga_alvo="vf01",
        itens=[
            Lacuna(
                habilidade="Power BI",
                nivel_atual="basico",
                nivel_necessario="intermediario",
                prioridade="alta",
                obrigatoria=True,
                frequencia=1,
                vagas_relacionadas=["vf01"],
            ),
            Lacuna(
                habilidade="Apache Airflow",
                nivel_atual="nenhum",
                nivel_necessario="basico",
                prioridade="baixa",
                obrigatoria=False,
                frequencia=1,
                vagas_relacionadas=["vf01"],
            ),
        ],
    )


def json_rascunho_plano(
    *,
    horas_semanais: float = 6.0,
    incluir_power_bi: bool = True,
    habilidade_extra: str | None = None,
    prerequisito_invalido: str | None = None,
) -> str:
    topicos = []
    if incluir_power_bi:
        topicos.append({
            "habilidade": "Power BI",
            "titulo": "Modelagem de dados no Power BI",
            "objetivos": ["Criar esquema estrela"],
            "prerequisitos": [],
            "horas_estimadas": 6.0,
            "atividades": ["Modelar base fictícia de vendas"],
            "projeto_pratico": "Painel de entregas fictícias",
            "situacao": "em_andamento",
        })
    topicos.append({
        "habilidade": "Apache Airflow",
        "titulo": "Introdução a DAGs no Airflow",
        "objetivos": ["Criar uma DAG simples"],
        "prerequisitos": [prerequisito_invalido] if prerequisito_invalido else [],
        "horas_estimadas": 6.0,
        "atividades": ["Agendar extração simples"],
        "projeto_pratico": None,
        "situacao": "pendente",
    })
    if habilidade_extra:
        topicos.append({
            "habilidade": habilidade_extra,
            "titulo": f"Tópico inventado de {habilidade_extra}",
            "objetivos": ["Aprender algo fora das lacunas"],
            "prerequisitos": [],
            "horas_estimadas": 4.0,
            "atividades": ["Atividade"],
            "projeto_pratico": None,
            "situacao": "pendente",
        })
    return json.dumps({"horas_semanais": horas_semanais, "topicos": topicos}, ensure_ascii=False)


def json_rascunho_progresso(*, evidencias: list[str] | None = None, exercicio_correto: bool = True) -> str:
    evs = ["Exercício resolvido corretamente na sessão de Power BI"] if evidencias is None else evidencias
    return json.dumps({
        "sessoes": [
            {
                "topico": "Modelagem de dados no Power BI",
                "resumo_explicacao": "Diferença entre tabela fato e tabela dimensão.",
                "exercicios": [
                    {
                        "enunciado": "Itens vendidos é fato ou dimensão?",
                        "tipo": "discursiva",
                        "resposta_formando": "Fato, pois registra eventos numéricos.",
                        "correto": exercicio_correto,
                        "feedback": "Correto!" if exercicio_correto else "Revise o conceito de fato.",
                    },
                    {
                        "enunciado": "Qual a cardinalidade entre Produto e Vendas?",
                        "tipo": "objetiva",
                        "resposta_formando": "Muitos para muitos",
                        "correto": False,
                        "feedback": "É um para muitos.",
                    },
                ],
            }
        ],
        "habilidades_adquiridas": [
            {
                "nome": "Modelagem dimensional",
                "categoria": "tecnica",
                "nivel": "basico",
                "evidencias": evs,
            }
        ],
        "ajustes_plano": ["Revisar cardinalidade na próxima sessão."],
    }, ensure_ascii=False)


@pytest.fixture
def fabrica(tmp_path):
    def criar(*respostas, tentativas_fidelidade: int = 2):
        modelo = ModeloRoteirizado(respostas=list(respostas))
        servico = ServicoTutor(
            modelo,
            SqliteDb(db_file=str(tmp_path / "tutor_teste.db")),
            tentativas_fidelidade=tentativas_fidelidade,
        )
        return servico, modelo

    return criar
