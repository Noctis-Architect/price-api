import re
from typing import Optional
import httpx
from app.scrapers.base import BaseScraper, SourceResult

class BonbastScraper(BaseScraper):
    source_id = "bonbast"
    source_name = "Bonbast (بن‌بست)"
    priority = 10  # Highest priority for paper cash market

    async def fetch(self, client: httpx.AsyncClient) -> SourceResult:
        try:
            # 1. Fetch homepage to extract dynamic session token
            resp = await client.get(
                "https://www.bonbast.com",
                headers=self.DEFAULT_HEADERS,
                timeout=8.0
            )
            resp.raise_for_status()

            # Find dynamic param string: $.post('/json', {param: "..."}
            match = re.search(r"\$\.post\(\s*['\"]/json['\"]\s*,\s*\{\s*param\s*:\s*['\"]([^'\"]+)['\"]\s*\}", resp.text)
            if not match:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error="Dynamic parameter token not found in HTML"
                )

            param_token = match.group(1)

            # 2. Query JSON data endpoint with extracted token
            post_headers = {
                **self.DEFAULT_HEADERS,
                "Referer": "https://www.bonbast.com/",
                "Origin": "https://www.bonbast.com",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }

            json_resp = await client.post(
                "https://www.bonbast.com/json",
                data={"param": param_token},
                headers=post_headers,
                timeout=8.0
            )
            json_resp.raise_for_status()
            data = json_resp.json()

            sell_toman = int(data.get("usd1", 0))
            buy_toman = int(data.get("usd2", 0))

            if sell_toman <= 0 and buy_toman <= 0:
                return SourceResult(
                    source_id=self.source_id,
                    source_name=self.source_name,
                    status="offline",
                    error="Invalid or empty USD price in response"
                )

            # Active reference price
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
                last_source_update=data.get("created"),
                raw={"usd1_sell": sell_toman, "usd2_buy": buy_toman, "eur1": data.get("eur1")}
            )
        except Exception as exc:
            return SourceResult(
                source_id=self.source_id,
                source_name=self.source_name,
                status="offline",
                error=str(exc)
            )
