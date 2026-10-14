import re
from typing import Dict, Any

EMAIL_SYNTAX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
PHONE_DIGITS = re.compile(r'^\+?[0-9]{7,15}$')

class DataValidator:
    @staticmethod
    def validate_and_score(lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates lead fields and calculates a deterministic completeness confidence score.
        """
        name = (lead_data.get("business_name") or "").strip()
        phone = (lead_data.get("phone") or "").strip()
        email = (lead_data.get("email") or "").strip()
        website = (lead_data.get("website_url") or "").strip()
        address = (lead_data.get("address") or "").strip()
        pincode = (lead_data.get("pincode") or "").strip()
        google_maps = (lead_data.get("google_maps_url") or "").strip()
        city = (lead_data.get("city") or "").strip()

        # Validate Phone
        valid_phone = None
        if phone:
            digits_only = re.sub(r'[^\d+]', '', phone)
            if PHONE_DIGITS.match(digits_only):
                valid_phone = digits_only

        # Validate Email
        valid_email = None
        if email and EMAIL_SYNTAX.match(email):
            valid_email = email.lower()

        # Validate Pincode
        valid_pincode = None
        if pincode:
            pin_digits = re.sub(r'\D', '', pincode)
            if len(pin_digits) == 6:
                valid_pincode = pin_digits

        # Calculate Confidence Score (0.0 to 1.0)
        score = 0.0
        if name:
            score += 0.20
        if valid_phone:
            score += 0.25
        if valid_email:
            score += 0.25
        if website and website.startswith("http"):
            score += 0.15
        if address and len(address) > 5:
            score += 0.10
        if google_maps:
            score += 0.05

        lead_data["business_name"] = name
        lead_data["phone"] = valid_phone
        lead_data["email"] = valid_email
        lead_data["pincode"] = valid_pincode
        lead_data["city"] = city.title() if city else None
        lead_data["confidence_score"] = round(min(score, 1.0), 2)

        return lead_data
