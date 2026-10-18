
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent.parent / "estoque.db"


def conectar():
    """Abre uma conexão com o banco e habilita as chaves estrangeiras."""
    conexao = sqlite3.connect(DATABASE_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco():
    """Cria as tabelas necessárias caso ainda não existam."""
    with conectar() as conexao:
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL CHECK (length(trim(nome)) > 0),
                descricao TEXT,
                quantidade_atual INTEGER NOT NULL DEFAULT 0
                    CHECK (quantidade_atual >= 0),
                estoque_minimo INTEGER NOT NULL DEFAULT 0
                    CHECK (estoque_minimo >= 0),
                ativo INTEGER NOT NULL DEFAULT 1
                    CHECK (ativo IN (0, 1))
            )
        """)

        conexao.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
                quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                observacao TEXT,
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)


def cadastrar_produto(nome, quantidade_inicial, descricao="", estoque_minimo=0):
    """Cadastra um produto e registra o saldo inicial."""
    nome = nome.strip() if isinstance(nome, str) else ""

    if not nome:
        raise ValueError("O nome do produto é obrigatório.")

    if type(quantidade_inicial) is not int or quantidade_inicial < 0:
        raise ValueError("A quantidade inicial deve ser um inteiro maior ou igual a zero.")

    if type(estoque_minimo) is not int or estoque_minimo < 0:
        raise ValueError("O estoque mínimo deve ser um inteiro maior ou igual a zero.")

    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO produtos (nome, descricao, quantidade_atual, estoque_minimo)
            VALUES (?, ?, ?, ?)
            """,
            (nome, descricao.strip(), quantidade_inicial, estoque_minimo),
        )
        produto_id = cursor.lastrowid

        if quantidade_inicial > 0:
            conexao.execute(
                """
                INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao)
                VALUES (?, 'ENTRADA', ?, ?)
                """,
                (produto_id, quantidade_inicial, "Estoque inicial"),
            )

        return produto_id


def listar_produtos():
    """Retorna os produtos ativos em ordem alfabética."""
    with conectar() as conexao:
        return conexao.execute("""
            SELECT id, nome, descricao, quantidade_atual, estoque_minimo, ativo
            FROM produtos
            WHERE ativo = 1
            ORDER BY nome COLLATE NOCASE
        """).fetchall()


def registrar_movimentacao(produto_id, tipo, quantidade, observacao=""):
    """Registra uma entrada ou saída e atualiza o saldo atomicamente."""
    if tipo not in ("ENTRADA", "SAIDA"):
        raise ValueError("O tipo deve ser ENTRADA ou SAIDA.")

    if type(quantidade) is not int or quantidade <= 0:
        raise ValueError("A quantidade deve ser um inteiro maior que zero.")

    with conectar() as conexao:
        produto = conexao.execute(
            """
            SELECT id, quantidade_atual
            FROM produtos
            WHERE id = ? AND ativo = 1
            """,
            (produto_id,),
        ).fetchone()

        if produto is None:
            raise ValueError("Produto não encontrado ou inativo.")

        saldo_atual = produto["quantidade_atual"]

        if tipo == "SAIDA" and quantidade > saldo_atual:
            raise ValueError("Estoque insuficiente para essa saída.")

        if tipo == "ENTRADA":
            novo_saldo = saldo_atual + quantidade
        else:
            novo_saldo = saldo_atual - quantidade

        conexao.execute(
            "UPDATE produtos SET quantidade_atual = ? WHERE id = ?",
            (novo_saldo, produto_id),
        )

        conexao.execute(
            """
            INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao)
            VALUES (?, ?, ?, ?)
            """,
            (produto_id, tipo, quantidade, observacao.strip()),
        )

    return novo_saldo


def listar_movimentacoes(produto_id=None):
    """Retorna o histórico de movimentações, opcionalmente por produto."""
    with conectar() as conexao:
        consulta = """
            SELECT m.id, m.produto_id, p.nome AS produto_nome,
                   m.tipo, m.quantidade, m.data_hora, m.observacao
            FROM movimentacoes AS m
            JOIN produtos AS p ON p.id = m.produto_id
        """
        parametros = ()

        if produto_id is not None:
            consulta += " WHERE m.produto_id = ?"
            parametros = (produto_id,)

        consulta += " ORDER BY m.id DESC"

        return conexao.execute(consulta, parametros).fetchall()
