import io
import json

import cv2
import firebase_admin
import numpy as np
import starlette.status
from fastapi import HTTPException
from firebase_admin import credentials, storage

from app.config import Settings

settings = Settings()


class FirebaseContainer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.cred = credentials.Certificate(self.get_firebase_credentials())
        self.app = firebase_admin.initialize_app(
            self.cred, {"storageBucket": settings.firebase_bucket}
        )
        self.bucket = storage.bucket()

    def add_image_to_container(self, image: np.ndarray, name: str, user_id: str) -> str:
        success, image_encoded = cv2.imencode(".png", image)
        if not success:
            raise HTTPException(
                status_code=starlette.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to encode image.",
            )

        image_bytes = io.BytesIO(image_encoded.tobytes())

        blob_path = f"users/{user_id}/collection/{name}"
        blob = self.bucket.blob(blob_path)

        if blob.exists():
            raise HTTPException(
                status_code=starlette.status.HTTP_409_CONFLICT, detail="Image already exists."
            )

        blob.upload_from_file(image_bytes, content_type="image/png")
        blob.make_public()

        return blob.public_url

    @staticmethod
    def get_firebase_credentials() -> dict:
        """Parse firebase_credentials JSON string to a dictionary."""
        try:
            return json.loads(settings.firebase_config_file)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON for firebase_credentials") from e
