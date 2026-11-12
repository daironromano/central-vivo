import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.core.security import gerar_hash_senha, verificar_senha


class UserModel:
    """
    Model MVC responsável pela persistência segura de usuários e perfis RBAC
    ('administrador' e 'usuario') com senhas criptografadas em Argon2id / PBKDF2-SHA256.
    """

    def __init__(self):
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.pasta_data = os.path.join(raiz, "data")
        os.makedirs(self.pasta_data, exist_ok=True)
        self.arquivo_usuarios = os.path.join(self.pasta_data, "users_db.json")
        self._garantir_usuarios_padrao()

    def _ler_db(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.arquivo_usuarios):
            return {}
        try:
            with open(self.arquivo_usuarios, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _salvar_db(self, db: Dict[str, Dict[str, Any]]):
        with open(self.arquivo_usuarios, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)

    def _garantir_usuarios_padrao(self):
        db = self._ler_db()
        alterado = False

        senha_admin = os.getenv("ADMIN_DEFAULT_PASSWORD", "Vivo@Admin2026")
        senha_user = os.getenv("USER_DEFAULT_PASSWORD", "Vivo@User2026")

        if "dairon" not in db:
            db["dairon"] = {
                "username": "dairon",
                "nome": "Dairon Romano",
                "perfil": "administrador",
                "password_hash": gerar_hash_senha(senha_admin),
                "ativo": True,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            alterado = True

        if "usuario" not in db:
            db["usuario"] = {
                "username": "usuario",
                "nome": "Operador Regional Norte",
                "perfil": "usuario",
                "password_hash": gerar_hash_senha(senha_user),
                "ativo": True,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            alterado = True

        if alterado:
            self._salvar_db(db)

    def autenticar(self, username: str, senha: str) -> Optional[Dict[str, Any]]:
        uname = (username or "").strip().lower()
        db = self._ler_db()
        user = db.get(uname)
        if not user or not user.get("ativo", True):
            return None
        if not verificar_senha(senha, user.get("password_hash", "")):
            return None
        return {
            "username": user["username"],
            "nome": user["nome"],
            "perfil": user["perfil"],
        }

    def listar_usuarios_publico(self) -> List[Dict[str, Any]]:
        db = self._ler_db()
        saida = []
        for u in db.values():
            saida.append({
                "username": u["username"],
                "nome": u["nome"],
                "perfil": u["perfil"],
                "ativo": u.get("ativo", True),
                "criado_em": u.get("criado_em", "-"),
            })
        return saida

    def criar_ou_atualizar_usuario(
        self, username: str, nome: str, perfil: str, nova_senha: Optional[str] = None
    ) -> Dict[str, Any]:
        uname = (username or "").strip().lower()
        if not uname or len(uname) < 3:
            raise ValueError("O nome de usuário deve ter pelo menos 3 caracteres.")
        if perfil not in ("administrador", "usuario"):
            raise ValueError("Perfil inválido. Use 'administrador' ou 'usuario'.")

        db = self._ler_db()
        existente = db.get(uname)

        if not existente and (not nova_senha or len(nova_senha) < 8):
            raise ValueError("Para novos usuários, a senha deve ter no mínimo 8 caracteres.")

        hash_pw = (
            gerar_hash_senha(nova_senha)
            if (nova_senha and len(nova_senha.strip()) > 0)
            else existente["password_hash"]
        )

        db[uname] = {
            "username": uname,
            "nome": (nome or uname).strip(),
            "perfil": perfil,
            "password_hash": hash_pw,
            "ativo": True,
            "criado_em": existente["criado_em"] if existente else datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        self._salvar_db(db)
        return {
            "username": uname,
            "nome": db[uname]["nome"],
            "perfil": perfil,
        }

    def remover_usuario(self, username: str):
        uname = (username or "").strip().lower()
        if uname == "dairon":
            raise ValueError("O administrador principal ('dairon') não pode ser removido.")
        db = self._ler_db()
        if uname in db:
            db.pop(uname)
            self._salvar_db(db)
