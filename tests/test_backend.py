import pytest

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_and_get_meeting(async_client):
    payload = {"title": "Réunion Test", "organizer_name": "Alice"}
    create_resp = await async_client.post("/api/meetings", json=payload)
    assert create_resp.status_code == 200
    meeting = create_resp.json()
    assert meeting["title"] == payload["title"]

    code = meeting["meeting_code"]
    get_resp = await async_client.get(f"/api/meetings/{code}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()
    assert fetched["id"] == meeting["id"]
