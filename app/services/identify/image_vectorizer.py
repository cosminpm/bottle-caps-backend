import io

import cv2
import numpy as np
import torch
from fastapi import UploadFile
from torchvision import models, transforms

from app.shared.utils import apply_mask


class ImageVectorizer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()

        self.preprocess = transforms.Compose(
            [
                transforms.ToPILImage(),
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    async def image_to_vector(self, cap: UploadFile) -> list:
        file_data = await cap.read()
        image = cv2.imdecode(np.frombuffer(file_data, np.uint8), cv2.IMREAD_COLOR)
        img = apply_mask(np.array(image))

        # Reset the file pointer
        cap.file = io.BytesIO(file_data)

        return self.numpy_to_vector(img=img)

    def numpy_to_vector(self, img: np.ndarray) -> list[float]:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tensor = self.preprocess(img_rgb).unsqueeze(0)

        with torch.no_grad():
            vector = self.model(img_tensor)
        return vector.flatten().tolist()
