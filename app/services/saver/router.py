import asyncio
import json

from fastapi import APIRouter, Depends, UploadFile
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
    return await save_image(file, name, user_id, vector)


from io import BytesIO


@saver_router.post("/saver/bulk")
async def post_save_images(
    files: list[UploadFile],
    user_id: str,
    request: Request,
) -> StreamingResponse:
    """Save multiple images and send progress updates via SSE."""
    total_files = len(files)
    progress_queue = asyncio.Queue()
    update_event = asyncio.Event()

    file_buffers = [{"filename": file.filename, "buffer": await file.read()} for file in files]

    async def worker():
        for idx, file in enumerate(file_buffers):
            try:
                fake_upload_file = UploadFile(
                    filename=file["filename"], file=BytesIO(file["buffer"])
                )
                await save_image(fake_upload_file, file["filename"], user_id)
            finally:
                await progress_queue.put(
                    {
                        "processed": idx + 1,
                        "total": total_files,
                        "percentage": (idx + 1) / total_files,
                    }
                )
                update_event.set()

    async def event_generator():
        processed = 0
        while processed < total_files:
            await update_event.wait()
            while not progress_queue.empty():
                data = await progress_queue.get()
                yield f"data: {json.dumps(data)}\n\n"
                processed = data["processed"]
            update_event.clear()

    asyncio.create_task(worker())  # noqa: RUF006

    return StreamingResponse(event_generator(), media_type="text/event-stream")


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
