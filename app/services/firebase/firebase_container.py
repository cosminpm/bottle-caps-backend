import firebase_admin
from fastapi import UploadFile
from firebase_admin import credentials
from firebase_admin import storage

from app.config import Settings

settings = Settings()

class FirebaseContainer:
    def __init__(self):
        self.cred = credentials.Certificate(settings.firebase_config_file)
        self.app = firebase_admin.initialize_app(self.cred, {
            'storageBucket': settings.firebase_bucket
        })
        self.bucket = storage.bucket()

    def add_image_to_container(self, file: UploadFile, name: str, user_id: str):
        blob_path = f'{user_id}/{name}'
        blob = self.bucket.blob(blob_path)
        blob.upload_from_file(file.file, content_type=file.content_type)

        # Optional: Make the file publicly accessible and get its URL
        blob.make_public()
        return blob.public_url
