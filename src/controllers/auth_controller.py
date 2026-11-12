from flask import Blueprint, request, jsonify, make_response, render_template, redirect, url_for, g
from src.models.user_model import UserModel
from src.core.security import (
    SESSION_COOKIE_NAME,
    verificar_bloqueio_bruteforce,
    registrar_falha_login,
    limpar_falhas_login,
    criar_token_sessao,
    validar_token_sessao,
    exigir_autenticacao,
    registrar_auditoria,
    ler_ultimos_logs_auditoria,
)

auth_bp = Blueprint("auth_bp", __name__)
user_model = UserModel()


@auth_bp.route("/login", methods=["GET"])
def pagina_login():
    token = request.cookies.get(SESSION_COOKIE_NAME, "")
    if validar_token_sessao(token):
        return redirect(url_for("report_bp.dashboard_principal"))
    return render_template("login.html")


@auth_bp.route("/api/auth/login", methods=["POST"])
def api_login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip().lower()
    password = payload.get("password") or ""
    ip_cliente = request.remote_addr or "127.0.0.1"
    chave_rate = f"{ip_cliente}:{username}"

    segundos_bloqueado = verificar_bloqueio_bruteforce(chave_rate)
    if segundos_bloqueado:
        registrar_auditoria("LOGIN_BLOQUEADO_BRUTEFORCE", username or "desconhecido", "-", f"Bloqueado por {segundos_bloqueado}s")
        return jsonify({
            "detail": f"Muitas tentativas inválidas. Conta protegida temporariamente por {segundos_bloqueado} segundos."
        }), 429

    usuario = user_model.autenticar(username, password)
    if not usuario:
        registrar_falha_login(chave_rate)
        registrar_auditoria("LOGIN_FALHA", username or "desconhecido", "-", "Credenciais inválidas")
        return jsonify({"detail": "Usuário ou senha inválidos."}), 401

    limpar_falhas_login(chave_rate)
    sessao_dados = criar_token_sessao(
        username=usuario["username"],
        nome=usuario["nome"],
        perfil=usuario["perfil"],
    )

    registrar_auditoria("LOGIN_SUCESSO", usuario["username"], usuario["perfil"], "Sessão iniciada com Argon2id/HMAC")

    resp = make_response(jsonify({
        "status": "ok",
        "usuario": usuario,
        "csrf_token": sessao_dados["csrf_token"],
    }))
    resp.set_cookie(
        SESSION_COOKIE_NAME,
        sessao_dados["token"],
        httponly=True,
        samesite="Lax",
        max_age=8 * 3600,
    )
    return resp


@auth_bp.route("/api/auth/logout", methods=["POST"])
@exigir_autenticacao()
def api_logout():
    u = g.usuario_atual
    registrar_auditoria("LOGOUT", u.get("sub", ""), u.get("perfil", ""), "Sessão encerrada pelo usuário")
    resp = make_response(jsonify({"status": "logged_out"}))
    resp.delete_cookie(SESSION_COOKIE_NAME)
    return resp


@auth_bp.route("/api/auth/me", methods=["GET"])
@exigir_autenticacao()
def api_me():
    u = g.usuario_atual
    return jsonify({
        "username": u.get("sub"),
        "nome": u.get("nome"),
        "perfil": u.get("perfil"),
        "csrf_token": u.get("csrf"),
    })


@auth_bp.route("/api/admin/users", methods=["GET"])
@exigir_autenticacao(perfis_permitidos=["administrador"])
def listar_usuarios_e_auditoria():
    return jsonify({
        "usuarios": user_model.listar_usuarios_publico(),
        "auditoria": ler_ultimos_logs_auditoria(50),
    })


@auth_bp.route("/api/admin/users", methods=["POST"])
@exigir_autenticacao(perfis_permitidos=["administrador"])
def salvar_usuario():
    payload = request.get_json(silent=True) or {}
    try:
        novo = user_model.criar_ou_atualizar_usuario(
            username=payload.get("username", ""),
            nome=payload.get("nome", ""),
            perfil=payload.get("perfil", "usuario"),
            nova_senha=payload.get("password", ""),
        )
        u = g.usuario_atual
        registrar_auditoria(
            "ADMIN_SALVAR_USUARIO",
            u.get("sub", ""),
            u.get("perfil", ""),
            f"Usuário '{novo['username']}' configurado com perfil '{novo['perfil']}'",
        )
        return jsonify({"status": "ok", "usuario": novo})
    except ValueError as exc:
        return jsonify({"detail": str(exc)}), 400


@auth_bp.route("/api/admin/users/<username>", methods=["DELETE"])
@exigir_autenticacao(perfis_permitidos=["administrador"])
def excluir_usuario(username: str):
    try:
        user_model.remover_usuario(username)
        u = g.usuario_atual
        registrar_auditoria(
            "ADMIN_REMOVER_USUARIO",
            u.get("sub", ""),
            u.get("perfil", ""),
            f"Removeu usuário '{username}'",
        )
        return jsonify({"status": "ok"})
    except ValueError as exc:
        return jsonify({"detail": str(exc)}), 400
