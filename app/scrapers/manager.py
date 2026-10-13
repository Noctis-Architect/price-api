import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx

from app.scrapers.base import BaseScraper, SourceResult
from app.scrapers.bonbast import BonbastScraper
from app.scrapers.tgju import TgjuScraper
from app.scrapers.tetherland import TetherlandScraper
from app.scrapers.ramzinex import RamzinexScraper
from app.scrapers.wallex import WallexScraper

class ScraperManager:
    def __init__(self):
        # Ordered by priority
        self.scrapers: List[BaseScraper] = [
            BonbastScraper(),
            TgjuScraper(),
            TetherlandScraper(),
            RamzinexScraper(),
            WallexScraper()
        ]
        self.scrapers.sort(key=lambda s: s.priority)

    async def fetch_all(self, timeout_seconds: float = 10.0) -> Dict[str, Any]:
        """
        Executes all scrapers concurrently and selects the best active source via fallback.
        """
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            tasks = [scraper.fetch(client) for scraper in self.scrapers]
            results: List[SourceResult] = await asyncio.gather(*tasks, return_exceptions=False)

        now_utc = datetime.now(timezone.utc).isoformat()
        sources_dict: Dict[str, Any] = {}
        active_source: Optional[SourceResult] = None

        # Build sources map and select highest priority online source
        for scraper, result in zip(self.scrapers, results):
            sources_dict[scraper.source_id] = result.model_dump()
            if active_source is None and result.status == "online" and result.price_toman:
                active_source = result

        if not active_source:
            # Fallback if somehow all sources failed
            return {
                "status": "error",
                "message": "All scraping sources failed to return valid price",
                "currency": "USD",
                "unit": "toman",
                "price": None,
                "buy": None,
                "sell": None,
                "price_rial": None,
                "active_source": None,
                "active_source_name": None,
                "updated_at": now_utc,
                "sources": sources_dict
            }

        return {
            "status": "success",
            "currency": "USD",
            "unit": "toman",
            "price": active_source.price_toman,
            "buy": active_source.buy_toman,
            "sell": active_source.sell_toman,
            "price_rial": active_source.price_rial,
            "change_toman": active_source.change_toman,
            "change_percent": active_source.change_percent,
            "active_source": active_source.source_id,
            "active_source_name": active_source.source_name,
            "updated_at": now_utc,
            "sources": sources_dict
        }
