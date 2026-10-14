import re
from typing import List, Dict, Any

class DataDeduplicator:
    @staticmethod
    def _normalize_name(name: str) -> str:
        if not name:
            return ""
        # Lowercase, strip punctuation and common suffixes
        cleaned = re.sub(r'[^\w\s]', '', name.lower())
        cleaned = re.sub(r'\b(pvt|ltd|limited|private|inc|corp|co|company|enterprises)\b', '', cleaned)
        return " ".join(cleaned.split())

    @classmethod
    def deduplicate(cls, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicates list of leads by phone or normalized (name + city).
        Merges missing information across duplicates to yield richer leads.
        """
        merged_by_key: Dict[str, Dict[str, Any]] = {}
        phone_to_key: Dict[str, str] = {}

        for lead in leads:
            name_norm = cls._normalize_name(lead.get("business_name", ""))
            city_norm = (lead.get("city") or "").lower().strip()
            name_key = f"{name_norm}::{city_norm}"
            phone = lead.get("phone")

            target_key = None
            if phone and phone in phone_to_key:
                target_key = phone_to_key[phone]
            elif name_key in merged_by_key:
                target_key = name_key

            if target_key:
                # Merge into existing record
                existing = merged_by_key[target_key]
                for field in ["phone", "email", "website_url", "address", "pincode", "google_maps_url"]:
                    if not existing.get(field) and lead.get(field):
                        existing[field] = lead[field]
                # Keep higher confidence score
                existing["confidence_score"] = max(existing.get("confidence_score", 0), lead.get("confidence_score", 0))
            else:
                # New unique record
                merged_by_key[name_key] = lead
                if phone:
                    phone_to_key[phone] = name_key

        return list(merged_by_key.values())
