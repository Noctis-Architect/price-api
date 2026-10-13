import httpx
from app.scrapers.base import BaseScraper, SourceResult

class TgjuScraper(BaseScraper):
    source_id = "tgju"
    source_name = "TGJU (شبکه اطلاع‌رسانی طلا و ارز)"
    priority = 20  # High priority market source

    async def fetch(self, client: httpx.AsyncClient) -> SourceResult:
        try:
            resp = await client.get(
                "https://call.tgju.org/ajax.json",
                headers={
                    **self.DEFAULT_HEADERS,
                    "Referer": "https://www.tgju.org/",
                    "X-Requested-With": "XMLHttpRequest"
                },
                timeout=8.0
            )
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current", {})
            dollar_info = current.get("price_dollar_rl") or current.get("price_dollar_dt")
            if not dollar_info:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error="price_dollar_rl not found in TGJU payload"
                )

            raw_p = str(dollar_info.get("p", "0")).replace(",", "").strip()
            price_rial = int(raw_p) if raw_p.isdigit() else 0
            if price_rial <= 0:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error=f"Invalid price value from TGJU: {raw_p}"
                )

            price_toman = price_rial // 10

            raw_d = str(dollar_info.get("d", "0")).replace(",", "").strip()
            change_rial = int(raw_d) if raw_d.isdigit() else 0
            change_toman = change_rial // 10

            try:
                change_percent = float(dollar_info.get("dp", 0))
            except (ValueError, TypeError):
                change_percent = 0.0

            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="online",
                price_toman=price_toman,
                buy_toman=price_toman,
                sell_toman=price_toman,
                price_rial=price_rial,
                change_toman=change_toman,
                change_percent=change_percent,
                last_source_update=dollar_info.get("ts"),
                raw={
                    "high": dollar_info.get("h"),
                    "low": dollar_info.get("l"),
                    "time_text": dollar_info.get("t"),
                    "trend": dollar_info.get("dt")
                }
            )
        except Exception as exc:
            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="offline",
                error=str(exc)
            )
