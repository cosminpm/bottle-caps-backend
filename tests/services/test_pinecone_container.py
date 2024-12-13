import time
import uuid

import pytest
from dotenv import load_dotenv
from fastapi import HTTPException
from starlette import status

from app.services.pinecone_container import EMPTY_VECTOR, PineconeContainer

load_dotenv()

TEST_USER: str = "test_user"


class TestFirebaseContainer:
    pinecone_container: PineconeContainer = PineconeContainer()

    def test_remove_image_ok(self):
        image_name: str = "test_image.jpg"
        self.pinecone_container.upsert_into_pinecone(
            vector_id=str(uuid.uuid4()),
            values=EMPTY_VECTOR,
            metadata={"user_id": TEST_USER, "name": image_name},
        )
        time.sleep(1)
        self.pinecone_container.remove_vector(name=image_name, user_id=TEST_USER)
        time.sleep(1)
        res = self.pinecone_container.query_with_metadata(
            vector=EMPTY_VECTOR, metadata={"name": image_name, "user_id": TEST_USER}
        )
        assert len(res) == 0

    def test_remove_image_error_404(self):
        image_name: str = "non_existing.jpg"
        with pytest.raises(HTTPException) as exc_info:
            self.pinecone_container.remove_vector(name=image_name, user_id=TEST_USER)
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
