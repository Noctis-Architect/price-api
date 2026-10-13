import os
from pathlib import Path
from typing import Set
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8088"))
    
    # If False, GET /api/v1/usd is publicly readable from cache without 401
    REQUIRE_API_KEY: bool = os.getenv("REQUIRE_API_KEY", "false").lower() in ("true", "1", "yes")
    
    # Master admin key for /refresh
    API_KEY: str = os.getenv("API_KEY", "wphub_0935ce87e51d0a0511ce3393037fd1cb")
    
    # Allowed client API keys
    raw_keys = os.getenv(
        "ALLOWED_API_KEYS",
        "wphub_0935ce87e51d0a0511ce3393037fd1cb,Bzz7PLg4FXY4M3GqIBLgjkkwghSsZTdi"
    )
    ALLOWED_API_KEYS: Set[str] = {k.strip() for k in raw_keys.split(",") if k.strip()}
    if API_KEY:
        ALLOWED_API_KEYS.add(API_KEY)
    
    UPDATE_INTERVAL_MINUTES: int = int(os.getenv("UPDATE_INTERVAL_MINUTES", "30"))
    CACHE_FILE_PATH: Path = BASE_DIR / os.getenv("CACHE_FILE_PATH", "data/cache.json")
    REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10.0"))

settings = Settings()
