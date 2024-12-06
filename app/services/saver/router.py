import uuid

import numpy as np
from fastapi import APIRouter, Depends, UploadFile
from starlette.requests import Request

from app.config import LIMIT_PERIOD
from app.services.auth import validate_api_key
from app.services.firebase_container import FirebaseContainer
from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.limiter import request_limiter
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import resize_image_width

saver_router: APIRouter = APIRouter(dependencies=[Depends(validate_api_key)])


@saver_router.post("/saver", tags=["Saver"])
@request_limiter.limit(LIMIT_PERIOD)
async def save_image(
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
    if not vector:
        vector = await ImageVectorizer().image_to_vector(file)
    pinecone_container: PineconeContainer = PineconeContainer()
    firebase_container: FirebaseContainer = FirebaseContainer()
    file_name: str = f"{name}.jpg"

    image: np.ndarray = resize_image_width(file)
    upload_url: str = firebase_container.add_image_to_container(image, file_name, user_id)
    pinecone_container.upsert_into_pinecone(
        vector_id=str(uuid.uuid4()), values=vector, metadata={"user_id": user_id, "name": file_name}
    )
    return upload_url
