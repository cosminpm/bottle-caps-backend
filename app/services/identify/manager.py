from pathlib import Path

import cv2
import numpy as np
from numpy import ndarray

from app.services.detect.manager import detect_caps
from app.services.identify.image_vectorizer import ImageVectorizer
from app.services.pinecone_container import PineconeContainer
from app.shared.utils import apply_mask, img_to_numpy, resize_image_width

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
    return [{"name": cap["metadata"]["name"], "score": cap["score"]} for cap in result]


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
    image = resize_image_width(image)
    image = img_to_numpy(image)
    cropped_images = detect_caps(image)
    caps_identified = [
        identify_cap(cap=np.array(cap[0]), user_id=user_id) for cap in cropped_images
    ]

    positions = [tuple(int(v) for v in rct) for (img, rct) in cropped_images]

    return {"positions": positions, "caps_identified": caps_identified}
