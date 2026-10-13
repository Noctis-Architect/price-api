import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8088"))
    
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "true").lower() in ("true", "1", "yes")
    API_KEY: str = os.getenv("API_KEY", "wphub_0935ce87e51d0a0511ce3393037fd1cb")
    
    UPDATE_INTERVAL_MINUTES: int = int(os.getenv("UPDATE_INTERVAL_MINUTES", "30"))
    CACHE_FILE_PATH: Path = BASE_DIR / os.getenv("CACHE_FILE_PATH", "data/cache.json")
    REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10.0"))

settings = Settings()
