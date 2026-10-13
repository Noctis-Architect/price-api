import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone

from app.config import settings
from app.cache import price_cache
from app.scrapers.manager import ScraperManager

logger = logging.getLogger("price_api.scheduler")
scheduler = AsyncIOScheduler()
manager = ScraperManager()

async def refresh_prices_task() -> None:
    """
    Scrapes currency rates from all sources, performs fallback, and updates the cache.
    """
    logger.info("[Scheduler] Starting periodic currency price refresh...")
    try:
        result = await manager.fetch_all(timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS)
        if result.get("status") == "success" and result.get("price"):
            price_cache.set(result)
            logger.info(
                f"[Scheduler] Currency cache updated successfully. "
                f"Active Source: {result.get('active_source')} | USD Price: {result.get('price'):,} Toman"
            )
        else:
            logger.warning(f"[Scheduler] Scrape returned without valid price: {result.get('message')}")
    except Exception as e:
        logger.error(f"[Scheduler] Failed to refresh currency rates: {e}", exc_info=True)

def start_scheduler() -> None:
    """Initializes and starts the 30-minute background scheduler."""
    scheduler.add_job(
        refresh_prices_task,
        trigger=IntervalTrigger(minutes=settings.UPDATE_INTERVAL_MINUTES),
        id="refresh_currency_prices",
        name="Refresh USD currency prices every 30 minutes",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )
    scheduler.start()
    logger.info(f"[Scheduler] Scheduler started. Next refresh every {settings.UPDATE_INTERVAL_MINUTES} minutes.")

def stop_scheduler() -> None:
    """Stops the background scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Scheduler stopped.")
