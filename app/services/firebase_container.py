import firebase_admin
from fastapi import UploadFile
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
        self.cred = credentials.Certificate(settings.firebase_config_file)
        self.app = firebase_admin.initialize_app(
            self.cred, {"storageBucket": settings.firebase_bucket}
        )
        self.bucket = storage.bucket()

    def add_image_to_container(self, file: UploadFile, name: str, user_id: str) -> str:
        blob_path = f"user/collection/{user_id}/{name}"
        blob = self.bucket.blob(blob_path)
        blob.upload_from_file(file.file, content_type=file.content_type)

        blob.make_public()
        return blob.public_url
