from fastapi import HTTPException, Security
from fastapi.security import api_key
from starlette import status

from app.config import Settings

settings = Settings()

api_key_header = api_key.APIKeyHeader(name="X-API-KEY")


async def validate_api_key(key: str = Security(api_key_header)):
    """Validate that the key for the API is provided."""
    if key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized - API Key is wrong"
        )
