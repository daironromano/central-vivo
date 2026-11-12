import os
import hmac
import time
import json
import secrets
import hashlib
import base64
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional
from flask import request, jsonify, g, redirect, url_for

try:
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    _ARGON2_HASHER = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
except ImportError:
    _ARGON2_HASHER = None

SECRET_KEY = os.getenv("APP_SECRET_KEY", "vivo-centralizador-enterprise-hmac-key-2026-sec")
SESSION_COOKIE_NAME = "vivo_hub_session"
CSRF_HEADER_NAME = "X-CSRF-Token"

_LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 300


def gerar_hash_senha(senha_plana: str) -> str:
    if _ARGON2_HASHER is not None:
        return _ARGON2_HASHER.hash(senha_plana)

    salt = secrets.token_hex(32)
    dk = hashlib.pbkdf2_hmac("sha256", senha_plana.encode("utf-8"), salt.encode("utf-8"), 600000)
    return f"pbkdf2_sha256$600000${salt}${dk.hex()}"


def verificar_senha(senha_plana: str, hash_armazenado: str) -> bool:
    if not senha_plana or not hash_armazenado:
        return False

    if hash_armazenado.startswith("$argon2") and _ARGON2_HASHER is not None:
        try:
            return _ARGON2_HASHER.verify(hash_armazenado, senha_plana)
        except (VerifyMismatchError, Exception):
            return False

    if hash_armazenado.startswith("pbkdf2_sha256$"):
        try:
            _, iter_str, salt, hash_hex = hash_armazenado.split("$", 3)
            dk = hashlib.pbkdf2_hmac(
                "sha256", senha_plana.encode("utf-8"), salt.encode("utf-8"), int(iter_str)
            )
            return hmac.compare_digest(dk.hex(), hash_hex)
        except Exception:
            return False

    return False


def verificar_bloqueio_bruteforce(identificador: str) -> Optional[int]:
    reg = _LOGIN_ATTEMPTS.get(identificador)
    if not reg:
        return None
    bloqueado_ate = reg.get("locked_until", 0)
    agora = time.time()
    if bloqueado_ate > agora:
        return int(bloqueado_ate - agora)
    if bloqueado_ate > 0 and agora >= bloqueado_ate:
        _LOGIN_ATTEMPTS.pop(identificador, None)
    return None


def registrar_falha_login(identificador: str):
    agora = time.time()
    reg = _LOGIN_ATTEMPTS.get(identificador, {"count": 0, "locked_until": 0})
    reg["count"] += 1
    if reg["count"] >= MAX_ATTEMPTS:
        reg["locked_until"] = agora + LOCKOUT_SECONDS
    _LOGIN_ATTEMPTS[identificador] = reg


def limpar_falhas_login(identificador: str):
    _LOGIN_ATTEMPTS.pop(identificador, None)


def criar_token_sessao(username: str, nome: str, perfil: str) -> Dict[str, str]:
    csrf_token = secrets.token_urlsafe(32)
    payload = {
        "sub": username,
        "nome": nome,
        "perfil": perfil,
        "csrf": csrf_token,
        "iat": int(time.time()),
        "exp": int(time.time()) + (8 * 3600),
    }
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
    assinatura = hmac.new(
        SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return {
        "token": f"{payload_b64}.{assinatura}",
        "csrf_token": csrf_token,
    }


def validar_token_sessao(token: str) -> Optional[Dict[str, Any]]:
    if not token or "." not in token:
        return None
    try:
        payload_b64, assinatura_recebida = token.rsplit(".", 1)
        assinatura_esperada = hmac.new(
            SECRET_KEY.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(assinatura_recebida, assinatura_esperada):
            return None
        payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode("utf-8")).decode("utf-8"))
        if int(time.time()) > payload.get("exp", 0):
            return None
        return payload
    except Exception:
        return None


def registrar_auditoria(acao: str, usuario: str, perfil: str, detalhes: str = ""):
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    pasta_data = os.path.join(raiz, "data")
    os.makedirs(pasta_data, exist_ok=True)
    caminho_log = os.path.join(pasta_data, "audit_log.jsonl")
    evento = {
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "usuario": usuario,
        "perfil": perfil,
        "ip": request.remote_addr if request else "127.0.0.1",
        "acao": acao,
        "detalhes": detalhes,
    }
    try:
        with open(caminho_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    except Exception:
        pass


def ler_ultimos_logs_auditoria(limite: int = 50):
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    caminho_log = os.path.join(raiz, "data", "audit_log.jsonl")
    if not os.path.exists(caminho_log):
        return []
    try:
        with open(caminho_log, "r", encoding="utf-8") as f:
            linhas = [json.loads(line) for line in f if line.strip()]
        return list(reversed(linhas[-limite:]))
    except Exception:
        return []


def exigir_autenticacao(perfis_permitidos=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.cookies.get(SESSION_COOKIE_NAME, "")
            sessao = validar_token_sessao(token)
            if not sessao:
                if request.path.startswith("/api/"):
                    return jsonify({"detail": "Sessão expirada ou não autenticada."}), 401
                return redirect(url_for("auth_bp.pagina_login"))

            if request.method in ("POST", "PUT", "DELETE"):
                csrf_enviado = request.headers.get(CSRF_HEADER_NAME, "")
                if not csrf_enviado or not hmac.compare_digest(csrf_enviado, sessao.get("csrf", "")):
                    return jsonify({"detail": "Falha de validação CSRF. Recarregue a página."}), 403

            if perfis_permitidos and sessao.get("perfil") not in perfis_permitidos:
                registrar_auditoria(
                    "ACESSO_NEGADO_RBAC",
                    sessao.get("sub", "?"),
                    sessao.get("perfil", "?"),
                    f"Tentou acessar {request.path}",
                )
                return jsonify({
                    "detail": f"Acesso restrito ao perfil: {', '.join(perfis_permitidos)}."
                }), 403

            g.usuario_atual = sessao
            return f(*args, **kwargs)
        return wrapper
    return decorator


def aplicar_headers_seguranca(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self';"
    )
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response
