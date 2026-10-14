import json
import logging
import re
import urllib.parse
from typing import Dict, Any, Optional, Set
import httpx
from bs4 import BeautifulSoup
from app.core.config import settings

logger = logging.getLogger(__name__)

# Extensions to ignore when parsing emails
IGNORE_EMAIL_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js'}
# Domains to ignore for emails
IGNORE_EMAIL_DOMAINS = {'sentry.io', 'example.com', 'w3.org', 'domain.com', 'email.com', 'wixpress.com'}

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
# Indian phone patterns (mobile: 6-9 followed by 9 digits, or landlines with STD code)
PHONE_REGEX = re.compile(
    r'(?:(?:\+91[\s-]?)|\b0)?([6-9]\d{9})\b|'  # Indian 10-digit mobile
    r'\b(0\d{2,4}[\s-]?\d{6,8})\b'            # Landline with STD code
)
PINCODE_REGEX = re.compile(r'\b([1-9][0-9]{2}\s?[0-9]{3})\b')

class ContactExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": settings.DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def extract_from_website(self, url: str) -> Dict[str, Any]:
        """
        Extracts contact details from website homepage and optional contact page.
        """
        extracted = {
            "phone": None,
            "email": None,
            "address": None,
            "pincode": None,
            "city": None,
            "google_maps_url": None,
            "social_links": {},
            "crawled_urls": []
        }

        if not url or not url.startswith("http"):
            return extracted

        async with httpx.AsyncClient(
            headers=self.headers,
            follow_redirects=True,
            verify=False,
            timeout=settings.REQUEST_TIMEOUT_SECONDS
        ) as client:
            try:
                # 1. Fetch Homepage
                homepage_data, contact_links = await self._fetch_and_parse(client, url)
                extracted["crawled_urls"].append(url)
                self._merge_details(extracted, homepage_data)

                # 2. If phone or email missing, check contact page
                if (not extracted["phone"] or not extracted["email"]) and contact_links:
                    contact_url = contact_links[0]
                    extracted["crawled_urls"].append(contact_url)
                    contact_page_data, _ = await self._fetch_and_parse(client, contact_url)
                    self._merge_details(extracted, contact_page_data)

            except Exception as e:
                logger.debug(f"Error scraping website {url}: {e}")

        return extracted

    async def _fetch_and_parse(self, client: httpx.AsyncClient, target_url: str):
        details = {
            "phone": None,
            "email": None,
            "address": None,
            "pincode": None,
            "city": None,
            "google_maps_url": None,
            "social_links": {}
        }
        contact_links = []

        try:
            resp = await client.get(target_url)
            if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
                return details, contact_links

            soup = BeautifulSoup(resp.text, "lxml")

            # 1. Parse JSON-LD structured data
            json_ld_data = self._parse_json_ld(soup)
            self._merge_details(details, json_ld_data)

            # 2. Extract from explicit HTML links (tel:, mailto:)
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href.startswith("tel:"):
                    phone_val = href.replace("tel:", "").split("?")[0].strip()
                    if not details["phone"]:
                        details["phone"] = self._clean_phone(phone_val)
                elif href.startswith("mailto:"):
                    email_val = href.replace("mailto:", "").split("?")[0].strip().lower()
                    if not details["email"] and self._is_valid_email(email_val):
                        details["email"] = email_val
                elif "maps.google.com" in href or "goo.gl/maps" in href or "google.com/maps" in href:
                    if not details["google_maps_url"]:
                        details["google_maps_url"] = href
                elif any(domain in href for domain in ["instagram.com", "facebook.com", "linkedin.com", "twitter.com", "x.com"]):
                    for d in ["instagram", "facebook", "linkedin", "twitter"]:
                        if d in href and d not in details["social_links"]:
                            details["social_links"][d] = href

                # Look for contact / about links
                href_lower = href.lower()
                if any(k in href_lower for k in ["contact", "reach-us", "about-us", "contact-us", "get-in-touch"]):
                    full_contact = urllib.parse.urljoin(target_url, href)
                    # Stay on same domain
                    if urllib.parse.urlparse(full_contact).netloc == urllib.parse.urlparse(target_url).netloc:
                        if full_contact not in contact_links and full_contact != target_url:
                            contact_links.append(full_contact)

            # 3. Text-based Regex extraction if not found
            page_text = soup.get_text(separator=" ", strip=True)

            if not details["email"]:
                email_matches = EMAIL_REGEX.findall(page_text)
                for email_candidate in email_matches:
                    if self._is_valid_email(email_candidate.lower()):
                        details["email"] = email_candidate.lower()
                        break

            if not details["phone"]:
                phone_matches = PHONE_REGEX.findall(page_text)
                for mobile, landline in phone_matches:
                    candidate = mobile or landline
                    cleaned = self._clean_phone(candidate)
                    if cleaned:
                        details["phone"] = cleaned
                        break

            if not details["pincode"]:
                pin_matches = PINCODE_REGEX.findall(page_text)
                if pin_matches:
                    details["pincode"] = pin_matches[0].replace(" ", "")

        except Exception as e:
            logger.debug(f"Error parsing page {target_url}: {e}")

        return details, contact_links

    def _parse_json_ld(self, soup: BeautifulSoup) -> Dict[str, Any]:
        result = {}
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                if not script.string:
                    continue
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("@type", "")
                    if any(t in str(item_type) for t in ["Organization", "LocalBusiness", "Store", "Restaurant", "MedicalBusiness", "Place"]):
                        if "telephone" in item and not result.get("phone"):
                            result["phone"] = self._clean_phone(str(item["telephone"]))
                        if "email" in item and not result.get("email"):
                            candidate = str(item["email"]).strip().lower()
                            if self._is_valid_email(candidate):
                                result["email"] = candidate
                        if "address" in item:
                            addr = item["address"]
                            if isinstance(addr, dict):
                                street = addr.get("streetAddress", "")
                                locality = addr.get("addressLocality", "")
                                postal_code = addr.get("postalCode", "")
                                full_addr = ", ".join([p for p in [street, locality, postal_code] if p])
                                if full_addr:
                                    result["address"] = full_addr
                                if postal_code:
                                    result["pincode"] = postal_code
                                if locality:
                                    result["city"] = locality
                            elif isinstance(addr, str):
                                result["address"] = addr
            except Exception:
                continue
        return result

    def _merge_details(self, target: Dict[str, Any], source: Dict[str, Any]):
        for key in ["phone", "email", "address", "pincode", "city", "google_maps_url"]:
            if not target.get(key) and source.get(key):
                target[key] = source[key]
        if source.get("social_links"):
            target.setdefault("social_links", {}).update(source["social_links"])

    def _is_valid_email(self, email: str) -> bool:
        if not email or "@" not in email:
            return False
        if any(email.endswith(ext) for ext in IGNORE_EMAIL_EXTENSIONS):
            return False
        domain = email.split("@")[-1]
        if domain in IGNORE_EMAIL_DOMAINS:
            return False
        return True

    def _clean_phone(self, phone: str) -> str:
        if not phone:
            return ""
        # Remove unwanted punctuation
        cleaned = re.sub(r'[^\d+]', '', phone)
        # Normalize +91
        if cleaned.startswith("0091"):
            cleaned = "+91" + cleaned[4:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = "+" + cleaned
        elif len(cleaned) == 10 and cleaned[0] in "6789":
            cleaned = "+91" + cleaned
        return cleaned
