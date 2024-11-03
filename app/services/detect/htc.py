import os

import cv2
import numpy as np
from loguru import logger
from numpy import ndarray, uint16

multiplier_left_max_radius = 0.8
multiplier_right_max_radius = 1


def combine_overlapping_circles(circles: uint16) -> list[tuple[int, int, int]]:
    """Combine all the overlapping circles.

    Args:
    ----
        circles: The circles to combine.

    Returns:
    -------
        A list with all the circles.

    """
    circles = np.round(circles[0, :]).astype("int")
    combined_circles = []
    for x, y, r in circles:
        found_overlap = False
        for cx, cy, cr in combined_circles:
            if (x - cx) ** 2 + (y - cy) ** 2 < (r + cr) ** 2:
                found_overlap = True
                break
        if not found_overlap:
            combined_circles.append((x, y, r))
    return combined_circles


def hough_transform_circle(original_img: np.ndarray, max_radius: int) -> list[tuple[int, int, int]]:
    """Return the final circles after HTC transformation.

    Args:
    ----
        original_img: The image where we are going to find the circles.
        max_radius: The maximum radius of a bottlecap.

    Returns:
    -------
        A list with all the circles.

    """
    img = original_img.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (5, 5), 0)

    circles = cv2.HoughCircles(
        img,
        cv2.HOUGH_GRADIENT,
        1,
        20,
        param1=50,
        param2=18,
        minRadius=int(max_radius * multiplier_left_max_radius),
        maxRadius=int(max_radius * multiplier_right_max_radius),
    )
    circles: uint16 = np.uint16(np.around(circles))

    return combine_overlapping_circles(circles)


def _draw_img(img: ndarray, circles, env_var_name: str = "SAVE_IMG"):
    if os.getenv(env_var_name):
        circles_img = img.copy()
        circles = np.uint16(np.around(circles))
        for i in circles:
            # Draw the circle in the image
            center = (i[0], i[1])  # Center coordinates
            radius = i[2]  # Radius
            cv2.circle(circles_img, center, radius, (0, 255, 0), 2)
            cv2.circle(circles_img, center, 2, (0, 0, 255), 3)
        output_path: str = "./animations/pp_4.png"
        cv2.imwrite(output_path, circles_img)
        logger.info(f"Array saved as image to {output_path}.")
