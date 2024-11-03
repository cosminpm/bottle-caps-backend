import os
from functools import wraps

import cv2
import numpy as np
from loguru import logger

from app.config import Settings

settings = Settings()


def save_img(output_path: str):
    """Save the result the image result of a function if the environment variable is on.

    Args:
    ----
        output_path (str): Where the image will be saved.

    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if settings.save_image:
                if isinstance(result, np.ndarray):
                    cv2.imwrite(output_path, result)
                    logger.info(f"Array saved as image to {output_path}.")
                else:
                    logger.error("Result is not a NumPy array.")
            return result

        return wrapper

    return decorator
