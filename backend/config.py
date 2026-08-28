"""Configuration for the AI Product Comparison Advisor."""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

    # Paths
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_RAW_DIR: str = os.path.join(PROJECT_ROOT, "data", "raw")
    DATA_PROCESSED_DIR: str = os.path.join(PROJECT_ROOT, "data", "processed")
    VECTOR_DB_DIR: str = os.path.join(PROJECT_ROOT, "data", "vectors")

    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Performance
    MAX_RETRIEVAL_RESULTS: int = 10
    TOP_K_RECOMMENDATIONS: int = 3
    RESPONSE_TIMEOUT: int = 30


settings = Settings()
