from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from dotenv import load_dotenv
from starlette.requests import Request

from app.services.saver.router import post_save_images
from app.shared.utils import upload_file

load_dotenv()

TEST_USER: str = "test_user"


@pytest.mark.asyncio
async def test_saver_bulk_ok():
    """Manual test to check if the API endpoint is working.

    This test will return always true, but it's useful for me to see if
    the files are being uploaded.
    """
    directory: Path = Path("tests/services/saver/test_multiple_images")
    paths: list = list(directory.glob("*.jpg"))
    uploaded_files = [await upload_file(path) for path in paths]

    fake_request = MagicMock(spec=Request)
    await post_save_images(files=uploaded_files, user_id="test_user", request=fake_request)


@pytest.mark.asyncio
async def test_saver_bulk_mock():
    """Fake test, to check if the router is
    working correctly without calling the actual functionality.
    """  # noqa: D205
    directory: Path = Path("tests/services/saver/test_multiple_images")
    paths: list = list(directory.glob("*.jpg"))
    uploaded_files = [await upload_file(path) for path in paths]

    fake_request = MagicMock(spec=Request)

    with patch("app.services.saver.router.save_image", new_callable=AsyncMock) as mock_save_image:
        mock_save_image.return_value = None
        await post_save_images(files=uploaded_files, user_id="test_user", request=fake_request)
