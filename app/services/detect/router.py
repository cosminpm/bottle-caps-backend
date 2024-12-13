import cv2
import numpy as np
from fastapi import APIRouter, Depends, UploadFile
from starlette.requests import Request

from app.config import LIMIT_PERIOD
from app.services.auth import validate_api_key
from app.services.detect.manager import detect_caps
from app.services.limiter import request_limiter
from app.shared.utils import img_to_numpy

detect_router: APIRouter = APIRouter(dependencies=[Depends(validate_api_key)], tags=["Detect"])


@detect_router.post("/detect")
@request_limiter.limit(LIMIT_PERIOD)
async def detect(file: UploadFile, request: Request) -> list:
    """Detect bottle caps in an image.

    Args:
    ----
        file: The file we are going to detect the images.
        request (Request): Needed for the limiter

    Returns:
    -------
        The list of positions were the caps where detected.

    """
    image = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)
    image = img_to_numpy(image)
    cropped_images = detect_caps(image)
    return [tuple(int(v) for v in rct) for (img, rct) in cropped_images]
