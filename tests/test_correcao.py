"""Testes da correção de SQL em código e do plano direto."""

from tutor_estudos.servico import ServicoTutor

from conftest import json_rascunho_plano

SETUP = (
    "CREATE TABLE clientes (id INTEGER, nome TEXT); CREATE TABLE pedidos (id INTEGER, cliente_id INTEGER, valor REAL);"
    "INSERT INTO clientes VALUES (1, 'Ana'), (2, 'Bruno'); INSERT INTO pedidos VALUES (1, 1, 100.0);"
)
REFERENCIA = "SELECT c.nome, COALESCE(SUM(p.valor), 0) FROM clientes c LEFT JOIN pedidos p ON p.cliente_id = c.id GROUP BY c.id, c.nome;"


def test_correcao_sql_em_codigo():
    # e07 do kit (LEFT JOIN, correta) e e08 (INNER JOIN, perde o cliente sem pedidos)
    e07 = ServicoTutor._avaliar_sql("Q", "SELECT c.nome, COALESCE(SUM(p.valor), 0) AS total FROM clientes c "
                                         "LEFT JOIN pedidos p ON p.cliente_id = c.id GROUP BY c.id, c.nome;", SETUP, REFERENCIA)
    e08 = ServicoTutor._avaliar_sql("Q", "SELECT c.nome, SUM(p.valor) FROM clientes c JOIN pedidos p "
                                         "ON p.cliente_id = c.id GROUP BY c.nome;", SETUP, REFERENCIA)
    quebrada = ServicoTutor._avaliar_sql("Q", "SELECT nada FROM tabela_inexistente;", SETUP, REFERENCIA)
    destrutiva = ServicoTutor._avaliar_sql("Q", "DROP TABLE clientes;", SETUP, REFERENCIA)
    assert e07.correto is True
    assert e08.correto is False and "Bruno" in e08.feedback
    assert quebrada.correto is False and destrutiva.correto is False


def test_avaliar_exercicio_sql_nao_chama_modelo(fabrica):
    servico, modelo = fabrica()
    ex = servico.avaliar_exercicio("Q", "codigo", REFERENCIA, sql_setup=SETUP, sql_referencia=REFERENCIA)
    assert ex.correto is True and modelo.chamadas == 0


def test_planejar_direto_com_retry(fabrica, lacunas_ficticias, curriculo_ficticio):
    servico, modelo = fabrica(json_rascunho_plano(habilidade_extra="Rust"), json_rascunho_plano())
    plano = servico.planejar(lacunas_ficticias, curriculo_ficticio, 6)
    assert {t.habilidade for t in plano.topicos} == {"Power BI", "Apache Airflow"}
    assert modelo.chamadas == 2
