import os
import uuid
from pathlib import Path

import cv2
import keras
import numpy as np
import tensorflow as tf
from dotenv import load_dotenv
from keras import Sequential
from keras.src.applications.resnet import ResNet50
from keras.src.layers import Dense, Flatten
from keras.src.saving import load_model

from app.services.identify.manager import image_to_vector
from app.services.identify.pinecone_container import PineconeContainer
from app.shared.utils import _apply_mask, _read_img_from_path_with_mask

PROJECT_PATH = Path.cwd()
load_dotenv()


def create_img_training(name: str, folder_create: str, path_all_images: str) -> None:
    """Create the training image for the model.

    Args:
    ----
        name: The name of the cap.
        folder_create: Where to create the img.
        path_all_images: The full path.

    """
    folder_name = Path(name).stem
    folder_result = Path(folder_create) / folder_name

    if not folder_result.exists():
        folder_result.mkdir(parents=True)
        path_img = Path(path_all_images) / name
        img = _read_img_from_path_with_mask(str(path_img))
        cv2.imwrite(str(folder_result / name), img)


def create_training_folder() -> None:
    """Create the training folder that's going to be used to train the model."""
    path_all_images = str(Path("database") / "caps-resized")
    folder_create = str(Path("database") / "training")

    names_images = os.listdir(path=path_all_images)
    for name in names_images:
        create_img_training(name=name, folder_create=folder_create, path_all_images=path_all_images)


def create_model() -> Sequential:
    """Create the Keras model that it's going to be used.

    Returns
    -------
        A Keras model to identify bottle caps.

    """
    img_size = 224
    model = Sequential()
    base_model = ResNet50(
        weights="imagenet",
        include_top=False,
        input_shape=(img_size, img_size, 3),
        pooling="max",
    )
    model.add(base_model)
    model.add(Flatten())

    model.add(Dense(2048, activation="relu"))

    model.compile("adam", loss=tf.losses.CategoricalCrossentropy(), metrics=["accuracy"])
    model.summary()
    return model


def transform_imag_to_pinecone_format(img: np.ndarray, model: keras.Sequential, metadata) -> dict:
    """Transform an image to pinecone format, so we can upload it into the vector database.

    Args:
    ----
        img: The image.
        model: The keras model.
        metadata: The medatada of the model.

    Returns:
    -------
        A dictionary with all the metadata information frpm pinecone.

    """
    img = _apply_mask(img)
    vector = image_to_vector(img=img, model=model)

    return {"id": str(uuid.uuid4()), "values": vector, "metadata": metadata}


def generate_vector_database(
    pinecone_container: PineconeContainer, model: keras.Sequential
) -> None:
    """Create the vector database for pinecone connection.

    Args:
    ----
        pinecone_container: The pinecone container.
        model: The keras model

    """
    root_dir = str(Path("database") / "caps")
    folders = os.listdir(root_dir)
    for img_path in folders:
        file_path: str = str(Path(root_dir) / img_path)
        img = _read_img_from_path_with_mask(file_path)
        vector = image_to_vector(img=img, model=model)
        cap_info = {"id": img_path, "values": vector}
        pinecone_container.upsert_one_pinecone(cap_info=cap_info)


def get_model() -> keras.Sequential:
    """Get the model.

    Returns
    -------
        The keras model.

    """
    path = str(Path(PROJECT_PATH) / "app" / "models" / "model.keras")
    return load_model(path)


def generate_model(pinecone_container: PineconeContainer) -> None:
    """Generate the model where we are going to save the bottle caps and the model used to identify.

    Args:
    ----
        pinecone_container: The pinecone container.


    """
    model = create_model()
    path_model: str = str(Path(PROJECT_PATH) / "app" / "models" / "model.keras")
    model.save(path_model)
    model = get_model()
    generate_vector_database(pinecone_container=pinecone_container, model=model)


if __name__ == "__main__":
    pinecone_container = PineconeContainer()
    pinecone_container.empty_index()
    # generate_model(pinecone_container=pinecone_container)
    generate_vector_database(pinecone_container, get_model())