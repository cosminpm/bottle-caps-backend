import os
from pathlib import Path

from dotenv import load_dotenv

from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import read_img_from_path_with_mask

PROJECT_PATH = Path.cwd()
load_dotenv()


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
        cap_info = {"id": img_path, "values": vector}
        pinecone_container.upsert_dict_pinecone(cap_info=cap_info)


if __name__ == "__main__":
    fill_vector_database()
