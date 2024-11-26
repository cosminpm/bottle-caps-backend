import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import read_img_from_path_with_mask

PROJECT_PATH = Path.cwd()


def fill_vector_database() -> None:
    """Fill the Pinecone database with the images that are inside the caps folder."""
    pinecone_container = PineconeContainer()
    pinecone_container.empty_index()
    root_dir = str(Path("database") / "caps")
    folders = os.listdir(root_dir)
    img_vectorizer = ImageVectorizer()
    for img_path in folders:
        file_path: str = str(Path(root_dir) / img_path)
        img = read_img_from_path_with_mask(file_path)
        vector = img_vectorizer.numpy_to_vector(img=img)
        pinecone_container.upsert_into_pinecone(
            vector_id=img_path, values=vector, metadata={"user_id": "test_user", "name": img_path}
        )


if __name__ == "__main__":
    fill_vector_database()
