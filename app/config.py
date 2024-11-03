from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    firebase_config_file: str
    firebase_bucket: str

    pinecone_api_key: str
    pinecone_env: str

    profiling: bool = False
    save_image: bool = False
