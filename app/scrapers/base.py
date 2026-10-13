from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import httpx
from datetime import datetime, timezone

class SourceResult(BaseModel):
    source_id: str
    source_name: str
    status: str = "online"  # "online" or "offline"
    price_toman: Optional[int] = None
    buy_toman: Optional[int] = None
    sell_toman: Optional[int] = None
    price_rial: Optional[int] = None
    change_toman: Optional[int] = None
    change_percent: Optional[float] = None
    last_source_update: Optional[str] = None
    error: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None

class BaseScraper(ABC):
    source_id: str
    source_name: str
    priority: int = 100  # Lower number = higher priority

    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fa,en-US;q=0.7,en;q=0.3"
    }

    @abstractmethod
    async def fetch(self, client: httpx.AsyncClient) -> SourceResult:
        """Fetch and parse rate from the source."""
        pass
