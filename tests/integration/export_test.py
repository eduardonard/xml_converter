from fastapi.testclient import TestClient
import httpx
import pytest

from app.constants import APP_CREDENTIALS
from app.main import app

EXPORT_PATH_TEMPLATE = "/export/queue_id/{queue_id}/annotation_id/{annotation_id}"
BIN_REPLACEMENT = "/api/bin/"
REQUEST_SUFFIX = "/req/shift"

client = TestClient(app)


@pytest.fixture
def base64_data() -> dict[str, str]:
    """
    Fixture that provides base64 encoded data for testing.
    """
    with open('data/base64_strings/us.txt', 'r') as file:
        us = file.read()
    with open('data/base64_strings/uk.txt', 'r') as file:
        uk = file.read()
    with open('data/base64_strings/eu.txt', 'r') as file:
        eu = file.read()
    return {
        "us": us,
        "uk": uk,
        "eu": eu
    }


@pytest.fixture
def setup_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Fixture to set up environment variables for tests.
    """
    # Ensure that the environment variables are set
    if not APP_CREDENTIALS.username or not APP_CREDENTIALS.password:
        raise ValueError("Environment variables USERNAME and PASSWORD must be set.")

    # Use monkeypatch to temporarily set environment variables
    monkeypatch.setenv("USERNAME", APP_CREDENTIALS.username)
    monkeypatch.setenv("PASSWORD", APP_CREDENTIALS.password)


async def get_previous_request(bin_url: str) -> str:
    """
    Helper function to get the previous request's body content from a given bin_url.
    """
    async with httpx.AsyncClient() as client:
        get_last_request_url = f"{bin_url}{REQUEST_SUFFIX}"

        request_id_response = await client.get(get_last_request_url)

        if request_id_response.status_code != 200:
            raise ValueError("Failed to get last request from bin URL.")

        response_json = request_id_response.json()
        body_content = response_json.get("body", {}).get("content")

        return body_content


def get_api_url(bin_url: str) -> str:
    """
    Replace the URL path for fetching API data.
    """
    return bin_url.replace("/b/", BIN_REPLACEMENT)


async def export_item(
    setup_env_vars, base64_data, queue_id: int, annotation_id: int, key: str
):
    """
    Helper function to test export items for different regions.
    """
    # Format the export path with the given project and item IDs
    export_path = EXPORT_PATH_TEMPLATE.format(queue_id=queue_id, annotation_id=annotation_id)

    # Test with a valid annotation_id}"
    response = client.get(
        export_path,
        auth=(APP_CREDENTIALS.username, APP_CREDENTIALS.password),
    )
    assert response.status_code == 200

    response_data = response.json()
    bin_url = response_data.get("bin_url")
    api_url = get_api_url(bin_url)

    # Get the previous request's body content
    previous_request = await get_previous_request(api_url)
    assert base64_data[key] == previous_request


@pytest.mark.integration
async def test_read_item_eu(setup_env_vars, base64_data):
    await export_item(setup_env_vars, base64_data, 1197496, 3427896, "eu")


@pytest.mark.integration
async def test_read_item_uk(setup_env_vars, base64_data):
    await export_item(setup_env_vars, base64_data, 1197490, 3427891, "uk")


@pytest.mark.integration
async def test_read_item_us(setup_env_vars, base64_data):
    await export_item(setup_env_vars, base64_data, 1197493, 3427898, "us")
