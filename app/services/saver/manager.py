import asyncio
import uuid
from typing import TYPE_CHECKING

from fastapi import UploadFile

from app.services.firebase_container import FirebaseContainer
from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import resize_image_max_size

if TYPE_CHECKING:
    import numpy as np


async def save_image_progress(
    file: UploadFile,
    name: str,
    user_id: str,
    progress_callback: asyncio.Event,
    vector: list[float] | None = None,
):
    """Asynchronously saves an image and triggers a progress callback once completed.

    Args:
    ----
        file (UploadFile): The image file to be uploaded.
        name (str): The name for the image.
        user_id (str): Unique user identifier.
        progress_callback (asyncio.Event): Event to signal when the upload is complete.
        vector (list[float] | None, optional): Optional vector data associated with the image.

    Returns:
    -------
        str: URL of the uploaded image.

    """
    url_upload = await save_image(file=file, name=name, user_id=user_id, vector=vector)
    progress_callback.set()
    return url_upload


async def save_image(
    file: UploadFile,
    name: str,
    user_id: str,
    vector: list[float] | None = None,
) -> str:
    """Add an image it will upload it to Firebase and Pinecone.

    Args:
    ----
        file (UploadFile): The image.
        name (str): The name.
        user_id (str): The user id.
        vector (list[float]): The vector to save in Pinecone.

    Returns:
    -------
    The path of the firebase image.

    """
    if not vector:
        vector = await ImageVectorizer().image_to_vector(file)
    pinecone_container: PineconeContainer = PineconeContainer()
    firebase_container: FirebaseContainer = FirebaseContainer()
    file_name: str = f"{name}.jpg"

    image: np.ndarray = resize_image_max_size(file)
    upload_url: str = firebase_container.add_image_to_container(image, file_name, user_id)
    pinecone_container.upsert_into_pinecone(
        vector_id=str(uuid.uuid4()), values=vector, metadata={"user_id": user_id, "name": file_name}
    )
    return upload_url


def remove_image(
    name: str,
    user_id: str,
) -> None:
    """Delete an image.

    Args:
    ----
        name (str): The name of the image
        user_id (str): The id of the user

    """
    pinecone_container: PineconeContainer = PineconeContainer()
    firebase_container: FirebaseContainer = FirebaseContainer()
    firebase_container.remove_image(name=name, user_id=user_id)
    pinecone_container.remove_vector(name=name, user_id=user_id)
