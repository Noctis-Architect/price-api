import httpx
from app.scrapers.base import BaseScraper, SourceResult

class TetherlandScraper(BaseScraper):
    source_id = "tetherland"
    source_name = "TetherLand (تترلند)"
    priority = 30  # High liquidity USDT/Toman reference

    async def fetch(self, client: httpx.AsyncClient) -> SourceResult:
        try:
            resp = await client.get(
                "https://api.tetherland.com/currencies",
                headers=self.DEFAULT_HEADERS,
                timeout=8.0
            )
            resp.raise_for_status()
            data = resp.json()

            currencies = data.get("data", {}).get("currencies", {})
            usdt_info = currencies.get("USDT", {})
            raw_price = usdt_info.get("price")
            if not raw_price:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error="USDT price missing in Tetherland response"
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
                raw={
                    "diff24d": usdt_info.get("diff24d"),
                    "diff7d": usdt_info.get("diff7d")
                }
            )
        except Exception as exc:
            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="offline",
                error=str(exc)
            )
