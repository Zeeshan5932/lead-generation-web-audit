import logging
from typing import List, Dict, Any
from app.services import SerperClient, WebsiteAuditor, GoogleSheetsService
from app.config import config
from app.models import Lead
from app.utils.helpers import deduplicate_leads
from app.constants import HOT_STATUS, COLD_STATUS

logger = logging.getLogger(__name__)

class LeadProcessor:
    def __init__(self):
        self.serper = SerperClient(api_key=config.SERPER_API_KEY)
        self.auditor = WebsiteAuditor()
        self.sheets = GoogleSheetsService()

    def run(self) -> Dict[str, Any]:
        logger.info("=" * 50)
        logger.info("LEAD GENERATION AGENT STARTED")
        logger.info("=" * 50)

        inputs = self.sheets.get_inputs()
        if not inputs:
            logger.warning("No valid inputs found in Google Sheet.")
            return {"status": "completed", "total_leads": 0, "hot_leads": 0, "cold_leads": 0, "websites_audited": 0}

        all_leads: List[Lead] = []
        websites_audited = 0

        for inp in inputs:
            keyword = inp["keyword"]
            location = inp["location"]
            logger.info(f"\nKeyword: {keyword} | Location: {location}")
            
            raw_leads = self.serper.search_businesses(keyword, location, config.RESULTS_PER_SEARCH)
            
            for lead in raw_leads:
                if lead.website_url:
                    logger.info(f"Auditing Website: {lead.business_name} | {lead.website_url}")
                    audited_lead = self.auditor.audit(lead)
                    websites_audited += 1
                    all_leads.append(audited_lead)
                else:
                    lead.issues_found.append("No Website")
                    lead.lead_status = HOT_STATUS
                    logger.info(f"HOT LEAD FOUND! Business: {lead.business_name} | Issues: No Website")
                    all_leads.append(lead)

        # Deduplicate
        unique_leads = deduplicate_leads(all_leads)
        
        hot_count = sum(1 for lead in unique_leads if lead.lead_status == HOT_STATUS)
        cold_count = sum(1 for lead in unique_leads if lead.lead_status == COLD_STATUS)

        # Write to sheets
        self.sheets.initialize_headers()
        self.sheets.write_all_leads(unique_leads)
        self.sheets.write_hot_leads(unique_leads)

        logger.info("\n" + "=" * 50)
        logger.info("PROCESS COMPLETED")
        logger.info("=" * 50)
        logger.info(f"Total businesses found: {len(all_leads)}")
        logger.info(f"Unique businesses processed: {len(unique_leads)}")
        logger.info(f"Websites audited: {websites_audited}")
        logger.info(f"HOT leads: {hot_count}")
        logger.info(f"COLD leads: {cold_count}")
        logger.info("=" * 50)

        return {
            "status": "completed",
            "total_leads": len(unique_leads),
            "hot_leads": hot_count,
            "cold_leads": cold_count,
            "websites_audited": websites_audited
        }