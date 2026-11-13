from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    # Libera o CORS para que o Frontend (Vite/React) consiga acessar esta API
    @app.after_request
    def liberar_cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    # Registrar rotas/blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # Criar tabelas no banco SQLite se ainda não existirem
    with app.app_context():
        from app import models  # noqa: F401 - garante o carregamento de todas as tabelas
        db.create_all()

    return app
