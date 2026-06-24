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
async def test_upload_jpeg(client):
    file_content = b"fake-jpeg-bytes"
    resp = await client.post(
        "/api/files/upload",
        files={"file": ("photo.jpg", io.BytesIO(file_content), "image/jpeg")},
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


@pytest.mark.asyncio
@pytest.mark.xfail(reason="File size limit not yet implemented")
async def test_upload_large_file_returns_error(client):
    file_content = b"x" * (11 * 1024 * 1024)  # >10MB
    resp = await client.post(
        "/api/files/upload",
        files={"file": ("huge.png", io.BytesIO(file_content), "image/png")},
    )
    assert resp.status_code in (400, 413)
