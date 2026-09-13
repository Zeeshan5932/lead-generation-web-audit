import requests
import logging
from typing import List, Dict, Any
from app.config import config
from app.models import Lead
from app.constants import USER_AGENT
from app.utils.validators import normalize_website_url

logger = logging.getLogger(__name__)

class SerperClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/places"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT
        }

    def search_businesses(self, keyword: str, location: str, num_results: int = 20) -> List[Lead]:
        query = f"{keyword} in {location}"
        payload = {
            "q": query,
            "num": num_results
        }
        
        leads = []
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            places = data.get("places", [])
            logger.info(f"Found {len(places)} businesses for '{query}'")
            
            for place in places:
                lead = Lead(
                    business_name=place.get("title", "Unknown Business"),
                    website_url=normalize_website_url(place.get("website", "")),
                    phone=place.get("phoneNumber", ""),
                    email="",  # Serper places rarely have email, will extract from website if possible
                    address=place.get("address", ""),
                    issues_found=[],
                    lead_status="COLD"
                )
                leads.append(lead)
                
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error("Serper API: Unauthorized (401). Check API key.")
            elif response.status_code == 403:
                logger.error("Serper API: Forbidden (403).")
            elif response.status_code == 429:
                logger.error("Serper API: Rate limit reached (429).")
            else:
                logger.error(f"Serper API HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Serper API request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in Serper search: {e}")
            
        return leads