import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/auth/register", json={
        "email": "alice@test.com",
        "name": "Alice",
        "password": "pass12345",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["name"] == "Alice"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "bob@test.com", "name": "Bob", "password": "pass12345",
    })
    resp = await client.post("/api/auth/register", json={
        "email": "bob@test.com", "name": "Bob2", "password": "pass45678",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "carol@test.com", "name": "Carol", "password": "pass12345",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "carol@test.com", "password": "pass12345",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "dave@test.com", "name": "Dave", "password": "pass12345",
    })
    resp = await client.post("/api/auth/login", json={
        "email": "dave@test.com", "password": "wrong",
    })
    assert resp.status_code == 401
