
import pytest

from app import criar_app
from app import db


@pytest.fixture
def app_teste(tmp_path, monkeypatch):
    banco_teste = tmp_path / "estoque_teste.db"

    monkeypatch.setattr(db, "DATABASE_PATH", banco_teste)

    app = criar_app()
    app.config.update(TESTING=True)

    with app.app_context():
        yield app


@pytest.fixture
def cliente(app_teste):
    return app_teste.test_client()


def obter_saldo(produto_id):
    with db.conexao_banco() as conexao:
        produto = conexao.execute(
            "SELECT quantidade_atual FROM produtos WHERE id = ?",
            (produto_id,),
        ).fetchone()

    return produto["quantidade_atual"]


def contar_movimentacoes(produto_id):
    with db.conexao_banco() as conexao:
        resultado = conexao.execute(
            "SELECT COUNT(*) AS total FROM movimentacoes WHERE produto_id = ?",
            (produto_id,),
        ).fetchone()

    return resultado["total"]


def test_cadastrar_produto_com_sucesso(app_teste):
    produto_id = db.cadastrar_produto(
        nome="Caderno universitário",
        quantidade_inicial=10,
        descricao="Caderno de teste",
        estoque_minimo=3,
    )

    assert produto_id > 0
    assert obter_saldo(produto_id) == 10
    assert contar_movimentacoes(produto_id) == 1


def test_nao_permite_cadastrar_produto_sem_nome(app_teste):
    with pytest.raises(ValueError, match="nome do produto"):
        db.cadastrar_produto(
            nome="   ",
            quantidade_inicial=5,
        )


def test_registrar_entrada_atualiza_saldo(app_teste):
    produto_id = db.cadastrar_produto("Caneta azul", 10)

    novo_saldo = db.registrar_movimentacao(
        produto_id,
        "ENTRADA",
        5,
        "Reposição",
    )

    assert novo_saldo == 15
    assert obter_saldo(produto_id) == 15
    assert contar_movimentacoes(produto_id) == 2


def test_registrar_saida_atualiza_saldo(app_teste):
    produto_id = db.cadastrar_produto("Borracha", 10)

    novo_saldo = db.registrar_movimentacao(
        produto_id,
        "SAIDA",
        4,
        "Venda",
    )

    assert novo_saldo == 6
    assert obter_saldo(produto_id) == 6
    assert contar_movimentacoes(produto_id) == 2


def test_saida_maior_que_estoque_e_rejeitada(app_teste):
    produto_id = db.cadastrar_produto("Envelope", 5)
    total_inicial = contar_movimentacoes(produto_id)

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        db.registrar_movimentacao(
            produto_id,
            "SAIDA",
            8,
            "Teste de saída inválida",
        )

    assert obter_saldo(produto_id) == 5
    assert contar_movimentacoes(produto_id) == total_inicial


def test_nao_permite_quantidade_zero_em_movimentacao(app_teste):
    produto_id = db.cadastrar_produto("Lápis", 5)

    with pytest.raises(ValueError, match="inteiro maior que zero"):
        db.registrar_movimentacao(
            produto_id,
            "ENTRADA",
            0,
        )

    assert obter_saldo(produto_id) == 5


def test_pagina_inicial_carrega(cliente):
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert b"Estoque atual" in resposta.data


def test_formulario_cadastra_produto(cliente):
    resposta = cliente.post(
        "/produtos/cadastrar",
        data={
            "nome": "Papel sulfite",
            "descricao": "Pacote de papel",
            "quantidade": "20",
            "estoque_minimo": "5",
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Produto cadastrado com sucesso!".encode() in resposta.data
    assert "Papel sulfite".encode() in resposta.data


def test_formulario_rejeita_saida_sem_estoque_suficiente(cliente):
    produto_id = db.cadastrar_produto("Marcador", 2)

    resposta = cliente.post(
        "/movimentacoes/registrar",
        data={
            "produto_id": str(produto_id),
            "tipo": "SAIDA",
            "quantidade": "5",
            "observacao": "Teste",
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Estoque insuficiente para essa saída.".encode() in resposta.data
    assert obter_saldo(produto_id) == 2
    assert contar_movimentacoes(produto_id) == 1


def test_pagina_inicial_exibe_botao_de_alterar_tema(cliente):
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert b"Alterar tema" in resposta.data
    assert b"tema-loja-fran" in resposta.data

def test_pagina_inicial_exibe_botao_de_alto_contraste(cliente):
    resposta = cliente.get("/")

    assert resposta.status_code == 200
    assert b"Alto contraste: desligado" in resposta.data
    assert b"alternar-contraste" in resposta.data
    assert b"alto-contraste-loja-fran" in resposta.data