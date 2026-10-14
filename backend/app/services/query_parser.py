import re
from typing import Tuple, Dict, Any, List

# Mapping common search terms to OpenStreetMap tags
CATEGORY_OSM_MAPPING: Dict[str, List[Dict[str, str]]] = {
    "salon": [
        {"key": "shop", "value": "hairdresser"},
        {"key": "shop", "value": "beauty"},
        {"key": "amenity", "value": "spa"}
    ],
    "beauty": [
        {"key": "shop", "value": "beauty"},
        {"key": "shop", "value": "hairdresser"}
    ],
    "spa": [
        {"key": "amenity", "value": "spa"},
        {"key": "leisure", "value": "sauna"}
    ],
    "hotel": [
        {"key": "tourism", "value": "hotel"},
        {"key": "tourism", "value": "guest_house"},
        {"key": "tourism", "value": "motel"}
    ],
    "restaurant": [
        {"key": "amenity", "value": "restaurant"},
        {"key": "amenity", "value": "cafe"},
        {"key": "amenity", "value": "fast_food"}
    ],
    "cafe": [
        {"key": "amenity", "value": "cafe"}
    ],
    "hospital": [
        {"key": "amenity", "value": "hospital"},
        {"key": "amenity", "value": "clinic"},
        {"key": "amenity", "value": "doctors"}
    ],
    "clinic": [
        {"key": "amenity", "value": "clinic"},
        {"key": "amenity", "value": "doctors"}
    ],
    "software": [
        {"key": "office", "value": "it"},
        {"key": "office", "value": "company"},
        {"key": "craft", "value": "electronics"}
    ],
    "it": [
        {"key": "office", "value": "it"},
        {"key": "office", "value": "company"}
    ],
    "company": [
        {"key": "office", "value": "company"},
        {"key": "office", "value": "it"}
    ],
    "school": [
        {"key": "amenity", "value": "school"},
        {"key": "amenity", "value": "college"}
    ],
    "college": [
        {"key": "amenity", "value": "college"},
        {"key": "amenity", "value": "university"}
    ],
    "gym": [
        {"key": "leisure", "value": "fitness_centre"},
        {"key": "leisure", "value": "sports_centre"}
    ],
    "pharmacy": [
        {"key": "amenity", "value": "pharmacy"}
    ],
    "bank": [
        {"key": "amenity", "value": "bank"}
    ],
    "supermarket": [
        {"key": "shop", "value": "supermarket"},
        {"key": "shop", "value": "convenience"}
    ]
}

def parse_natural_language_query(query: str) -> Tuple[str, str]:
    """
    Deterministically parses queries like:
    - 'List salons in Coimbatore' -> ('salons', 'Coimbatore')
    - 'Hotels in Chennai' -> ('Hotels', 'Chennai')
    - 'Software companies in Bangalore' -> ('Software companies', 'Bangalore')
    - 'Hospitals in Erode' -> ('Hospitals', 'Erode')
    """
    cleaned = query.strip()
    
    # Strip common leading verbs: "List", "Find", "Show me", "Search for", "Get", "Top", "Best"
    cleaned = re.sub(r'^(list|find|show\s+me|search\s+for|get|top|best|all)\s+', '', cleaned, flags=re.IGNORECASE).strip()

    # Match prepositions: " in ", " near ", " around ", " at "
    prep_match = re.search(r'\b(in|near|around|at)\b', cleaned, flags=re.IGNORECASE)
    if prep_match:
        split_idx = prep_match.start()
        prep_len = len(prep_match.group(0))
        category = cleaned[:split_idx].strip()
        location = cleaned[split_idx + prep_len:].strip()
        if category and location:
            return category, location

    # If comma-separated: "Salons, Coimbatore"
    if "," in cleaned:
        parts = cleaned.split(",", 1)
        return parts[0].strip(), parts[1].strip()

    # Fallback: if single phrase, return query as category, empty location
    return cleaned, ""

def get_osm_tags_for_category(category: str) -> List[Dict[str, str]]:
    """
    Returns relevant OSM tags (key, value) for a given category.
    """
    cat_lower = category.lower()
    
    for key, tags in CATEGORY_OSM_MAPPING.items():
        if key in cat_lower or cat_lower in key:
            return tags
            
    # Default fallback tags for commercial places
    return [
        {"key": "shop", "value": "yes"},
        {"key": "office", "value": "yes"},
        {"key": "amenity", "value": "yes"}
    ]
