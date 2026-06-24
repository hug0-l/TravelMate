import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_pois_empty(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.get(f"/api/trips/{trip_id}/pois", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_poi(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "測試景點",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "測試景點"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_poi_fails_without_name(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.post(f"/api/trips/{trip_id}/pois", json={}, headers=auth_headers)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_pois_with_data(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "測試景點",
    }, headers=auth_headers)
    resp = await client.get(f"/api/trips/{trip_id}/pois", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "測試景點"


@pytest.mark.asyncio
async def test_update_poi(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    poi_resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "測試景點",
    }, headers=auth_headers)
    poi_id = poi_resp.json()["id"]
    resp = await client.put(f"/api/pois/{poi_id}", json={
        "notes": "updated",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["notes"] == "updated"


@pytest.mark.asyncio
async def test_delete_poi(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    poi_resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "Delete Me",
    }, headers=auth_headers)
    poi_id = poi_resp.json()["id"]
    resp = await client.delete(f"/api/pois/{poi_id}", headers=auth_headers)
    assert resp.status_code == 204
