import asyncio
import json

from fastapi import APIRouter, Depends, UploadFile
from loguru import logger
from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.config import LIMIT_PERIOD
from app.services.auth import validate_api_key
from app.services.limiter import request_limiter
from app.services.saver.manager import remove_image, save_image

saver_router: APIRouter = APIRouter(dependencies=[Depends(validate_api_key)], tags=["Saver"])


@saver_router.post("/saver")
@request_limiter.limit(LIMIT_PERIOD)
async def post_save_image(
    file: UploadFile,
    name: str,
    user_id: str,
    request: Request,
    vector: list[float] | None = None,
) -> str:
    """Save an image into saver.

    Args:
    ----
        file (UploadFile): The file.
        name (str): The name of the file.
        user_id (str): The user_id that is uploading the file.
        vector (list[float]): The vector we are going to save in pinecone
        request (Request): Needed for the limiter

    Returns:
    -------
        A public string that show us where the bottle cap it is.

    """
    file_data = await file.read()
    return await save_image(file_data, name, user_id, vector)


@saver_router.post("/saver/bulk")
async def post_save_images(
    files: list[UploadFile],
    user_id: str,
    request: Request,
) -> StreamingResponse:
    """Save multiple images and send progress updates via SSE."""
    files_data = [(await data.read(), data.filename) for data in files]
    total_images: int = len(files)

    async def event_stream():
        tasks = [save_image(file, name, user_id) for file, name in files_data]
        for index, coro in enumerate(asyncio.as_completed(tasks)):
            try:
                await coro
                data = {"processed": index, "total": total_images}
                yield f"data: {json.dumps(data)}\n\n"
                logger.info(f" Bulk upload succeeded {user_id}: {index}")

            except Exception as e:  # noqa: BLE001
                yield f"data:{e!s}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@saver_router.delete("/delete")
@request_limiter.limit(LIMIT_PERIOD)
async def delete_image(
    name: str,
    user_id: str,
    request: Request,
) -> None:
    """Delete an image.

    Args:
    ----
        name (str): The name of the image
        user_id (str): The id of the user
        request (Request): Needed for the limiter

    """
    remove_image(name, user_id)
