import os
import time
import requests


BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
USERNAME = os.getenv("TEST_USERNAME", "root")
PASSWORDS = [
    os.getenv("TEST_PASSWORD_A", "Test@123"),
    os.getenv("TEST_PASSWORD_B", "Test@456"),
]


def _login(username: str, password: str):
    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    return r


def _change_password(token: str, new_password: str, current_password: str, requested_by: str):
    r = requests.post(
        f"{BASE_URL}/auth/change-password",
        json={
            "new_password": new_password,
            "current_password": current_password,
            "requested_by": requested_by,
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    return r


def test_login_bcrypt_root():
    # Tenta login com qualquer uma das senhas conhecidas
    success = False
    for pwd in PASSWORDS:
        resp = _login(USERNAME, pwd)
        if resp.status_code == 200:
            success = True
            break
    assert success, "Nenhuma senha conhecida funcionou para login do usuário root"


def test_change_password_flow_root():
    # Determina a senha atual e a nova senha alternando entre os valores
    current_pwd = None
    new_pwd = None
    token = None

    for pwd in PASSWORDS:
        resp = _login(USERNAME, pwd)
        if resp.status_code == 200:
            data = resp.json()
            token = data["access_token"]
            current_pwd = pwd
            # escolhe a outra senha como nova
            new_pwd = [p for p in PASSWORDS if p != current_pwd][0]
            break

    assert token is not None, "Não foi possível autenticar para iniciar o fluxo de troca de senha"

    # Solicita troca de senha
    resp_change = _change_password(token, new_pwd, current_pwd, requested_by="PYTEST-CHANGE")
    assert resp_change.status_code == 200, f"Falha ao trocar senha: {resp_change.status_code} {resp_change.text}"
    assert resp_change.json().get("ok") is True

    # Pequeno atraso para garantir escrita
    time.sleep(0.5)

    # Valida login com a nova senha
    resp_login_new = _login(USERNAME, new_pwd)
    assert resp_login_new.status_code == 200, "Login com nova senha falhou"

    # Reverte para a senha original
    token_new = resp_login_new.json()["access_token"]
    resp_revert = _change_password(token_new, current_pwd, new_pwd, requested_by="PYTEST-REVERT")
    assert resp_revert.status_code == 200, f"Falha ao reverter senha: {resp_revert.status_code} {resp_revert.text}"
    assert resp_revert.json().get("ok") is True