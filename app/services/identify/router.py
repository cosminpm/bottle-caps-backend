import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import LIMIT_PERIOD
from app.services.auth import validate_api_key
from app.services.identify.manager import identify_cap, post_detect_and_identify
from app.services.limiter import request_limiter
from app.shared.utils import resize_image_width

identify_router: APIRouter = APIRouter(dependencies=[Depends(validate_api_key)])


@identify_router.post("/identify")
@request_limiter.limit(LIMIT_PERIOD)
async def identify(file: UploadFile, user_id: str, request: Request) -> list[dict]:
    """Identify the bottle cap of an image.

    Args:
    ----
        file: The file we are going to identify in an image.
        user_id: The user_id of the person.
        request (Request): Needed for the limiter

    Returns:
    -------
        The result of the identification of the bottle cap in a dictionary.

    """
    image = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)
    image = resize_image_width(image)
    return identify_cap(cap=np.array(image), user_id=user_id)


@identify_router.post("/detect_and_identify")
@request_limiter.limit(LIMIT_PERIOD)
async def detect_and_identify(file: UploadFile, user_id: str, request: Request):
    """Detect and identify an image containing multiple bottle caps.

    Args:
    ----
        file:  The file we are going to process.
        user_id: The user_id of the person.
        request (Request): Needed for the limiter

    Returns:
    -------
        A json response containing the main information.

    """
    result = post_detect_and_identify(await file.read(), user_id=user_id)
    return JSONResponse(
        content={
            "filename": file.filename,
            "positions": result["positions"],
            "caps": result["caps_identified"],
        }
    )
