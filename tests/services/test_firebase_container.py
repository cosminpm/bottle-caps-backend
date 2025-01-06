from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
from starlette import status

from app.services.firebase_container import FirebaseContainer
from app.shared.utils import resize_image_max_size, upload_file

if TYPE_CHECKING:
    import numpy as np

load_dotenv()

TEST_USER: str = "test_user"


class TestFirebaseContainer:
    firebase_container: FirebaseContainer = FirebaseContainer()

    @pytest.mark.asyncio
    async def test_remove_image_ok(self):
        file_path: Path = Path("tests/services/test_image.jpg")
        file: UploadFile = await upload_file(file_path)
        test_image_name: str = "TEST_IMAGE"
        image: np.ndarray = resize_image_max_size(file)
        self.firebase_container.add_image_to_container(
            image=image, user_id=TEST_USER, name=test_image_name
        )
        assert self.firebase_container.remove_image(user_id=TEST_USER, name=test_image_name) is True

    @pytest.mark.asyncio
    async def test_remove_image_error(self):
        test_image_name: str = "NOT_EXISTING"
        with pytest.raises(HTTPException) as exc_info:
            self.firebase_container.remove_image(user_id=TEST_USER, name=test_image_name)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
