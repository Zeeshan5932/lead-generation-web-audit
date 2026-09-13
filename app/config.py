import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Lead_Agent_Master")
    GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials/google-service-account.json")
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
    MIN_DELAY = float(os.getenv("MIN_DELAY", "1.0"))
    MAX_DELAY = float(os.getenv("MAX_DELAY", "2.0"))
    RESULTS_PER_SEARCH = int(os.getenv("RESULTS_PER_SEARCH", "20"))

    @classmethod
    def validate(cls):
        if not cls.SERPER_API_KEY:
            raise ValueError("SERPER_API_KEY is required in .env")
        if not os.path.exists(cls.GOOGLE_CREDENTIALS_FILE):
            raise FileNotFoundError(f"Google credentials file not found at {cls.GOOGLE_CREDENTIALS_FILE}")

config = Config()