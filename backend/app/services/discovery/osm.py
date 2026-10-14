import logging
import urllib.parse
from typing import List, Dict, Any, Optional
import httpx
from app.core.config import settings
from app.services.discovery.base import BaseDiscoveryProvider
from app.services.query_parser import get_osm_tags_for_category

logger = logging.getLogger(__name__)

class OSMDiscoveryProvider(BaseDiscoveryProvider):
    @property
    def name(self) -> str:
        return "OpenStreetMap"

    async def _geocode_location(self, client: httpx.AsyncClient, location: str) -> Optional[Dict[str, Any]]:
        """
        Geocode city/area using OpenStreetMap Nominatim.
        """
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "LeadHunt/1.0 (info@leadhunt.local)"}
        params = {
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        try:
            resp = await client.get(url, params=params, headers=headers, timeout=8.0)
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    item = data[0]
                    return {
                        "lat": float(item["lat"]),
                        "lon": float(item["lon"]),
                        "display_name": item.get("display_name", location),
                        "boundingbox": item.get("boundingbox", [])
                    }
        except Exception as e:
            logger.debug(f"Geocoding error for location '{location}': {e}")
        return None

    async def _search_nominatim_pois(self, client: httpx.AsyncClient, category: str, location: str, limit: int) -> List[Dict[str, Any]]:
        results = []
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "LeadHunt/1.0 (info@leadhunt.local)"}
        
        cat_clean = category.rstrip('s').lower()
        search_terms = [
            f"{cat_clean} {location}",
            f"{category} {location}",
            f"{category} in {location}"
        ]

        seen_names = set()
        for term in search_terms:
            try:
                resp = await client.get(url, params={"q": term, "format": "json", "limit": limit, "addressdetails": 1}, headers=headers, timeout=6.0)
                if resp.status_code == 200:
                    for item in resp.json():
                        name = item.get("name")
                        if not name or name.lower() in seen_names:
                            continue
                        seen_names.add(name.lower())

                        lat = item.get("lat")
                        lon = item.get("lon")
                        addr = item.get("address", {})
                        street = addr.get("road") or addr.get("suburb", "")
                        city_tag = addr.get("city") or addr.get("town") or addr.get("state_district") or location.title()
                        pincode = addr.get("postcode", "")
                        display = item.get("display_name", "")
                        full_address = f"{street}, {city_tag}" if street else display

                        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                        osm_source_url = f"https://www.openstreetmap.org/{item.get('osm_type', 'node')}/{item.get('osm_id', '')}"

                        results.append({
                            "business_name": name,
                            "category": category.title(),
                            "address": full_address,
                            "city": city_tag,
                            "pincode": pincode,
                            "phone": "",
                            "email": "",
                            "website_url": "",
                            "google_maps_url": google_maps_url,
                            "source_url": osm_source_url,
                            "source_name": self.name,
                            "raw_metadata": item
                        })
                if len(results) >= limit:
                    break
            except Exception as e:
                logger.debug(f"Nominatim POI search error: {e}")
        return results

    async def search(self, category: str, location: str, limit: int = 40) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(headers={"User-Agent": "LeadHunt/1.0"}) as client:
            geo = await self._geocode_location(client, location)
            
            # Fast Overpass Query if geocoded
            if geo:
                lat = geo["lat"]
                lon = geo["lon"]
                radius = 12000
                tags = get_osm_tags_for_category(category)
                tag_conds = []
                for t in tags[:2]:
                    if t["value"] == "yes":
                        tag_conds.append(f'node["{t["key"]}"](around:{radius},{lat},{lon});')
                    else:
                        tag_conds.append(f'node["{t["key"]}"="{t["value"]}"](around:{radius},{lat},{lon});')

                query_ql = f"""
                [out:json][timeout:10];
                (
                  {" ".join(tag_conds)}
                );
                out center tags {limit};
                """

                try:
                    resp = await client.get(
                        "https://overpass-api.de/api/interpreter",
                        params={"data": query_ql},
                        timeout=8.0
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        elements = data.get("elements", [])
                        for elem in elements:
                            t = elem.get("tags", {})
                            name = t.get("name") or t.get("name:en")
                            if not name:
                                continue

                            elem_type = elem.get("type", "node")
                            elem_id = elem.get("id")
                            elem_lat = elem.get("lat") or (elem.get("center", {}).get("lat")) or lat
                            elem_lon = elem.get("lon") or (elem.get("center", {}).get("lon")) or lon

                            street = t.get("addr:street", "")
                            housenumber = t.get("addr:housenumber", "")
                            suburb = t.get("addr:suburb", "") or t.get("addr:neighbourhood", "")
                            city_tag = t.get("addr:city") or location.title()
                            pincode = t.get("addr:postcode", "")

                            addr_parts = [p for p in [housenumber, street, suburb, city_tag] if p]
                            full_address = ", ".join(addr_parts) if addr_parts else f"{name}, {city_tag}"

                            phone = t.get("phone") or t.get("contact:phone") or t.get("contact:mobile") or ""
                            email = t.get("email") or t.get("contact:email") or ""
                            website = t.get("website") or t.get("contact:website") or t.get("url") or ""

                            google_maps_url = f"https://www.google.com/maps/search/?api=1&query={elem_lat},{elem_lon}"
                            osm_source_url = f"https://www.openstreetmap.org/{elem_type}/{elem_id}"

                            results.append({
                                "business_name": name,
                                "category": category.title(),
                                "address": full_address,
                                "city": city_tag,
                                "pincode": pincode,
                                "phone": phone,
                                "email": email,
                                "website_url": website,
                                "google_maps_url": google_maps_url,
                                "source_url": osm_source_url,
                                "source_name": self.name,
                                "raw_metadata": {
                                    "osm_id": elem_id,
                                    "tags": t
                                }
                            })

                            if len(results) >= limit:
                                break
                except Exception as ex:
                    logger.debug(f"Overpass fast attempt skipped: {ex}")

            # Supplement or fallback with Nominatim POI search
            if len(results) < limit:
                nominatim_leads = await self._search_nominatim_pois(client, category, location, limit - len(results))
                results.extend(nominatim_leads)

        return results
