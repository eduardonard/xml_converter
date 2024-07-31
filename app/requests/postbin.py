from typing import Dict, Any
import httpx
from fastapi import HTTPException
from app.constants import POSTBIN_URL


async def create_bin() -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(POSTBIN_URL)
            response.raise_for_status()

            bin_data = response.json()
            bin_id = bin_data.get("binId")

            if not bin_id:
                raise HTTPException(
                    status_code=500, detail="Failed to retrieve bin URL"
                )
            return f"{POSTBIN_URL}/{bin_id}"

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while requesting {exc.request.url!r}.",
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"HTTP error occurred: {exc.response.text}",
        )


async def post_json(json_data: Dict[str, Any], url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=json_data)
            response.raise_for_status()
            return {"status_code": response.status_code, "response_text": response.text}
    except httpx.RequestError as exc:
        # Handle request errors, such as connection errors
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while requesting {exc.request.url!r}.",
        )
    except httpx.HTTPStatusError as exc:
        # Handle HTTP errors, such as 4xx or 5xx responses
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"HTTP error occurred: {exc.response.text}",
        )
    except Exception as exc:
        # Handle any other exceptions
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(exc)}"
        )
