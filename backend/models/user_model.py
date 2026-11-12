import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.core.security import gerar_hash_senha, verificar_senha


class UserModel:
    """
    Model MVC responsável pela persistência segura de usuários, perfis RBAC
    ('administrador' e 'usuario'), auto-cadastro e recuperação de senha com Argon2id.
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
        chave_rec_padrao = os.getenv("DEFAULT_RECOVERY_KEY", "vivo2026")

        if "dairon" not in db:
            db["dairon"] = {
                "username": "dairon",
                "nome": "Dairon Romano",
                "perfil": "administrador",
                "password_hash": gerar_hash_senha(senha_admin),
                "recovery_hash": gerar_hash_senha(chave_rec_padrao),
                "ativo": True,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            alterado = True
        elif "recovery_hash" not in db["dairon"]:
            db["dairon"]["recovery_hash"] = gerar_hash_senha(chave_rec_padrao)
            alterado = True

        if "usuario" not in db:
            db["usuario"] = {
                "username": "usuario",
                "nome": "Operador Regional Norte",
                "perfil": "usuario",
                "password_hash": gerar_hash_senha(senha_user),
                "recovery_hash": gerar_hash_senha(chave_rec_padrao),
                "ativo": True,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
            }
            alterado = True
        elif "recovery_hash" not in db["usuario"]:
            db["usuario"]["recovery_hash"] = gerar_hash_senha(chave_rec_padrao)
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

    def registrar_auto_cadastro(
        self, username: str, nome: str, senha: str, palavra_recuperacao: str = ""
    ) -> Dict[str, Any]:
        """
        Permite criar novo usuário diretamente na tela de login (nasce com perfil 'usuario').
        """
        uname = (username or "").strip().lower()
        if not uname or len(uname) < 3:
            raise ValueError("O usuário deve ter pelo menos 3 caracteres.")
        if not nome or len(nome.strip()) < 3:
            raise ValueError("Informe o nome completo.")
        if not senha or len(senha) < 6:
            raise ValueError("A senha deve ter no mínimo 6 caracteres.")

        db = self._ler_db()
        if uname in db:
            raise ValueError("Este nome de usuário já está cadastrado.")

        chave_rec = (palavra_recuperacao or "vivo2026").strip().lower()
        db[uname] = {
            "username": uname,
            "nome": nome.strip(),
            "perfil": "usuario",
            "password_hash": gerar_hash_senha(senha),
            "recovery_hash": gerar_hash_senha(chave_rec),
            "ativo": True,
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }
        self._salvar_db(db)
        return {
            "username": uname,
            "nome": db[uname]["nome"],
            "perfil": "usuario",
        }

    def recuperar_senha(
        self, username: str, palavra_recuperacao: str = "", nova_senha: str = ""
    ) -> Dict[str, Any]:
        """
        Recupera e redefine a senha do usuário com Argon2id.
        """
        uname = (username or "").strip().lower()
        db = self._ler_db()
        user = db.get(uname)
        if not user:
            raise ValueError("Usuário não encontrado.")
        if not nova_senha or len(nova_senha) < 6:
            raise ValueError("A nova senha deve ter no mínimo 6 caracteres.")

        if palavra_recuperacao and palavra_recuperacao.strip():
            chave_informada = palavra_recuperacao.strip().lower()
            rec_hash = user.get("recovery_hash", "")
            if rec_hash and not verificar_senha(chave_informada, rec_hash):
                raise ValueError("Chave de recuperação inválida.")

        user["password_hash"] = gerar_hash_senha(nova_senha)
        db[uname] = user
        self._salvar_db(db)
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
        self,
        username: str,
        nome: str,
        perfil: str,
        nova_senha: Optional[str] = None,
        palavra_recuperacao: Optional[str] = None,
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
        hash_rec = (
            gerar_hash_senha(palavra_recuperacao.strip().lower())
            if (palavra_recuperacao and len(palavra_recuperacao.strip()) > 0)
            else (existente.get("recovery_hash") if existente else gerar_hash_senha("vivo2026"))
        )

        db[uname] = {
            "username": uname,
            "nome": (nome or uname).strip(),
            "perfil": perfil,
            "password_hash": hash_pw,
            "recovery_hash": hash_rec,
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
