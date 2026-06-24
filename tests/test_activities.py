import pytest
from httpx import AsyncClient


@pytest.fixture
async def day_id(client: AsyncClient, auth_headers: dict) -> str:
    trip = await client.post("/api/trips/", json={
        "title": "Trip", "start_date": "2026-07-01", "end_date": "2026-07-03",
    }, headers=auth_headers)
    day = await client.post(f"/api/trips/{trip.json()['id']}/days", json={
        "date": "2026-07-01",
    }, headers=auth_headers)
    return day.json()["id"]


@pytest.mark.asyncio
async def test_create_activity(client: AsyncClient, auth_headers: dict, day_id: str):
    resp = await client.post(f"/api/days/{day_id}/activities", json={
        "title": "Visit Shrine", "category": "attraction",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Visit Shrine"


@pytest.mark.asyncio
async def test_list_activities(client: AsyncClient, auth_headers: dict, day_id: str):
    await client.post(f"/api/days/{day_id}/activities", json={"title": "A1"}, headers=auth_headers)
    await client.post(f"/api/days/{day_id}/activities", json={"title": "A2"}, headers=auth_headers)
    resp = await client.get(f"/api/days/{day_id}/activities", headers=auth_headers)
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_update_activity(client: AsyncClient, auth_headers: dict, day_id: str):
    create = await client.post(f"/api/days/{day_id}/activities", json={
        "title": "Old", "category": "other",
    }, headers=auth_headers)
    act_id = create.json()["id"]
    resp = await client.put(f"/api/activities/{act_id}", json={
        "title": "Updated", "notes": "Bring camera",
    }, headers=auth_headers)
    assert resp.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_activity(client: AsyncClient, auth_headers: dict, day_id: str):
    create = await client.post(f"/api/days/{day_id}/activities", json={
        "title": "Delete", "category": "other",
    }, headers=auth_headers)
    act_id = create.json()["id"]
    resp = await client.delete(f"/api/activities/{act_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_reorder_activities(client: AsyncClient, auth_headers: dict, day_id: str):
    a1 = (await client.post(f"/api/days/{day_id}/activities", json={"title": "A"}, headers=auth_headers)).json()
    a2 = (await client.post(f"/api/days/{day_id}/activities", json={"title": "B"}, headers=auth_headers)).json()
    resp = await client.put(f"/api/days/{day_id}/activities/reorder", json={
        "activity_ids": [a2["id"], a1["id"]],
    }, headers=auth_headers)
    data = resp.json()
    assert data[0]["id"] == a2["id"]


@pytest.mark.asyncio
async def test_create_activity_with_transport_mode(client: AsyncClient, auth_headers: dict, day_id: str):
    resp = await client.post(f"/api/days/{day_id}/activities", json={
        "title": "Go to Museum",
        "category": "transport",
        "transport_mode": "driving",
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["transport_mode"] == "driving"


@pytest.mark.asyncio
async def test_update_activity_transport_mode(client: AsyncClient, auth_headers: dict, day_id: str):
    create = await client.post(f"/api/days/{day_id}/activities", json={
        "title": "Commute",
        "category": "transport",
        "transport_mode": "driving",
    }, headers=auth_headers)
    act_id = create.json()["id"]
    resp = await client.put(f"/api/activities/{act_id}", json={
        "transport_mode": "walking",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["transport_mode"] == "walking"
