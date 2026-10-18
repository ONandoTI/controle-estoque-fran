
from flask import render_template, request, redirect, url_for, flash

from app.db import (
    cadastrar_produto,
    listar_produtos,
    registrar_movimentacao,
    listar_movimentacoes,
)


def registrar_rotas(app):

    @app.route("/")
    def index():
        produtos = listar_produtos()
        movimentacoes = listar_movimentacoes()

        produtos_estoque_baixo = [
            produto for produto in produtos
            if produto["quantidade_atual"] <= produto["estoque_minimo"]
        ]

        return render_template(
            "index.html",
            produtos=produtos,
            movimentacoes=movimentacoes,
            total_estoque_baixo=len(produtos_estoque_baixo),
        )

    @app.route("/produtos/cadastrar", methods=["POST"])
    def cadastrar():
        nome = request.form.get("nome", "")
        descricao = request.form.get("descricao", "")
        quantidade = request.form.get("quantidade", "")
        estoque_minimo = request.form.get("estoque_minimo", "0")

        try:
            quantidade = int(quantidade)
            estoque_minimo = int(estoque_minimo)

            cadastrar_produto(
                nome=nome,
                descricao=descricao,
                quantidade_inicial=quantidade,
                estoque_minimo=estoque_minimo,
            )
            flash("Produto cadastrado com sucesso!", "sucesso")

        except (ValueError, TypeError) as erro:
            flash(str(erro) or "Informe valores válidos.", "erro")

        return redirect(url_for("index"))

    @app.route("/movimentacoes/registrar", methods=["POST"])
    def movimentar():
        produto_id = request.form.get("produto_id", "")
        tipo = request.form.get("tipo", "")
        quantidade = request.form.get("quantidade", "")
        observacao = request.form.get("observacao", "")

        try:
            produto_id = int(produto_id)
            quantidade = int(quantidade)

            registrar_movimentacao(
                produto_id=produto_id,
                tipo=tipo,
                quantidade=quantidade,
                observacao=observacao,
            )
            flash("Movimentação registrada com sucesso!", "sucesso")

        except (ValueError, TypeError) as erro:
            flash(str(erro) or "Informe valores válidos.", "erro")

        return redirect(url_for("index"))
