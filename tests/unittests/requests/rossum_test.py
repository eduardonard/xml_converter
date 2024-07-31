import pytest
import httpx
import respx
from fastapi import HTTPException
from app.requests.rossum import rossum_login, get_annotations
from app.constants import ROSSUM_CREDENTIALS


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_rossum_login_success():
    # Mock the login endpoint
    respx.post(f"{ROSSUM_CREDENTIALS.url}auth/login").mock(
        return_value=httpx.Response(200, json={"key": "fake_api_key"})
    )

    headers = await rossum_login()

    assert headers == {"Authorization": "Token fake_api_key"}


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_rossum_login_failure():
    # Mock the login endpoint with a failure response
    respx.post(f"{ROSSUM_CREDENTIALS.url}auth/login").mock(
        return_value=httpx.Response(401, json={"detail": "Authentication failed"})
    )

    with pytest.raises(HTTPException) as excinfo:
        await rossum_login()

    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Rossum authentication failed"


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_get_annotations_success():
    queue_id = 123
    respx.get(f"{ROSSUM_CREDENTIALS.url}queues/{queue_id}/export?format=xml").mock(
        return_value=httpx.Response(200, text="<xml>data</xml>")
    )

    headers = {"Authorization": "Token fake_api_key"}
    result = await get_annotations(queue_id, headers)

    assert result == "<xml>data</xml>"


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_get_annotations_queue_not_found():
    queue_id = 999
    respx.get(f"{ROSSUM_CREDENTIALS.url}queues/{queue_id}/export?format=xml").mock(
        return_value=httpx.Response(404)
    )
    respx.get(f"{ROSSUM_CREDENTIALS.url}queues").mock(
        return_value=httpx.Response(200, json={"results": [{"id": 123}, {"id": 456}]})
    )

    headers = {"Authorization": "Token fake_api_key"}

    with pytest.raises(Exception) as excinfo:
        await get_annotations(queue_id, headers)

    assert str(excinfo.value) == "404: Queue id not found, available queues: 123, 456"
