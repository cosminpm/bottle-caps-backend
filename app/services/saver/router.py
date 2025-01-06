import asyncio

from fastapi import APIRouter, Depends, UploadFile
from starlette.requests import Request

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


@saver_router.post("/saver/bulk")
@request_limiter.limit(LIMIT_PERIOD)
async def post_save_images(
    files: list[UploadFile],
    user_id: str,
    request: Request,
) -> None:
    """Save multiple images."""
    tasks = []

    for file in files:
        name = file.filename
        task = save_image(file, name, user_id)
        tasks.append(task)
    await asyncio.gather(*tasks)


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
