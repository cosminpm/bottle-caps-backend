import os
from typing import Dict

import cv2
import keras
import numpy as np
from keras.applications import ResNet50
from keras.layers import Dense, Flatten
from keras.models import load_model, Sequential
from matplotlib import pyplot as plt
from PIL import Image
import tensorflow as tf

from ScriptsMain.Pinecone import PineconeContainer, image_to_vector
from ScriptsMain.UtilsFun import read_img_from_path_with_mask, read_img_with_mask

PROJECT_PATH = os.path.abspath(os.path.join(os.getcwd(), os.pardir))


def create_img_training(name: str, folder_create: str, path_all_images: str):
    folder_name = os.path.splitext(name)[0]
    folder_result = os.path.join(folder_create, folder_name)

    if not os.path.exists(folder_result):
        os.makedirs(folder_result)
        path_img = os.path.join(path_all_images, name)
        img = read_img_from_path_with_mask(path_img)
        cv2.imwrite(os.path.join(folder_result, name), img)


def create_training_folder():
    path_all_images = os.path.join(PROJECT_PATH, 'database', 'caps-resized')
    folder_create = os.path.join(PROJECT_PATH, 'training')

    names_images = os.listdir(path=path_all_images)
    for name in names_images:
        create_img_training(name=name, folder_create=folder_create, path_all_images=path_all_images)


def create_model():
    img_size = 224

    model = Sequential()

    base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(img_size, img_size, 3), pooling='max')

    model.add(base_model)

    model.add(Flatten())

    model.add(Dense(256, activation='relu'))  # Add fully connected layers

    model.compile('adam', loss=tf.losses.CategoricalCrossentropy(), metrics=['accuracy'])
    model.summary()
    return model


def generate_vector_database(pinecone_container, model: keras.Sequential):
    root_dir = os.path.join(PROJECT_PATH, 'training')
    folders = os.listdir(root_dir)
    for folder in folders:
        folder = os.path.join(root_dir, folder)
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            img = read_img_from_path_with_mask(path)
            vector = image_to_vector(img=img, model=model)
            cap_info = {
                'id': file,
                'values': vector
            }
            pinecone_container.upsert_to_pinecone(vector=cap_info)


def save_model(model, path):
    model.save(path)


def get_model() -> keras.Sequential:
    path = os.path.join(PROJECT_PATH, 'model')
    return load_model(path)


def generate_all(pinecone_container: PineconeContainer):
    model = create_model()
    path_model = os.path.join(PROJECT_PATH, 'model')
    save_model(model=model, path=path_model)
    model = get_model()
    generate_vector_database(pinecone_container=pinecone_container, model=model)


def show_similar_images(org_img: str, match_result: Dict):
    images = [os.path.join(PROJECT_PATH, 'training', match['id'].split('.')[0], match['id']) for match in
              match_result['matches']]
    values = ["{:.3f}".format(match['score']) for match in match_result['matches']]
    show_images(images, org_img, values)


def show_images(images, specific_image_path, values):
    num_images = len(images) + 1
    rows = int(np.ceil(np.sqrt(num_images)))
    cols = int(np.ceil(num_images / rows))

    fig, axes = plt.subplots(rows, cols)

    specific_image = Image.open(specific_image_path)
    axes[0, 0].imshow(specific_image)
    axes[0, 0].axis('off')

    for i, ax in enumerate(axes.flatten()[1:]):
        if i < num_images - 1:
            image_path = images[i]
            image = Image.open(image_path)
            ax.imshow(image)
            ax.axis('off')
            ax.text(0.5, -0.2, values[i], ha='center', transform=ax.transAxes)
        else:
            ax.axis('off')

    plt.tight_layout()
    plt.show()


def identify_cap(cap: np.ndarray, pinecone_container: PineconeContainer, model: keras.Sequential):
    img = read_img_with_mask(cap)
    vector = image_to_vector(img=img, model=model)
    result = pinecone_container.query_database(vector=vector)
    return result


def main():
    pinecone_container = PineconeContainer()
    model: keras.Sequential = get_model()

    path = r'database/test-images/one-image/7.png'
    cap_path = os.path.join(PROJECT_PATH, path)

    img = read_img_from_path_with_mask(cap_path)
    vector = image_to_vector(img=img, model=model)
    result = pinecone_container.query_database(vector=vector)
    # show_similar_images(cap_path, result)


if __name__ == '__main__':
    # create_training_folder()
    # pinecone_container = PineconeContainer()
    # generate_all(pinecone_container)
    main()