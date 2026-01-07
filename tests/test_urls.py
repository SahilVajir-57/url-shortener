import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_shorten_url_success(client: AsyncClient):
    response = await client.post(
        "/shorten",
        json={"url": "https://www.google.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["original_url"] == "https://www.google.com/"
    assert data["clicks"] == 0
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_shorten_url_with_custom_code(client: AsyncClient):
    response = await client.post(
        "/shorten",
        json={"url": "https://www.github.com", "custom_code": "mycode"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "mycode"


@pytest.mark.asyncio
async def test_shorten_url_duplicate_custom_code(client: AsyncClient):
    # Create first URL
    await client.post(
        "/shorten",
        json={"url": "https://www.google.com", "custom_code": "duplicate"}
    )
    
    # Try to create another with same code
    response = await client.post(
        "/shorten",
        json={"url": "https://www.github.com", "custom_code": "duplicate"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Custom code already in use"


@pytest.mark.asyncio
async def test_shorten_url_invalid_url(client: AsyncClient):
    response = await client.post(
        "/shorten",
        json={"url": "not-a-valid-url"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_redirect_success(client: AsyncClient):
    # Create URL
    create_response = await client.post(
        "/shorten",
        json={"url": "https://www.google.com"}
    )
    short_code = create_response.json()["short_code"]
    
    # Test redirect
    response = await client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://www.google.com/"


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient):
    response = await client.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "URL not found"


@pytest.mark.asyncio
async def test_redirect_deactivated(client: AsyncClient):
    # Create URL
    create_response = await client.post(
        "/shorten",
        json={"url": "https://www.google.com"}
    )
    short_code = create_response.json()["short_code"]
    
    # Deactivate
    await client.delete(f"/{short_code}")
    
    # Try to redirect
    response = await client.get(f"/{short_code}", follow_redirects=False)
    assert response.status_code == 410
    assert response.json()["detail"] == "URL has been deactivated"


@pytest.mark.asyncio
async def test_get_stats(client: AsyncClient):
    # Create URL
    create_response = await client.post(
        "/shorten",
        json={"url": "https://www.google.com"}
    )
    short_code = create_response.json()["short_code"]
    
    # Get stats
    response = await client.get(f"/{short_code}/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == short_code
    assert data["original_url"] == "https://www.google.com/"
    assert "clicks" in data


@pytest.mark.asyncio
async def test_get_stats_not_found(client: AsyncClient):
    response = await client.get("/nonexistent/stats")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_analytics(client: AsyncClient):
    # Create URL
    create_response = await client.post(
        "/shorten",
        json={"url": "https://www.google.com"}
    )
    short_code = create_response.json()["short_code"]
    
    # Get analytics
    response = await client.get(f"/{short_code}/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == short_code
    assert "total_clicks" in data
    assert "daily_clicks" in data
    assert "top_referrers" in data


@pytest.mark.asyncio
async def test_deactivate_url(client: AsyncClient):
    # Create URL
    create_response = await client.post(
        "/shorten",
        json={"url": "https://www.google.com"}
    )
    short_code = create_response.json()["short_code"]
    
    # Deactivate
    response = await client.delete(f"/{short_code}")
    assert response.status_code == 204
    
    # Verify deactivated
    stats_response = await client.get(f"/{short_code}/stats")
    assert stats_response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_deactivate_not_found(client: AsyncClient):
    response = await client.delete("/nonexistent")
    assert response.status_code == 404