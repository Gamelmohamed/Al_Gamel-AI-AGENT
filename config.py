import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "1_Knowledge"
CRM_DIR = BASE_DIR / "03_CRM"
EMAIL_AGENT_DIR = BASE_DIR / "02_Email_Agent"
LOGS_DIR = BASE_DIR / "06_Logs"

CUSTOMERS_FILE = CRM_DIR / "customers.json"
INQUIRIES_FILE = CRM_DIR / "inquiries.json"
FOLLOWUPS_FILE = CRM_DIR / "follow_ups.json"
PROCESSED_EMAILS_FILE = CRM_DIR / "processed_email_ids.json"

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash").strip()

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
