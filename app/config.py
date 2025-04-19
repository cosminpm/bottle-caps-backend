from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

LIMIT_PERIOD: str = "15/minute"


class Settings(BaseSettings):
    firebase_config_file: str
    firebase_bucket: str

    pinecone_api_key: str
    pinecone_env: str

    profiling_time: bool = False

    save_image: bool = False
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    prefix_url: str = "http://"
    torch_home: str = "./model"

    api_key: str = "dumb_key"

    sentry_dsn: str = "dumb_dsn"
    is_sentry: bool = True
