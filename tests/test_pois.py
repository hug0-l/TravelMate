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


@pytest.mark.asyncio
async def test_create_poi_with_all_fields(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "台北101",
        "address": "台北市信義區信義路五段7號",
        "lat": 25.0339,
        "lng": 121.5646,
        "place_id": "ChIJBQUFBQUFBQAR",
        "notes": "觀景台",
        "category": "attraction",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "台北101"
    assert data["address"] == "台北市信義區信義路五段7號"
    assert data["lat"] == 25.0339
    assert data["lng"] == 121.5646
    assert data["place_id"] == "ChIJBQUFBQUFBQAR"
    assert data["notes"] == "觀景台"
    assert data["category"] == "attraction"


@pytest.mark.asyncio
async def test_update_poi_lat_lng(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    poi_resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "Test Spot",
    }, headers=auth_headers)
    poi_id = poi_resp.json()["id"]
    resp = await client.put(f"/api/pois/{poi_id}", json={
        "lat": 25.034,
        "lng": 121.565,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["lat"] == 25.034
    assert data["lng"] == 121.565


@pytest.mark.asyncio
async def test_update_poi_address(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    poi_resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "Test Spot",
    }, headers=auth_headers)
    poi_id = poi_resp.json()["id"]
    resp = await client.put(f"/api/pois/{poi_id}", json={
        "address": "新地址",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["address"] == "新地址"


@pytest.mark.asyncio
async def test_update_poi_multiple_fields(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    trip_id = create.json()["id"]
    poi_resp = await client.post(f"/api/trips/{trip_id}/pois", json={
        "name": "Original",
        "notes": "original notes",
        "category": "other",
        "address": "old address",
    }, headers=auth_headers)
    poi_id = poi_resp.json()["id"]
    resp = await client.put(f"/api/pois/{poi_id}", json={
        "name": "Updated",
        "notes": "new notes",
        "category": "restaurant",
        "address": "new address",
        "lat": 25.0,
        "lng": 121.5,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated"
    assert data["notes"] == "new notes"
    assert data["category"] == "restaurant"
    assert data["address"] == "new address"
    assert data["lat"] == 25.0
    assert data["lng"] == 121.5
