from typing import Dict
import httpx
from fastapi import HTTPException
from app.constants import ROSSUM_CREDENTIALS


# Authentication function
async def rossum_login() -> Dict[str, str]:
    auth_url = f"{ROSSUM_CREDENTIALS.url}auth/login"

    async with httpx.AsyncClient() as client:
        auth_response = await client.post(
            auth_url,
            json={
                "username": ROSSUM_CREDENTIALS.username,
                "password": ROSSUM_CREDENTIALS.password,
            },
        )

        if auth_response.status_code != httpx.codes.OK:
            raise HTTPException(
                status_code=auth_response.status_code,
                detail="Rossum authentication failed",
            )

        auth_data = auth_response.json()
        api_key = auth_data.get("key")

        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve API key from Rossum response",
            )

        # Return headers for authentication
        return {"Authorization": f"Token {api_key}"}


# Function to get annotations
async def get_annotations(queue_id: int, headers: Dict[str, str]) -> str:
    queues_url = f"{ROSSUM_CREDENTIALS.url}queues"
    export_url = f"{queues_url}/{queue_id}/export?format=xml"

    async with httpx.AsyncClient() as client:
        export_response = await client.get(export_url, headers=headers)

        match export_response.status_code:
            case httpx.codes.OK:
                return export_response.text

            case httpx.codes.NOT_FOUND:
                queues_response = await client.get(queues_url, headers=headers)
                if queues_response.status_code == httpx.codes.OK:
                    queue_ids = [
                        str(queue["id"])
                        for queue in queues_response.json().get("results", [])
                    ]
                    raise HTTPException(
                        status_code=404,
                        detail=f"Queue id not found, available queues: {', '.join(queue_ids)}",
                    )
                else:
                    raise HTTPException(
                        status_code=queues_response.status_code,
                        detail="Failed to retrieve available queues",
                    )

            case _:
                raise HTTPException(
                    status_code=export_response.status_code,
                    detail="Unexpected error occurred while fetching annotations",
                )
