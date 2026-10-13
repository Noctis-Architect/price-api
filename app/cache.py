import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from app.config import settings

class PriceCache:
    def __init__(self, cache_file: Path = settings.CACHE_FILE_PATH):
        self.cache_file = cache_file
        self._memory_cache: Optional[Dict[str, Any]] = None
        self._last_updated_at: Optional[datetime] = None

        # Ensure parent directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Loads cached data from disk at initialization if available."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._memory_cache = data
                    if "updated_at" in data:
                        try:
                            self._last_updated_at = datetime.fromisoformat(data["updated_at"])
                        except Exception:
                            self._last_updated_at = datetime.now(timezone.utc)
            except Exception as e:
                print(f"[Cache] Failed to load disk cache: {e}")

    def get(self) -> Optional[Dict[str, Any]]:
        """Returns the in-memory cached JSON instantly."""
        return self._memory_cache

    def set(self, data: Dict[str, Any]) -> None:
        """Updates in-memory cache and persists atomically to disk."""
        self._memory_cache = data
        self._last_updated_at = datetime.now(timezone.utc)

        # Atomic disk write (write to temp file, then rename)
        try:
            temp_dir = self.cache_file.parent
            with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False, encoding="utf-8") as tf:
                json.dump(data, tf, ensure_ascii=False, indent=2)
                temp_name = tf.name
            os.replace(temp_name, self.cache_file)
        except Exception as e:
            print(f"[Cache] Error writing to disk cache: {e}")

    @property
    def has_data(self) -> bool:
        return self._memory_cache is not None

    @property
    def age_seconds(self) -> Optional[float]:
        if not self._last_updated_at:
            return None
        dt = self._last_updated_at
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = (now - dt).total_seconds()
        return max(0.0, diff)

# Global singleton cache instance
price_cache = PriceCache()
