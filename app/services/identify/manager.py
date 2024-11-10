from pathlib import Path

from numpy import ndarray

from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import apply_mask

PROJECT_PATH = Path.cwd()


def identify_cap(cap: ndarray, user_id: str) -> list[dict]:
    """Identify a cap from the Pinecone database.

    Args:
    ----
        cap: The cap.
        user_id: The user_id of the person

    Returns:
    -------
        The cap model with all the information.

    """
    pinecone_container: PineconeContainer = PineconeContainer()
    image_vectorizer: ImageVectorizer = ImageVectorizer()
    img = apply_mask(cap)
    vector = image_vectorizer.numpy_to_vector(img=img)
    result = pinecone_container.query_with_metadata(vector=vector, metadata={"user_id": user_id})
    return [cap.to_dict() for cap in result]
