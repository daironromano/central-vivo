"""
Entrypoint Principal — Centralizador Diário de Relatórios (Vivo)
Arquitetura MVC Separada em:
- backend/  (Models, Controllers, Extractors, Core Security & Excel Builder)
- frontend/ (Views HTML e Assets CSS/JS)
"""

import os
from backend.app import criar_app

app = criar_app()

if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    modo = os.getenv("ENV_MODE", "MOCK").upper()

    print("=" * 72)
    print(" VIVO — CENTRALIZADOR DIARIO DE RELATORIOS (ARQUITETURA MVC COMPLETA)")
    print(f" Camadas: backend/ + frontend/ | Modo: {modo}")
    print(f" Acesse no navegador: http://{host}:{port}")
    print("=" * 72)

    app.run(host=host, port=port, debug=False)
