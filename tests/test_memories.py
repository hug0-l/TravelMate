import pytest
from httpx import AsyncClient


@pytest.fixture
async def trip_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post("/api/trips/", json={
        "title": "Memory Trip", "start_date": "2026-12-01", "end_date": "2026-12-05",
    }, headers=auth_headers)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_memory(client: AsyncClient, auth_headers: dict, trip_id: str):
    resp = await client.post(f"/api/trips/{trip_id}/memories", json={
        "title": "First Day",
        "content": "Arrived at Tokyo!",
        "date": "2026-12-01",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "First Day"
    assert data["content"] == "Arrived at Tokyo!"


@pytest.mark.asyncio
async def test_list_memories(client: AsyncClient, auth_headers: dict, trip_id: str):
    await client.post(f"/api/trips/{trip_id}/memories", json={
        "title": "M1", "date": "2026-12-01",
    }, headers=auth_headers)
    await client.post(f"/api/trips/{trip_id}/memories", json={
        "title": "M2", "date": "2026-12-02",
    }, headers=auth_headers)
    resp = await client.get(f"/api/trips/{trip_id}/memories", headers=auth_headers)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_delete_memory(client: AsyncClient, auth_headers: dict, trip_id: str):
    create = await client.post(f"/api/trips/{trip_id}/memories", json={
        "title": "Delete Me", "date": "2026-12-01",
    }, headers=auth_headers)
    mem_id = create.json()["id"]
    resp = await client.delete(f"/api/memories/{mem_id}", headers=auth_headers)
    assert resp.status_code == 204
