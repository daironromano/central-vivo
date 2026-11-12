import os
from dotenv import load_dotenv
from flask import Flask

from src.controllers.auth_controller import auth_bp
from src.controllers.report_controller import report_bp, report_model
from src.core.security import aplicar_headers_seguranca, SECRET_KEY

load_dotenv()


def create_app() -> Flask:
    """
    Factory MVC da Aplicação Centralizador Vivo.
    - Models:      src/models/ (user_model.py, report_model.py)
    - Views:       src/views/templates/ e src/views/static/
    - Controllers: src/controllers/ (auth_controller.py, report_controller.py)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "src", "views", "templates")
    static_dir = os.path.join(base_dir, "src", "views", "static")

    flask_app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )
    flask_app.config["SECRET_KEY"] = SECRET_KEY

    # Middleware global de cabeçalhos de segurança (CSP, NoSniff, X-Frame-Options, etc.)
    flask_app.after_request(aplicar_headers_seguranca)

    # Registro dos Controllers (Blueprints MVC)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(report_bp)

    return flask_app


app = create_app()


if __name__ == "__main__":
    report_model.inicializar_todos()
    print("==========================================================")
    print("  CENTRALIZADOR DE RELATORIOS VIVO (ARQUITETURA MVC)")
    print("  -> Acesse: http://127.0.0.1:8000")
    print("  -> Perfil Administrador: dairon / Vivo@Admin2026")
    print("  -> Perfil Usuario:       usuario / Vivo@User2026")
    print("==========================================================")
    app.run(host="127.0.0.1", port=8000, debug=True)
