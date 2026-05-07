"""
config.py — Central configuration loader for Security Scanner Portal.
Reads environment variables from a .env file and exposes them as constants.
Prints a graceful warning (not an error) if optional keys are missing.
"""
import os
import logging
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

logger = logging.getLogger(__name__)

# ── Flask ──────────────────────────────────────────────────────────────────
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

# ── Telegram ───────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "8409651640:AAHinzRPqz1EO9lGO8FjG5FBINo2rHxFCEk"
)

# ── Optional API Keys ──────────────────────────────────────────────────────
GOOGLE_SB_API_KEY = os.getenv("GOOGLE_SB_API_KEY", "")
PHISHTANK_API_KEY = os.getenv("PHISHTANK_API_KEY", "")
VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

# ── Data paths ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

PHISHTANK_FEED = os.path.join(DATA_DIR, "phishtank_feed.csv")
OPENPHISH_FEED = os.path.join(DATA_DIR, "openphish_feed.txt")
SCAN_HISTORY_FILE = os.path.join(DATA_DIR, "scan_history.csv")
FEEDBACK_LOG_FILE = os.path.join(DATA_DIR, "feedback_log.csv")
TRAINING_DATA_FILE = os.path.join(DATA_DIR, "training_data.csv")
MODEL_PATH = os.path.join(MODELS_DIR, "trained_model.pkl")

# ── Ensure directories exist ───────────────────────────────────────────────
for _dir in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    os.makedirs(_dir, exist_ok=True)

# ── Warn on missing optional keys ─────────────────────────────────────────
def _warn_missing():
    """Print startup warnings for missing optional API keys."""
    if not GOOGLE_SB_API_KEY:
        print("[CONFIG] WARNING: GOOGLE_SB_API_KEY not set — Google Safe Browsing checks disabled.")
    if not PHISHTANK_API_KEY:
        print("[CONFIG] INFO: PHISHTANK_API_KEY not set — using local CSV feed fallback.")
    if not VIRUSTOTAL_API_KEY:
        print("[CONFIG] INFO: VIRUSTOTAL_API_KEY not set — VirusTotal checks disabled.")

_warn_missing()
