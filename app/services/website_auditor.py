import requests
import re
import time
import random
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from typing import List
from app.config import config
from app.models import Lead
from app.constants import USER_AGENT, HOT_STATUS, COLD_STATUS
from app.utils.helpers import random_delay

logger = logging.getLogger(__name__)

class WebsiteAuditor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def audit(self, lead: Lead) -> Lead:
        if not lead.website_url:
            lead.issues_found.append("No Website")
            lead.lead_status = HOT_STATUS
            logger.info(f"HOT LEAD FOUND! Business: {lead.business_name} | Issues: No Website")
            return lead

        random_delay()
        url = lead.website_url
        
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT, allow_redirects=True)
            final_url = response.url
            
            # Check 1: SSL
            if not final_url.startswith("https://"):
                lead.issues_found.append("No SSL")
            
            # Check 2: Mobile Responsiveness
            soup = BeautifulSoup(response.text, "html.parser")
            viewport = soup.find("meta", attrs={"name": "viewport"})
            if not viewport:
                lead.issues_found.append("Not Mobile Friendly")
                
            # Check 3: Website Status
            if response.status_code >= 400:
                lead.issues_found.append("Website Down")
                
            # Optional: Conservative email extraction from website
            if not lead.email:
                email_pattern = r'\b(info|contact|hello|sales|support|office)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
                match = re.search(email_pattern, response.text, re.IGNORECASE)
                if match:
                    lead.email = match.group(0).lower()

        except requests.exceptions.Timeout:
            lead.issues_found.append("Website Down")
            logger.warning(f"Website timeout: {url}")
        except requests.exceptions.ConnectionError:
            lead.issues_found.append("Website Down")
            logger.warning(f"Connection error: {url}")
        except requests.exceptions.TooManyRedirects:
            lead.issues_found.append("Website Down")
            logger.warning(f"Too many redirects: {url}")
        except requests.exceptions.RequestException as e:
            lead.issues_found.append("Website Down")
            logger.warning(f"Request error for {url}: {e}")
        except Exception as e:
            lead.issues_found.append("Website Down")
            logger.error(f"Unexpected error auditing {url}: {e}")

        # Determine Status
        if lead.issues_found:
            lead.lead_status = HOT_STATUS
            logger.info(f"HOT LEAD FOUND! Business: {lead.business_name} | Issues: {', '.join(lead.issues_found)}")
        else:
            lead.lead_status = COLD_STATUS
            logger.info(f"COLD LEAD: {lead.business_name} | No issues found.")

        return lead