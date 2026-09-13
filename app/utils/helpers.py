import re
import time
import random
from typing import List
from app.config import config
from app.models import Lead

def normalize_url(url: str) -> str:
    return url.strip().lower()

def normalize_business_name(name: str) -> str:
    return re.sub(r'[^a-z0-9\s]', '', name.lower()).strip()

def clean_phone(phone: str) -> str:
    return re.sub(r'[^0-9+]', '', phone).strip()

def clean_email(email: str) -> str:
    return email.strip().lower()

def random_delay():
    delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
    time.sleep(delay)

def deduplicate_leads(leads: List[Lead]) -> List[Lead]:
    seen = set()
    unique_leads = []
    
    for lead in leads:
        norm_name = normalize_business_name(lead.business_name)
        norm_website = normalize_url(lead.website_url) if lead.website_url else ""
        norm_address = normalize_business_name(lead.address)
        
        # Key strategy: name + website OR name + address
        key1 = f"{norm_name}|{norm_website}"
        key2 = f"{norm_name}|{norm_address}"
        
        if key1 not in seen and key2 not in seen:
            seen.add(key1)
            seen.add(key2)
            unique_leads.append(lead)
            
    return unique_leads