from io import BytesIO
from pathlib import Path

import aiofiles
import cv2
import numpy as np
import starlette.datastructures
from fastapi import UploadFile

SIFT = cv2.SIFT_create()
MAX_SIZE: int = 256


def _get_name_from_path(path: str) -> str:
    return path.split("\\")[-1]


def read_img_from_path_with_mask(img_path: str) -> np.ndarray:
    """Transform a path image of a cap and apply a black mask to it.

    Args:
    ----
        img_path (str): The path of the image.

    Returns:
    -------
        The ndarray of the mask.

    """
    return apply_mask(cv2.imread(img_path))


def apply_mask(image: np.ndarray) -> np.ndarray:
    """Apply a mask of the ndarray cap, basically removing the background of the bottle-cap.

    Args:
    ----
        image ( np.ndarray): The img that we are going to apply the mask.

    Returns:
    -------
        The img with a mask

    """
    height, width, _ = image.shape
    size = min(width, height)
    center_x, center_y = width // 2, height // 2
    radius = size // 2

    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(mask, (center_x, center_y), radius, (255), thickness=-1)

    return cv2.bitwise_and(image, image, mask=mask)


def read_img_from_path(img_path: str) -> np.ndarray:
    """Read image from path.

    Args:
    ----
        img_path: The path of the image

    Returns:
    -------
        The numpy array of the image.

    """
    return cv2.cvtColor(cv2.imread(img_path), 1)


def img_to_numpy(img) -> np.ndarray:
    """Convert an img into a numpy array.

    Args:
    ----
        img: Image to convert

    Returns:
    -------
        The numpy img

    """
    return cv2.cvtColor(img, 1)


def rgb_to_bgr(r: int, g: int, b: int) -> tuple:
    """Reorder RGB image to BGR image.

    Args:
    ----
        r: red value
        g: green value
        b: blue value

    Returns:
    -------
    Tuple of BGR.

    """
    return b, g, r


async def upload_file(path: Path) -> UploadFile:
    """Given a path to a file, mimic it as it was uploaded by the FastAPI framework.

    Args:
    ----
        path (Path): Path to the file.

    Returns:
    -------
    The uploaded file.

    """
    async with aiofiles.open(path, mode="rb") as file:
        file_contents = await file.read()
        return UploadFile(filename=str(path), file=BytesIO(file_contents))


def resize_image_max_size(image: np.ndarray | UploadFile) -> np.ndarray:
    """Resize the image so its maximum dimension (width or height) is less than or equal to 512.

    Can accept both np.ndarray and uploaded image files.
    """
    if isinstance(image, (UploadFile | starlette.datastructures.UploadFile)):
        image_bytes = image.file.read()
        image_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError("Failed to load image. Ensure the file is a valid image format.")

    height, width = image.shape[:2]
    max_dimension = max(height, width)

    if max_dimension > MAX_SIZE:
        scale_factor = MAX_SIZE / max_dimension
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return image
