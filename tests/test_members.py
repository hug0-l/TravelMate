import pytest
from httpx import AsyncClient


@pytest.fixture
async def trip_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post("/api/trips/", json={
        "title": "Collab Trip", "start_date": "2026-09-01", "end_date": "2026-09-05",
    }, headers=auth_headers)
    return resp.json()["id"]


@pytest.fixture
async def second_user_headers(client: AsyncClient) -> dict:
    resp = await client.post("/api/auth/register", json={
        "email": "friend@test.com", "name": "Friend", "password": "pass12345",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_list_members(client: AsyncClient, auth_headers: dict, trip_id: str):
    resp = await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)
    assert resp.status_code == 200
    members = resp.json()
    assert len(members) == 1
    assert members[0]["role"] == "owner"


@pytest.mark.asyncio
async def test_invite_member(client: AsyncClient, auth_headers: dict, second_user_headers: dict, trip_id: str):
    resp = await client.post(f"/api/trips/{trip_id}/members/invite", json={
        "email": "friend@test.com",
    }, headers=auth_headers)
    assert resp.status_code == 201

    # Now list should have 2 members
    resp = await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_invite_non_owner_forbidden(client: AsyncClient, auth_headers: dict, trip_id: str):
    # Register another user who is not the owner
    other = await client.post("/api/auth/register", json={
        "email": "viewer@test.com", "name": "Viewer", "password": "pass12345",
    })
    other_token = other.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp = await client.post(f"/api/trips/{trip_id}/members/invite", json={
        "email": "friend@test.com",
    }, headers=other_headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_remove_member(client: AsyncClient, auth_headers: dict, trip_id: str):
    # First invite someone
    await client.post("/api/auth/register", json={
        "email": "removeme@test.com", "name": "RemoveMe", "password": "pass12345",
    })
    await client.post(f"/api/trips/{trip_id}/members/invite", json={
        "email": "removeme@test.com",
    }, headers=auth_headers)

    # Get members to find the member id
    resp = await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)
    members = resp.json()
    member_to_remove = [m for m in members if m["email"] == "removeme@test.com"][0]

    resp = await client.delete(
        f"/api/trips/{trip_id}/members/{member_to_remove['id']}",
        headers=auth_headers,
    )
    assert resp.status_code == 204

    resp = await client.get(f"/api/trips/{trip_id}/members", headers=auth_headers)
    assert len(resp.json()) == 1  # Only owner left
