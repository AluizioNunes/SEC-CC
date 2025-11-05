from __future__ import annotations
from typing import Dict, Any, Optional
import logging

from fastapi import APIRouter, HTTPException, Request, Depends, status
from pydantic import BaseModel

from ..db_asyncpg import get_pool
from ..auth import (
    jwt_manager,
    get_current_user,
    require_auth,
    audit_log,
    create_access_token,
)

logger = logging.getLogger("sec-fastapi")

auth_router = APIRouter(prefix="/auth", tags=["auth"]) 


@auth_router.post("/login")
async def login(request: Request):
    """Login validando usuário/e-mail e senha (bcrypt) na tabela SEC.Usuario.
    Aceita payload JSON: { "username": string, "password": string }.
    O campo "username" pode ser usuário (Usuario) ou e-mail (Email).
    Apenas senhas com hash bcrypt ($2…) são aceitas.
    """
    try:
        try:
            body = await request.json()
        except Exception:
            raw = await request.body()
            try:
                import json
                body = json.loads(raw.decode("utf-8"))
            except Exception:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Corpo da requisição inválido")
        identifier = body.get("username") or body.get("email") or body.get("usuario")
        password = body.get("password")

        if not identifier or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username/email e senha são obrigatórios"
            )

        # Buscar usuário na tabela SEC.Usuario
        pool = await get_pool()
        row = await pool.fetchrow(
            'SELECT idusuario AS "IdUsuario", nome AS "Nome", email AS "Email", usuario AS "Login", senha AS "Senha", perfil AS "Perfil", permissao AS "Permissao" FROM "SEC"."Usuario" WHERE usuario=$1 OR email=$1 LIMIT 1',
            identifier
        )

        if not row:
            audit_log(
                action="unauthorized_access",
                user_id=str(identifier),
                resource="auth_system",
                details={"reason": "user_not_found", "ip_address": request.client.host}
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

        stored_password = row["Senha"]
        valid_password = False
        try:
            if isinstance(stored_password, str) and stored_password.startswith("$2"):
                import bcrypt  # type: ignore
                valid_password = bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8"))
            else:
                valid_password = False
        except Exception:
            valid_password = False

        if not valid_password:
            audit_log(
                action="unauthorized_access",
                user_id=str(identifier),
                resource="auth_system",
                details={"reason": "invalid_password", "ip_address": request.client.host}
            )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

        # Montar dados do token e resposta
        username_value = row["Login"] or row["Email"] or str(row["IdUsuario"])  # preferir Login
        role_value = row["Perfil"] or "user"

        token_data = {"sub": str(row["IdUsuario"]), "username": username_value, "role": role_value}
        access_token = create_access_token(token_data)
        refresh_token = jwt_manager.create_refresh_token({"sub": str(row["IdUsuario"]), "role": role_value})

        # Log de sucesso
        audit_log(
            action="login",
            user_id=username_value,
            resource="auth_system",
            details={"ip_address": request.client.host}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,
            "user": {
                "id": row["IdUsuario"],
                "name": row["Nome"],
                "email": row["Email"],
                "login": row["Login"],
                "profile": role_value,
            },
        }
    except HTTPException:
        raise
    except ValueError:
        # JSON malformado
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Corpo da requisição inválido")
    except Exception as e:
        audit_log(
            action="system_error",
            user_id=str(identifier if 'identifier' in locals() else 'unknown'),
            resource="auth_system",
            details={"error": str(e), "ip_address": getattr(request.client, 'host', 'unknown')}
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno do servidor")


@auth_router.post("/refresh")
async def refresh_token(request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Refresh access token"""
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token required"
            )

        # Verify refresh token
        payload = jwt_manager.verify_token(refresh_token, "refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Create new access token
        token_data = {"sub": payload["sub"], "role": payload.get("role", "user")}
        new_access_token = jwt_manager.create_access_token(token_data)

        # Log token refresh
        audit_log(
            action="token_refresh",
            user_id=payload["sub"],
            resource="auth_system",
            details={"ip_address": request.client.host}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@auth_router.post("/logout")
async def logout(request: Request, current_user: Dict[str, Any] = Depends(require_auth)):
    """Logout endpoint with audit logging"""
    try:
        # Log logout
        audit_log(
            action="logout",
            user_id=current_user["sub"],
            resource="auth_system",
            details={"ip_address": request.client.host}
        )

        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@auth_router.get("/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(require_auth)):
    """Get current user information"""
    return {
        "user_id": current_user["sub"],
        "role": current_user.get("role", "user"),
        "authenticated": True
    }


class ChangePasswordPayload(BaseModel):
    new_password: str
    current_password: Optional[str] = None
    requested_by: Optional[str] = None


@auth_router.post("/change-password")
async def change_password(payload: ChangePasswordPayload, request: Request, current_user: Dict[str, Any] = Depends(require_auth)):
    """Altera a senha do usuário autenticado com hash bcrypt ($2b$) e auditoria."""
    try:
        # Validar tamanho máximo do bcrypt (72 bytes)
        if len(payload.new_password.encode("utf-8")) > 72:
            raise HTTPException(status_code=400, detail="Senha muito longa (limite: 72 bytes)")

        user_id = int(str(current_user.get("sub")))

        pool = await get_pool()

        # Se current_password foi fornecida, validar contra a senha atual
        if payload.current_password is not None:
            row_pwd = await pool.fetchrow('SELECT senha AS "Senha" FROM "SEC"."Usuario" WHERE idusuario=$1', user_id)
            if not row_pwd:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            stored_password = row_pwd["Senha"]
            valid_password = False
            try:
                if isinstance(stored_password, str) and stored_password.startswith("$2"):
                    import bcrypt  # type: ignore
                    valid_password = bcrypt.checkpw(payload.current_password.encode("utf-8"), stored_password.encode("utf-8"))
                else:
                    valid_password = False
            except Exception:
                valid_password = False

            if not valid_password:
                audit_log(
                    action="unauthorized_access",
                    user_id=str(user_id),
                    resource="SEC.Usuario",
                    details={"reason": "wrong_current_password", "ip_address": request.client.host}
                )
                raise HTTPException(status_code=401, detail="Senha atual incorreta")

        # Gerar hash bcrypt para a nova senha
        import bcrypt
        salt = bcrypt.gensalt(rounds=11)
        hashed = bcrypt.hashpw(payload.new_password.encode("utf-8"), salt).decode("utf-8")  # $2b$

        # Atualizar senha e auditoria
        updated = await pool.fetchrow(
            'UPDATE "SEC"."Usuario" SET Senha=$1, CadastranteUpdate=$2, DataUpdate=CURRENT_TIMESTAMP WHERE idusuario=$3 RETURNING idusuario',
            hashed,
            (payload.requested_by or 'API-PASSWORD-CHANGE'),
            user_id,
        )

        if not updated:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        # Auditoria
        audit_log(
            action="password_change",
            user_id=str(user_id),
            resource="SEC.Usuario",
            details={"requested_by": (payload.requested_by or 'API-PASSWORD-CHANGE'), "ip_address": request.client.host}
        )

        return {"ok": True, "message": "Senha alterada com sucesso", "user_id": str(user_id)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")