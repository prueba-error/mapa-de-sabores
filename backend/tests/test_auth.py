import uuid

import pytest
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from httpx import AsyncClient


def test_password_hashing():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_cycle():
    payload = {"sub": "42", "email": "test@example.com"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "42"
    assert decoded["email"] == "test@example.com"
    assert "exp" in decoded


@pytest.mark.asyncio
async def test_auth_flow_e2e(client: AsyncClient):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "MyPassword123"

    # 1. Registro exitoso
    register_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": password,
            "full_name": "Test User",
        },
    )
    assert register_res.status_code == 201
    user_data = register_res.json()
    assert user_data["email"] == unique_email
    assert user_data["full_name"] == "Test User"
    assert "id" in user_data

    # 2. Conflicto por email duplicado
    duplicate_res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": password,
        },
    )
    assert duplicate_res.status_code == 409

    # 3. Login con contraseña incorrecta
    wrong_login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_email,
            "password": "WrongPassword!",
        },
    )
    assert wrong_login_res.status_code == 401

    # 4. Login exitoso y obtención de JWT
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": unique_email,
            "password": password,
        },
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 5. Consulta de /me con token válido
    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email
    assert me_data["id"] == user_data["id"]

    # 6. Consulta de /me sin token o con token inválido
    unauth_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_123"},
    )
    assert unauth_res.status_code == 401
