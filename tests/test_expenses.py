import pytest
from httpx import AsyncClient


@pytest.fixture
async def trip_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post("/api/trips/", json={
        "title": "Budget Trip", "start_date": "2026-10-01", "end_date": "2026-10-05",
    }, headers=auth_headers)
    return resp.json()["id"]


@pytest.fixture
async def user_id(client: AsyncClient, auth_headers: dict) -> str:
    # Get current user
    resp = await client.post("/api/auth/register", json={
        "email": "budget@test.com", "name": "Budget Tester", "password": "pass12345",
    })
    return resp.json()["user_id"]


@pytest.mark.asyncio
async def test_create_expense(client: AsyncClient, auth_headers: dict, trip_id: str):
    # Register a second user for splitting
    await client.post("/api/auth/register", json={
        "email": "splitter@test.com", "name": "Splitter", "password": "pass12345",
    })
    # Invite them
    await client.post(f"/api/trips/{trip_id}/members/invite", json={
        "email": "splitter@test.com",
    }, headers=auth_headers)

    # Get members to find user ids
    members_resp = await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)
    members = members_resp.json()
    owner = [m for m in members if m["role"] == "owner"][0]
    editor = [m for m in members if m["role"] == "editor"][0]

    resp = await client.post(f"/api/trips/{trip_id}/expenses", json={
        "title": "Dinner",
        "category": "food",
        "amount": 100.0,
        "currency": "TWD",
        "paid_by": owner["user_id"],
        "split_with": [editor["user_id"]],
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Dinner"
    assert data["amount"] == 100.0
    assert len(data["splits"]) == 2  # Owner + Editor


@pytest.mark.asyncio
async def test_list_expenses(client: AsyncClient, auth_headers: dict, trip_id: str):
    # Get user id
    m = (await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)).json()[0]
    await client.post(f"/api/trips/{trip_id}/expenses", json={
        "title": "Lunch", "amount": 50.0, "paid_by": m["user_id"],
    }, headers=auth_headers)
    resp = await client.get(f"/api/trips/{trip_id}/expenses", headers=auth_headers)
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Lunch"


@pytest.mark.asyncio
async def test_budget_summary(client: AsyncClient, auth_headers: dict, trip_id: str):
    m = (await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)).json()[0]
    await client.post(f"/api/trips/{trip_id}/expenses", json={
        "title": "Hotel", "amount": 300.0, "category": "accommodation", "paid_by": m["user_id"],
    }, headers=auth_headers)
    resp = await client.get(f"/api/trips/{trip_id}/budget-summary", headers=auth_headers)
    data = resp.json()
    assert data["total_expenses"] == 300.0
    assert "accommodation" in data["by_category"]


@pytest.mark.asyncio
async def test_delete_expense(client: AsyncClient, auth_headers: dict, trip_id: str):
    m = (await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)).json()[0]
    create = await client.post(f"/api/trips/{trip_id}/expenses", json={
        "title": "Delete", "amount": 20.0, "paid_by": m["user_id"],
    }, headers=auth_headers)
    exp_id = create.json()["id"]
    resp = await client.delete(f"/api/expenses/{exp_id}", headers=auth_headers)
    assert resp.status_code == 204
