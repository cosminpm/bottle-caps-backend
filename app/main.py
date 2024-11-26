from contextlib import asynccontextmanager
from typing import Any

import cv2
import numpy as np
import requests
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from pyinstrument import Profiler
from requests import Request
from starlette import status

load_dotenv()

from app.config import Settings
from app.services.detect.manager import detect_caps
from app.services.identify.manager import identify_cap
from app.services.saver.router import saver_router
from app.shared.utils import img_to_numpy


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Ping the server so it does not shut down."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(func=call_healthcheck, trigger="interval", seconds=14 * 60)
    scheduler.start()
    yield


app = FastAPI(lifespan=lifespan)
settings = Settings()

origins = [
    "*",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(saver_router)

# Profiling
if settings.profiling_time:

    @app.middleware("http")
    async def profile_time_request(request: Request, call_next: Any) -> Any:
        """Profile the request."""
        profiler = Profiler(interval=0.01, async_mode="enabled")
        profiler.start()
        response = await call_next(request)
        profiler.stop()
        profiler.open_in_browser()
        return response


def call_healthcheck():
    """Call this server to ensure it's responding."""
    endpoint_url = "https://bottle-caps-backend.onrender.com/health"
    response = requests.get(endpoint_url, timeout=60)
    if response.status_code == status.HTTP_200_OK:
        logger.info("Successfully hit the endpoint")
    else:
        logger.error(f"Failed to hit endpoint. Status code: {response.status_code}")


@app.get("/health")
def health_check():
    """Healthcheck."""
    return status.HTTP_200_OK


def post_detect_and_identify(file_contents: bytes, user_id: str) -> dict:
    """Detect and indentify a bottle cap.

    Args:
    ----
        file_contents: The raw content.
        user_id: The user_id of the person.

    Returns:
    -------
        A dictionary containing all the necessary information.

    """
    image = cv2.imdecode(np.frombuffer(file_contents, np.uint8), cv2.IMREAD_COLOR)
    image = img_to_numpy(image)
    cropped_images = detect_caps(image)
    caps_identified = [
        identify_cap(cap=np.array(cap[0]), user_id=user_id) for cap in cropped_images
    ]

    positions = [tuple(int(v) for v in rct) for (img, rct) in cropped_images]

    return {"positions": positions, "caps_identified": caps_identified}


@app.post("/detect_and_identify")
async def detect_and_identify(file: UploadFile, user_id: str):
    """Detect and identify an image containing multiple bottle caps.

    Args:
    ----
        file:  The file we are going to process.
        user_id: The user_id of the person.

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


@app.post("/detect")
async def detect(file: UploadFile) -> list:
    """Detect bottle caps in an image.

    Args:
    ----
        file: The file we are going to detect the images.

    Returns:
    -------
        The list of positions were the caps where detected.

    """
    image = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)
    image = img_to_numpy(image)
    cropped_images = detect_caps(image)
    return [tuple(int(v) for v in rct) for (img, rct) in cropped_images]


@app.post("/identify")
async def identify(file: UploadFile, user_id: str) -> list[dict]:
    """Identify the bottle cap of an image.

    Args:
    ----
        file: The file we are going to identify in an image.
        user_id: The user_id of the person.

    Returns:
    -------
        The result of the identification of the bottle cap in a dictionary.

    """
    image = cv2.imdecode(np.frombuffer(await file.read(), np.uint8), cv2.IMREAD_COLOR)
    return identify_cap(cap=np.array(image), user_id=user_id)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.host, port=settings.port)
