import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings
from app.cache import price_cache
from app.scheduler import start_scheduler, stop_scheduler, refresh_prices_task
from app.security import verify_api_key, verify_admin_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("price_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure cache is populated
    logger.info("Initializing USD Price API service...")
    if not price_cache.has_data or (price_cache.age_seconds and price_cache.age_seconds > 1800):
        logger.info("Warmup: Cache is empty or stale. Fetching initial rates now...")
        await refresh_prices_task()
    
    start_scheduler()
    logger.info("USD Price API service started successfully.")
    yield
    # Shutdown
    logger.info("Shutting down USD Price API service...")
    stop_scheduler()

app = FastAPI(
    title="USD Currency Price API",
    description="High-performance multi-source scraping API for USD (US Dollar to Toman/Rial) with fallback and 30-minute auto-refresh cache.",
    version=__version__,
    lifespan=lifespan
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _build_response(data: Dict[str, Any], simple: bool = False) -> Dict[str, Any]:
    """Helper to format price response."""
    cache_age = price_cache.age_seconds
    if simple:
        return {
            "price": data.get("price"),
            "buy": data.get("buy"),
            "sell": data.get("sell"),
            "price_rial": data.get("price_rial"),
            "unit": data.get("unit", "toman"),
            "source": data.get("active_source"),
            "updated_at": data.get("updated_at")
        }

    response_payload = dict(data)
    response_payload["cached"] = True
    response_payload["cache_age_seconds"] = round(cache_age, 2) if cache_age is not None else 0
    return response_payload

@app.get("/", tags=["Currency Rates"])
@app.get("/api/v1/usd", tags=["Currency Rates"])
async def get_usd_price(
    simple: bool = Query(
        False,
        description="Return lightweight compact JSON with only essential price fields"
    ),
    _auth: str = Depends(verify_api_key)
):
    """
    Returns live cached USD rate (in Toman & Rial) aggregated from top sources with automated fallback.
    Cached in memory to guarantee instant (<1ms) response times.
    """
    cached_data = price_cache.get()
    if not cached_data or not cached_data.get("price"):
        # If cache is not ready yet, perform on-demand fetch once
        await refresh_prices_task()
        cached_data = price_cache.get()

    if not cached_data or not cached_data.get("price"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Currency data is temporarily unavailable. Please try again shortly."
        )

    return _build_response(cached_data, simple=simple)

@app.post("/api/v1/refresh", tags=["Admin"])
async def manual_refresh(_auth: str = Depends(verify_admin_key)):
    """
    Force manual refresh of rates from all sources and update cache immediately.
    """
    await refresh_prices_task()
    cached_data = price_cache.get()
    return {
        "status": "success",
        "message": "Currency rates refreshed and cache updated successfully.",
        "data": cached_data
    }

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Service health and cache status."""
    has_cache = price_cache.has_data
    cache_age = price_cache.age_seconds
    return {
        "status": "healthy" if has_cache else "initializing",
        "version": __version__,
        "cache_ready": has_cache,
        "cache_age_seconds": round(cache_age, 2) if cache_age is not None else None,
        "update_interval_minutes": settings.UPDATE_INTERVAL_MINUTES
    }
