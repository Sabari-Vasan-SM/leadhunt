import logging
import urllib.parse
from typing import List, Dict, Any
import httpx
from app.core.config import settings
from app.services.discovery.base import BaseDiscoveryProvider

logger = logging.getLogger(__name__)

class GooglePlacesDiscoveryProvider(BaseDiscoveryProvider):
    @property
    def name(self) -> str:
        return "GooglePlacesAPI"

    async def search(self, category: str, location: str, limit: int = 20) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        api_key = settings.GOOGLE_PLACES_API_KEY
        if not api_key:
            logger.info("Google Places API key is not set; skipping Google Places provider.")
            return results

        query = f"{category} in {location}"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": api_key
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    logger.error(f"Google Places API returned HTTP {resp.status_code}")
                    return results

                data = resp.json()
                places = data.get("results", [])

                for place in places[:limit]:
                    name = place.get("name")
                    formatted_address = place.get("formatted_address", "")
                    place_id = place.get("place_id")
                    rating = place.get("rating")
                    
                    # Construct official Google Maps URL
                    google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(name + ' ' + formatted_address)}"

                    results.append({
                        "business_name": name,
                        "category": category.title(),
                        "address": formatted_address,
                        "city": location.title(),
                        "pincode": "",
                        "phone": "",
                        "email": "",
                        "website_url": "",
                        "google_maps_url": google_maps_url,
                        "source_url": google_maps_url,
                        "source_name": self.name,
                        "raw_metadata": {
                            "place_id": place_id,
                            "rating": rating,
                            "user_ratings_total": place.get("user_ratings_total"),
                            "types": place.get("types", [])
                        }
                    })

        except Exception as e:
            logger.error(f"Error querying Google Places API: {e}")

        return results
