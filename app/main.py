from fastapi import FastAPI
from fastapi.security import HTTPBasicCredentials
from fastapi.param_functions import Depends

from .transform_xml import (
    transform_invoice_xml,
    filter_xml_by_annotation_id,
    xml_to_base64,
)

from .auth import authenticate
from .requests.postbin import post_json, create_bin
from .requests.rossum import rossum_login, get_annotations

# Initialize FastAPI app
app = FastAPI()


@app.get("/export", status_code=200)
async def get_usage_form(
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    # This is the endpoint that returns usage instructions
    usage = {
        "message": "To export data, use the following endpoint format:",
        "endpoint": "/export/queue_id/{queue_id}/annotation_id/{annotation_id}",
        "example": "/export/queue_id/123/annotation_id/456",
        "description": "Replace {queue_id} and {annotation_id} with appropriate integer values.",
    }
    return usage


@app.get("/export/queue_id/{queue_id}/annotation_id/{annotation_id}", status_code=200)
async def export_data(
    annotation_id: int,
    queue_id: int,
    credentials: HTTPBasicCredentials = Depends(authenticate),
):
    try:
        # Get credentials
        headers = await rossum_login()

        # Get queues
        annotations = await get_annotations(queue_id, headers)

        # Filter annotations
        annotation = filter_xml_by_annotation_id(
            xml_str=annotations, annotation_id=annotation_id
        )

        # Transform XML
        xml = transform_invoice_xml(annotation)

        # Convert XML to base64
        base64_xml = xml_to_base64(xml)
        json_data = {
            "annotationId": annotation_id,
            "content": base64_xml,
        }

        # Create bin and get its url
        bin_url = await create_bin()

        post_url = bin_url.replace("api/bin/", "")

        # Post JSON to bin
        await post_json(json_data, post_url)

        return {"success": True, "bin_url": bin_url.replace("api/bin", "b")}

    except Exception as e:
        return {"success": False, "error": str(e)}
