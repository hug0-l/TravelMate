import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_share_trip(client: AsyncClient, auth_headers: dict):
    create = await client.post("/api/trips/", json={
        "title": "Shared Trip", "start_date": "2026-08-01", "end_date": "2026-08-05",
    }, headers=auth_headers)
    share_code = create.json()["share_code"]
    # Make it shared
    trip_id = create.json()["id"]
    await client.put(f"/api/trips/{trip_id}", json={"visibility": "shared"}, headers=auth_headers)
    # Access without auth
    resp = await client.get(f"/api/trips/share/{share_code}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Shared Trip"


@pytest.mark.asyncio
async def test_share_not_found(client: AsyncClient):
    resp = await client.get("/api/trips/share/nonexistent")
    assert resp.status_code == 404
