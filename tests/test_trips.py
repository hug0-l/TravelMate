import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_trip(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/trips/", json={
        "title": "Tokyo Trip",
        "start_date": "2026-10-01",
        "end_date": "2026-10-07",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Tokyo Trip"
    assert "share_code" in data


@pytest.mark.asyncio
async def test_list_trips_empty(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/trips/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_trips(client: AsyncClient, auth_headers: dict):
    await client.post("/api/trips/", json={
        "title": "Trip 1", "start_date": "2026-01-01", "end_date": "2026-01-05",
    }, headers=auth_headers)
    await client.post("/api/trips/", json={
        "title": "Trip 2", "start_date": "2026-02-01", "end_date": "2026-02-05",
    }, headers=auth_headers)
    resp = await client.get("/api/trips/", headers=auth_headers)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_get_trip(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Osaka", "start_date": "2026-05-01", "end_date": "2026-05-03",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.get(f"/api/trips/{trip_id}", headers=auth_headers)
    assert resp.json()["title"] == "Osaka"


@pytest.mark.asyncio
async def test_update_trip(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Old", "start_date": "2026-01-01", "end_date": "2026-01-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.put(f"/api/trips/{trip_id}", json={"title": "Updated"}, headers=auth_headers)
    assert resp.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_trip(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Delete Me", "start_date": "2026-01-01", "end_date": "2026-01-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.delete(f"/api/trips/{trip_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_trip_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/trips/nonexistent", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized(client: AsyncClient):
    resp = await client.get("/api/trips/")
    assert resp.status_code == 401  # HTTPBearer returns 401 without token
