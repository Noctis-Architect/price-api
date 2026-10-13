import httpx
from app.scrapers.base import BaseScraper, SourceResult

class RamzinexScraper(BaseScraper):
    source_id = "ramzinex"
    source_name = "Ramzinex (رمزینکس)"
    priority = 40  # Secondary fallback

    async def fetch(self, client: httpx.AsyncClient) -> SourceResult:
        try:
            resp = await client.get(
                "https://publicapi.ramzinex.com/exchange/api/v1.0/exchange/pairs/11",
                headers=self.DEFAULT_HEADERS,
                timeout=8.0
            )
            resp.raise_for_status()
            data = resp.json()

            pair_data = data.get("data", {})
            buy_rial = pair_data.get("buy", 0)
            sell_rial = pair_data.get("sell", 0)

            if not sell_rial and not buy_rial:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error="Buy/sell values missing from Ramzinex response"
                )

            sell_toman = int(sell_rial) // 10
            buy_toman = int(buy_rial) // 10
            price_toman = sell_toman if sell_toman > 0 else buy_toman
            price_rial = price_toman * 10

            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="online",
                price_toman=price_toman,
                buy_toman=buy_toman,
                sell_toman=sell_toman,
                price_rial=price_rial,
                raw={
                    "financial_status": pair_data.get("financial_status"),
                    "volume": pair_data.get("volume")
                }
            )
        except Exception as exc:
            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="offline",
                error=str(exc)
            )
