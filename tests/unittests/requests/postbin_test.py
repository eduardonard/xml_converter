import pytest
import httpx
import respx
from fastapi import HTTPException
from app.requests.postbin import create_bin, post_json


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_create_bin_success():
    POSTBIN_URL = "https://www.postb.in/api/bin"
    respx.post(POSTBIN_URL).mock(
        return_value=httpx.Response(200, json={"binId": "fake_bin_id"})
    )

    bin_url = await create_bin()

    assert bin_url == "https://www.postb.in/api/bin/fake_bin_id"


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_create_bin_failure():
    POSTBIN_URL = "https://www.postb.in/api/bin"
    respx.post(POSTBIN_URL).mock(
        return_value=httpx.Response(500, json={"detail": "Server error"})
    )

    with pytest.raises(HTTPException) as excinfo:
        await create_bin()

    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == 'HTTP error occurred: {"detail": "Server error"}'


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_post_json_success():
    url = "https://www.example.com/api"
    json_data = {"key": "value"}
    respx.post(url).mock(return_value=httpx.Response(200, text="Success"))

    response = await post_json(json_data, url)

    assert response["status_code"] == 200
    assert response["response_text"] == "Success"


@pytest.mark.asyncio
@pytest.mark.unit
@respx.mock
async def test_post_json_http_error():
    url = "https://www.example.com/api"
    json_data = {"key": "value"}
    respx.post(url).mock(return_value=httpx.Response(404, text="Not Found"))

    with pytest.raises(HTTPException) as excinfo:
        await post_json(json_data, url)

    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "HTTP error occurred: Not Found"
