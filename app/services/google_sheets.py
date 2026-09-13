import gspread
import logging
from typing import List
from app.config import config
from app.models import Lead
from app.constants import (
    SHEET_INPUTS, SHEET_ALL_LEADS, SHEET_HOT_LEADS,
    INPUTS_COLUMNS, LEAD_COLUMNS
)

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    def __init__(self):
        try:
            gc = gspread.service_account(filename=config.GOOGLE_CREDENTIALS_FILE)
            self.sheet = gc.open(config.GOOGLE_SHEET_NAME)
            logger.info(f"Successfully connected to Google Sheet: {config.GOOGLE_SHEET_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise

    def get_inputs(self) -> List[dict]:
        try:
            worksheet = self.sheet.worksheet(SHEET_INPUTS)
            records = worksheet.get_all_records()
            # Filter out empty rows
            valid_inputs = []
            for row in records:
                keyword = str(row.get("Keyword", "")).strip()
                location = str(row.get("Location", "")).strip()
                if keyword and location:
                    valid_inputs.append({"keyword": keyword, "location": location})
            return valid_inputs
        except gspread.WorksheetNotFound:
            logger.error(f"Worksheet '{SHEET_INPUTS}' not found.")
            return []
        except Exception as e:
            logger.error(f"Error reading inputs: {e}")
            return []

    def initialize_headers(self):
        for sheet_name in [SHEET_ALL_LEADS, SHEET_HOT_LEADS]:
            try:
                worksheet = self.sheet.worksheet(sheet_name)
                if not worksheet.get_all_values():
                    worksheet.append_row(LEAD_COLUMNS)
                    logger.info(f"Initialized headers for {sheet_name}")
            except gspread.WorksheetNotFound:
                logger.warning(f"Worksheet '{sheet_name}' not found. Please create it.")
            except Exception as e:
                logger.error(f"Error initializing headers for {sheet_name}: {e}")

    def _clear_data_rows(self, worksheet_name: str):
        try:
            worksheet = self.sheet.worksheet(worksheet_name)
            # Clear all, then re-add headers to ensure clean state
            worksheet.clear()
            worksheet.append_row(LEAD_COLUMNS)
            logger.info(f"Cleared existing data in {worksheet_name}")
        except Exception as e:
            logger.error(f"Error clearing {worksheet_name}: {e}")

    def write_all_leads(self, leads: List[Lead]):
        self._clear_data_rows(SHEET_ALL_LEADS)
        try:
            worksheet = self.sheet.worksheet(SHEET_ALL_LEADS)
            if leads:
                rows = [lead.to_row() for lead in leads]
                worksheet.append_rows(rows)
                logger.info(f"Wrote {len(leads)} leads to {SHEET_ALL_LEADS}")
        except Exception as e:
            logger.error(f"Error writing to {SHEET_ALL_LEADS}: {e}")

    def write_hot_leads(self, leads: List[Lead]):
        self._clear_data_rows(SHEET_HOT_LEADS)
        try:
            worksheet = self.sheet.worksheet(SHEET_HOT_LEADS)
            hot_leads = [lead for lead in leads if lead.lead_status == "HOT"]
            if hot_leads:
                rows = [lead.to_row() for lead in hot_leads]
                worksheet.append_rows(rows)
                logger.info(f"Wrote {len(hot_leads)} HOT leads to {SHEET_HOT_LEADS}")
        except Exception as e:
            logger.error(f"Error writing to {SHEET_HOT_LEADS}: {e}")