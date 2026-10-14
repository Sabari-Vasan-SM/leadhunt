from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseDiscoveryProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def search(self, category: str, location: str, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Returns list of discovered businesses with standard fields:
        {
            "business_name": str,
            "category": str,
            "address": str,
            "city": str,
            "pincode": str,
            "phone": str,
            "email": str,
            "website_url": str,
            "google_maps_url": str,
            "source_url": str,
            "source_name": str,
            "raw_metadata": dict
        }
        """
        pass
