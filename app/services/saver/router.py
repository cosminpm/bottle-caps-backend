from fastapi import APIRouter, UploadFile
import uuid
from app.main import firebase_container, pinecone_container

saver_router: APIRouter = APIRouter()


@saver_router.post("/saver/", tags=["Saver"])
async def save_image(file: UploadFile, name: str, user_id: str, vector: list[float]) -> str:
    """Save an image into saver.

    Args:
    ----
        file (UploadFile): The file.
        name (str): The name of the file.
        user_id (user_id): The user_id that is uploading the file.

    Returns:
    -------
        A public string that show us where the bottle cap it is.

    """
    pinecone_container.upsert_into_pinecone(vector_id=str(uuid.uuid4()), values=vector, metadata={
        "user_id": user_id,
        "name": name
    })
    return firebase_container.add_image_to_container(file, name, user_id)
