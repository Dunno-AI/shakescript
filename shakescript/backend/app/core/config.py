from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    VECTOR_DIMENSION: int = 768
    CHUNK_SIZE: int = 500
    OVERLAP: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
