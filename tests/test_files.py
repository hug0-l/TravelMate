import io

import pytest


@pytest.mark.asyncio
async def test_upload_image(client):
    file_content = b"fake-image-bytes"
    resp = await client.post(
        "/api/files/upload",
        files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "url" in data
    assert data["url"].startswith("/uploads/")


@pytest.mark.asyncio
async def test_upload_non_image_returns_400(client):
    file_content = b"fake-text-content"
    resp = await client.post(
        "/api/files/upload",
        files={"file": ("test.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "detail" in data
