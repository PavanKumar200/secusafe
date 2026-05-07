"""
threat_intel.py — Free threat intelligence layer.
Checks URLs against URLhaus, Google Safe Browsing, PhishTank (local CSV),
and OpenPhish (local feed). No API key required for most checks.
"""
import os
import csv
import logging
import requests
from config import (
    GOOGLE_SB_API_KEY,
    PHISHTANK_FEED,
    OPENPHISH_FEED,
)

logger = logging.getLogger(__name__)

# ── Preload local feeds at module import time ──────────────────────────────

def _load_phishtank_set():
    """Load PhishTank CSV feed into a set for O(1) lookup."""
    urls = set()
    if not os.path.exists(PHISHTANK_FEED):
        logger.info("PhishTank feed not found. Run setup_data.py to download it.")
        return urls
    try:
        with open(PHISHTANK_FEED, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("url", "").strip().lower().rstrip("/")
                if url:
                    urls.add(url)
        logger.info(f"PhishTank feed loaded: {len(urls)} URLs")
    except Exception as e:
        logger.warning(f"Failed to load PhishTank feed: {e}")
    return urls


def _load_openphish_set():
    """Load OpenPhish feed text file into a set for O(1) lookup."""
    urls = set()
    if not os.path.exists(OPENPHISH_FEED):
        logger.info("OpenPhish feed not found. Run setup_data.py to download it.")
        return urls
    try:
        with open(OPENPHISH_FEED, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                url = line.strip().lower().rstrip("/")
                if url:
                    urls.add(url)
        logger.info(f"OpenPhish feed loaded: {len(urls)} URLs")
    except Exception as e:
        logger.warning(f"Failed to load OpenPhish feed: {e}")
    return urls


# Load feeds once at startup
_phishtank_urls: set = _load_phishtank_set()
_openphish_urls: set = _load_openphish_set()


def _normalize_url(url: str) -> str:
    """Normalize a URL for consistent comparison."""
    return url.strip().lower().rstrip("/")


# ── Individual check functions ─────────────────────────────────────────────

def check_urlhaus(url: str) -> dict:
    """
    Check a URL against the URLhaus database (no API key needed).

    Returns:
        dict with keys: listed (bool), threat (str|None), tags (list)
    """
    default = {"listed": False, "threat": None, "tags": []}
    try:
        resp = requests.post(
            "https://urlhaus-api.abuse.ch/v1/url/",
            data={"url": url},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("query_status") == "is_hosting_malware":
                return {
                    "listed": True,
                    "threat": data.get("threat", "malware"),
                    "tags": data.get("tags") or [],
                }
            return default
    except Exception as e:
        logger.warning(f"URLhaus check failed: {e}")
    return default


def check_google_safe_browsing(url: str) -> dict:
    """
    Check a URL against Google Safe Browsing API v4.
    Requires GOOGLE_SB_API_KEY in environment.

    Returns:
        dict with keys: flagged (bool), threat_type (str|None)
    """
    default = {"flagged": False, "threat_type": None}
    if not GOOGLE_SB_API_KEY:
        return default
    try:
        api_url = (
            "https://safebrowsing.googleapis.com/v4/threatMatches:find"
            f"?key={GOOGLE_SB_API_KEY}"
        )
        payload = {
            "client": {"clientId": "security-scanner", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        resp = requests.post(api_url, json=payload, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            matches = data.get("matches", [])
            if matches:
                threat_type = matches[0].get("threatType", "UNKNOWN")
                return {"flagged": True, "threat_type": threat_type}
    except Exception as e:
        logger.warning(f"Google Safe Browsing check failed: {e}")
    return default


def get_domain_reputation(domain: str) -> dict:
    """
    Look up WHOIS data for a domain to get age and registrar.

    Returns:
        dict with keys: domain_age_days (int), registrar (str), is_new_domain (bool)
    """
    default = {"domain_age_days": -1, "registrar": "Unknown", "is_new_domain": False}
    try:
        import whois
        from datetime import datetime, timezone
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        registrar = w.registrar or "Unknown"
        if creation:
            now = datetime.now(timezone.utc)
            if creation.tzinfo is None:
                creation = creation.replace(tzinfo=timezone.utc)
            age_days = max(0, (now - creation).days)
            return {
                "domain_age_days": age_days,
                "registrar": str(registrar),
                "is_new_domain": age_days < 30,
            }
    except Exception as e:
        logger.warning(f"WHOIS reputation check failed for {domain}: {e}")
    return default


def check_phishtank_local(url: str) -> bool:
    """
    Check URL against locally loaded PhishTank feed (O(1) set lookup).

    Returns:
        True if URL is in PhishTank, False otherwise.
    """
    return _normalize_url(url) in _phishtank_urls


def check_openphish_local(url: str) -> bool:
    """
    Check URL against locally loaded OpenPhish feed (O(1) set lookup).

    Returns:
        True if URL is in OpenPhish feed, False otherwise.
    """
    return _normalize_url(url) in _openphish_urls


def run_all_intel_checks(url: str, domain: str) -> dict:
    """
    Master aggregator: runs all threat intelligence checks and combines results.

    Args:
        url: Full URL string to check.
        domain: Registered domain (e.g. 'example.com').

    Returns:
        Combined dict with urlhaus, google_sb, phishtank, openphish results
        and an intel_risk_boost integer (added to ML score, capped at 100).
    """
    urlhaus_result = check_urlhaus(url)
    google_sb_result = check_google_safe_browsing(url)
    phishtank_hit = check_phishtank_local(url)
    openphish_hit = check_openphish_local(url)

    boost = 0
    if urlhaus_result["listed"]:
        boost += 40
    if google_sb_result["flagged"]:
        boost += 35
    if phishtank_hit:
        boost += 30
    if openphish_hit:
        boost += 25

    return {
        "urlhaus": urlhaus_result,
        "google_sb": google_sb_result,
        "phishtank": phishtank_hit,
        "openphish": openphish_hit,
        "intel_risk_boost": min(boost, 100),
    }
