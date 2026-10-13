import httpx
from app.scrapers.base import BaseScraper, SourceResult

class WallexScraper(BaseScraper):
    source_id = "wallex"
    source_name = "Wallex (والکس)"
    priority = 50  # Tertiary fallback

    async def fetch(self, client: httpx.AsyncClient) -> SourceResult:
        try:
            resp = await client.get(
                "https://api.wallex.ir/v1/markets",
                headers=self.DEFAULT_HEADERS,
                timeout=8.0
            )
            resp.raise_for_status()
            data = resp.json()

            symbols = data.get("result", {}).get("symbols", {})
            usdt_tmn = symbols.get("USDTTMN", {})
            stats = usdt_tmn.get("stats", {})

            raw_price = stats.get("lastPrice")
            if not raw_price:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error="USDTTMN lastPrice not found in Wallex response"
                )

            price_toman = int(float(raw_price))
            price_rial = price_toman * 10

            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="online",
                price_toman=price_toman,
                buy_toman=price_toman,
                sell_toman=price_toman,
                price_rial=price_rial,
                change_percent=float(stats.get("24h_ch", 0)) if stats.get("24h_ch") else None,
                raw={
                    "24h_high": stats.get("24h_highPrice"),
                    "24h_low": stats.get("24h_lowPrice"),
                    "24h_volume": stats.get("24h_volume")
                }
            )
        except Exception as exc:
            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="offline",
                error=str(exc)
            )
