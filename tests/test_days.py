import pytest
from httpx import AsyncClient


@pytest.fixture
async def trip_id(client: AsyncClient, auth_headers: dict) -> str:
    resp = await client.post("/api/trips/", json={
        "title": "Test Trip", "start_date": "2026-06-01", "end_date": "2026-06-05",
    }, headers=auth_headers)
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_create_day(client: AsyncClient, auth_headers: dict, trip_id: str):
    resp = await client.post(f"/api/trips/{trip_id}/days", json={
        "date": "2026-06-01", "title": "Day 1",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Day 1"


@pytest.mark.asyncio
async def test_list_days(client: AsyncClient, auth_headers: dict, trip_id: str):
    await client.post(f"/api/trips/{trip_id}/days", json={
        "date": "2026-06-01",
    }, headers=auth_headers)
    await client.post(f"/api/trips/{trip_id}/days", json={
        "date": "2026-06-02",
    }, headers=auth_headers)
    resp = await client.get(f"/api/trips/{trip_id}/days", headers=auth_headers)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_update_day(client: AsyncClient, auth_headers: dict, trip_id: str):
    create = await client.post(f"/api/trips/{trip_id}/days", json={
        "date": "2026-06-01",
    }, headers=auth_headers)
    day_id = create.json()["id"]
    resp = await client.put(f"/api/days/{day_id}", json={"title": "Arrival"}, headers=auth_headers)
    assert resp.json()["title"] == "Arrival"


@pytest.mark.asyncio
async def test_delete_day(client: AsyncClient, auth_headers: dict, trip_id: str):
    create = await client.post(f"/api/trips/{trip_id}/days", json={
        "date": "2026-06-01",
    }, headers=auth_headers)
    day_id = create.json()["id"]
    resp = await client.delete(f"/api/days/{day_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_reorder_days(client: AsyncClient, auth_headers: dict, trip_id: str):
    d1 = (await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-01"}, headers=auth_headers)).json()
    d2 = (await client.post(f"/api/trips/{trip_id}/days", json={"date": "2026-06-02"}, headers=auth_headers)).json()
    resp = await client.put(f"/api/trips/{trip_id}/days/reorder", json={
        "day_ids": [d2["id"], d1["id"]],
    }, headers=auth_headers)
    data = resp.json()
    assert data[0]["id"] == d2["id"]
    assert data[1]["id"] == d1["id"]
