"""
Aplicação Principal Flask — Camada Backend MVC (Vivo Centralizador).
Conecta Models e Controllers de `backend/` às Views e Assets de `frontend/`.
"""

import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

from backend.core.security import aplicar_headers_seguranca
from backend.controllers.auth_controller import auth_bp
from backend.controllers.report_controller import report_bp


def criar_app() -> Flask:
    views_dir = BASE_DIR / "frontend" / "views"
    assets_dir = BASE_DIR / "frontend" / "assets"

    app = Flask(
        __name__,
        template_folder=str(views_dir),
        static_folder=str(assets_dir),
        static_url_path="/static",
    )

    app.config["MAX_CONTENT_LENGTH"] = 35 * 1024 * 1024  # 35 MB max upload

    # Aplica cabeçalhos de segurança OWASP em todas as respostas
    app.after_request(aplicar_headers_seguranca)

    # Registra Controllers MVC (Blueprints)
    app.register_blueprint(auth_bp)
    app.register_blueprint(report_bp)

    return app
