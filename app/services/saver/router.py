import uuid

from fastapi import APIRouter, UploadFile

from app.services.firebase_container import FirebaseContainer
from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer

saver_router: APIRouter = APIRouter()


@saver_router.post("/saver/", tags=["Saver"])
async def save_image(file: UploadFile, name: str, user_id: str, vector: list[float] | None = None) -> str:
    """Save an image into saver.

    Args:
    ----
        file (UploadFile): The file.
        name (str): The name of the file.
        user_id (str): The user_id that is uploading the file.
        vector (list[float]): The vector we are going to save in pinecone

    Returns:
    -------
        A public string that show us where the bottle cap it is.

    """
    if not vector:
        vector = ImageVectorizer().image_to_vector(file)
    pinecone_container: PineconeContainer = PineconeContainer()
    firebase_container: FirebaseContainer = FirebaseContainer()

    pinecone_container.upsert_into_pinecone(
        vector_id=str(uuid.uuid4()), values=vector, metadata={"user_id": user_id, "name": name}
    )
    return firebase_container.add_image_to_container(file, name, user_id)
