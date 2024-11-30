import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


from app.services.firebase_container import FirebaseContainer
from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import read_img_from_path_with_mask, upload_file

if TYPE_CHECKING:
    from fastapi import UploadFile

PROJECT_PATH = Path.cwd()


async def fill_vector_database() -> None:
    """Fill the Pinecone database with the images that are inside the caps folder."""
    pinecone_container = PineconeContainer()
    firebase_container = FirebaseContainer()

    pinecone_container.empty_index()
    root_dir = str(Path("database") / "caps")
    folders = os.listdir(root_dir)
    img_vectorizer = ImageVectorizer()
    for indx, img_path in enumerate(folders):
        file_path: Path = Path(root_dir) / img_path

        img = read_img_from_path_with_mask(str(file_path))
        vector = img_vectorizer.numpy_to_vector(img=img)

        file: UploadFile = await upload_file(file_path)
        firebase_container.add_image_to_container(file, img_path, "test_user")
        pinecone_container.upsert_into_pinecone(
            vector_id=img_path, values=vector, metadata={"user_id": "test_user", "name": img_path}
        )
        logger.info(f"A total of {indx}/{len(folders)} have been uploaded.")


if __name__ == "__main__":
    asyncio.run(fill_vector_database())
