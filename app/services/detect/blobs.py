import os

import cv2
import numpy as np
from loguru import logger
from numpy import ndarray

from app.config import Settings
from app.shared.save_img_decorator import save_img

DEBUG_BLOB = 1
DEBUG_PREPROCESS_BLOBS = 0
PREPO_number_of_levels = 3
PREPO_convolution_size = 15
percent_min_area_of_original = 0.01
percent_max_area_of_original = 0.99

settings = Settings()

@save_img(output_path="./animations/pp_1.png")
def reduce_colors_images(image: ndarray, n_colors: int) -> ndarray:
    """Reduce the number of colors to a specific number.

    Args:
    ----
        image: The image we are going to reduce.
        n_colors (int): The number of colors to reduce.

    Returns:
    -------
    The reduced image.

    """
    pixels = image.reshape((-1, 3)).astype(np.float32)

    # Perform k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags: int = cv2.KMEANS_RANDOM_CENTERS
    compactness, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)

    # Convert the labels back to an image
    quantized = centers[labels]
    return quantized.reshape(image.shape).astype(np.uint8)


@save_img(output_path="./animations/pp_2.png")
def preprocess_image_blobs(image: ndarray) -> ndarray:
    """Preprocess the image to make the detection of the blobs easier.

    Args:
    ----
        image (ndarray): The image we are going to preprocess.

    Returns:
    -------
        The preprocessed image.

    """
    img = cv2.GaussianBlur(image, (PREPO_convolution_size, PREPO_convolution_size), 0)
    img = reduce_colors_images(img, PREPO_number_of_levels)
    if DEBUG_PREPROCESS_BLOBS:
        cv2.imshow("Preprocess img", img)
        cv2.waitKey(0)
    return img


def get_avg_size_all_blobs(img: ndarray) -> int:
    """Get the average size of the blobs.

    Args:
    ----
        img: Image we are going to analyze.

    Returns:
    -------
        The average size of the blobs.

    """
    img = preprocess_image_blobs(img)
    params = cv2.SimpleBlobDetector_Params()

    # Parameters of SimpleBlobDetector
    # For Area
    params.filterByArea = True
    params.minArea = img.shape[0] * img.shape[1] * percent_min_area_of_original
    params.maxArea = img.shape[0] * img.shape[1] * percent_max_area_of_original
    params.filterByCircularity = False
    params.filterByConvexity = False

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(img)
    keypoints = _remove_overlapping_blobs(keypoints=keypoints)

    if len(keypoints) == 0:
        return 0
    return int(_get_avg_size_blobs(keypoints) / 2)


def _save_img(img: ndarray, keypoints):
    if settings.save_image:
        blobs_img = cv2.drawKeypoints(
            img.copy(),
            keypoints,
            np.array([]),
            (0, 0, 255),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )
        output_path: str = "./animations/pp_3.png"
        cv2.imwrite(output_path, blobs_img)
        logger.info(f"Array saved as image to {output_path}.")


def _get_avg_size_blobs(kps: list):
    kps_size = [int(kp.size) for kp in kps]
    lst = sorted(kps_size)
    if len(lst) % 2 == 1:
        # List has an odd number of elements
        result = int(lst[len(lst) // 2])
    else:
        # List has an even number of elements
        mid1 = int(lst[(len(lst) // 2) - 1])
        mid2 = int(lst[len(lst) // 2])
        result = max(mid2, mid1)
    return result


def _remove_overlapping_blobs(keypoints: list):
    boxes = []
    for kp in keypoints:
        x, y = int(kp.pt[0]), int(kp.pt[1])
        r = int(kp.size / 2)
        box = (x - r, y - r, x + r, y + r)
        boxes.append(box)

    # Iterate over the blobs and mark overlapping ones
    overlapping = [False] * len(keypoints)
    for i, box in enumerate(boxes):
        if overlapping[i]:
            continue
        for j, other_box in enumerate(boxes[i + 1 :]):
            if (
                box[0] < other_box[2]
                and box[2] > other_box[0]
                and box[1] < other_box[3]
                and box[3] > other_box[1]
            ):
                overlapping[i + j + 1] = True

    # Keep only the non-overlapping blobs
    filtered_keypoints = []
    for i, kp in enumerate(keypoints):
        if not overlapping[i]:
            filtered_keypoints.append(kp)
    return filtered_keypoints
