
import os

from flask import Flask
from app.db import inicializar_banco


def criar_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")

    if not app.config["SECRET_KEY"]:
        if os.environ.get("RENDER"):
            raise RuntimeError(
                "A variável FLASK_SECRET_KEY precisa ser configurada."
            )

        app.config["SECRET_KEY"] = "chave-local-apenas-desenvolvimento"

    inicializar_banco()

    from app.routes import registrar_rotas
    registrar_rotas(app)

    return app
