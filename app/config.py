from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    firebase_config_file: str
    firebase_bucket: str

    pinecone_api_key: str
    pinecone_env: str

    profiling_time: bool = False

    save_image: bool = False
    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8080
    prefix_url: str = "https://"
    torch_home: str = "./model"
