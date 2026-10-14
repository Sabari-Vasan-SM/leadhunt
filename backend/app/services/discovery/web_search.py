import logging
import re
import urllib.parse
from typing import List, Dict, Any
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings
from app.services.discovery.base import BaseDiscoveryProvider

logger = logging.getLogger(__name__)

class WebSearchDiscoveryProvider(BaseDiscoveryProvider):
    @property
    def name(self) -> str:
        return "WebSearch"

    async def search(self, category: str, location: str, limit: int = 25) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        search_query = f"{category} in {location} official website contact"
        headers = {
            "User-Agent": settings.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0, headers=headers) as client:
                # Query Bing HTML search
                url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(search_query)}"
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    items = soup.select("li.b_algo")

                    for item in items:
                        title_elem = item.select_one("h2 a")
                        snippet_elem = item.select_one(".b_caption p, .b_algoSlug, p")
                        if not title_elem:
                            continue

                        raw_title = title_elem.get_text(strip=True)
                        raw_href = title_elem.get("href", "")
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                        # Filter out aggregator / generic search pages if not a business
                        title_lower = raw_title.lower()
                        if any(term in title_lower for term in ["top 10", "best 10", "yellow pages", "tripadvisor", "wikipedia"]):
                            continue

                        # Clean company name
                        cleaned_name = re.sub(r'\s*([\|\-–—:].*)$', '', raw_title).strip()
                        if not cleaned_name or len(cleaned_name) < 3:
                            cleaned_name = raw_title

                        phone_match = re.search(r'(\+91[\s-]?)?[6-9]\d{9}|\b0\d{2,4}[-\s]?\d{6,8}\b', snippet)
                        found_phone = phone_match.group(0) if phone_match else ""

                        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', snippet)
                        found_email = email_match.group(0) if email_match else ""

                        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(cleaned_name + ' ' + location)}"

                        results.append({
                            "business_name": cleaned_name,
                            "category": category.title(),
                            "address": f"{cleaned_name}, {location.title()}",
                            "city": location.title(),
                            "pincode": "",
                            "phone": found_phone,
                            "email": found_email,
                            "website_url": raw_href if raw_href.startswith("http") else "",
                            "google_maps_url": google_maps_url,
                            "source_url": raw_href,
                            "source_name": self.name,
                            "raw_metadata": {
                                "snippet": snippet,
                                "original_title": raw_title,
                            }
                        })

                        if len(results) >= limit:
                            break

        except Exception as e:
            logger.debug(f"WebSearch provider error: {e}")

        return results
