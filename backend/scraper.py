"""
scraper.py — Extended web scraper with 20+ feature extraction.
Adds: URL entropy, domain age, redirect chain, DNS signals,
typosquatting detection, JS obfuscation, and SSL certificate info.
"""
import re
import math
import ssl
import socket
import logging
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tldextract

logger = logging.getLogger(__name__)

# ── Top 30 brand domains for typosquat detection ──────────────────────────
BRAND_DOMAINS = [
    "google.com", "facebook.com", "apple.com", "amazon.com", "microsoft.com",
    "paypal.com", "instagram.com", "twitter.com", "linkedin.com", "netflix.com",
    "bankofamerica.com", "chase.com", "wellsfargo.com", "dropbox.com", "adobe.com",
    "spotify.com", "github.com", "yahoo.com", "outlook.com", "office.com",
    "whatsapp.com", "telegram.org", "discord.com", "reddit.com", "wikipedia.org",
    "ebay.com", "walmart.com", "target.com", "coinbase.com", "binance.com",
]


class WebScraper:
    def __init__(self, url):
        self.url = url
        self.parsed_url = urlparse(url)
        self.soup = None
        self.content = None
        self.response = None

    # ── Public Methods ────────────────────────────────────────────────────

    def scrape(self):
        """Fetch the URL and parse the HTML. Returns True on success."""
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
            self.response = requests.get(
                self.url, headers=headers, timeout=10, allow_redirects=True
            )
            self.content = self.response.text
            self.soup = BeautifulSoup(self.content, "html.parser")
            return True
        except Exception as e:
            logger.error(f"Scraping error for {self.url}: {e}")
            return False

    def extract_features(self):
        """Extract all 20+ features from the scraped page."""
        if not self.soup:
            return None

        # ── Original 13 features ─────────────────────────────────────────
        features = {
            "url_length": len(self.url),
            "has_ip": self._check_ip_in_url(),
            "subdomain_count": self._count_subdomains(),
            "suspicious_tld": self._check_suspicious_tld(),
            "form_count": len(self.soup.find_all("form")),
            "input_count": len(self.soup.find_all("input")),
            "external_links": self._count_external_links(),
            "hidden_elements": self._count_hidden_elements(),
            "urgency_keywords": self._check_urgency(),
            "countdown_timers": len(
                self.soup.find_all(
                    string=lambda t: t and "timer" in t.lower()
                )
            ),
            "fake_notifications": self._check_fake_notifications(),
            "has_https": int(self.parsed_url.scheme == "https"),
            "popup_count": len(
                self.soup.find_all(
                    ["div"],
                    class_=lambda x: x and "popup" in " ".join(x).lower(),
                )
            ),
        }

        # ── NEW Feature 14: URL entropy ───────────────────────────────────
        features["url_entropy"] = self._url_entropy()

        # ── NEW Feature 15: Domain age ────────────────────────────────────
        features["domain_age_days"] = self._domain_age_days()

        # ── NEW Features 16-17: Redirect chain ───────────────────────────
        redirect_info = self._redirect_chain()
        features["redirect_count"] = redirect_info["redirect_count"]
        features["domain_changed_on_redirect"] = redirect_info["domain_changed"]

        # ── NEW Features 18-20: DNS signals ───────────────────────────────
        dns_info = self._dns_signals()
        features["has_mx_record"] = dns_info["has_mx"]
        features["has_spf_record"] = dns_info["has_spf"]
        features["has_dmarc_record"] = dns_info["has_dmarc"]

        # ── NEW Features 21-22: Typosquatting ────────────────────────────
        typo_info = self._typosquat_check()
        features["typosquat_score"] = typo_info["score"]
        features["closest_brand"] = typo_info["closest_brand"]

        # ── NEW Feature 23: JS obfuscation ───────────────────────────────
        features["js_obfuscation_count"] = self._js_obfuscation_count()

        # ── NEW Features 24-25: SSL info ─────────────────────────────────
        ssl_info = self._ssl_info()
        features["ssl_days_remaining"] = ssl_info["days_remaining"]
        features["ssl_self_signed"] = ssl_info["self_signed"]

        return features

    # ── Original private helpers ──────────────────────────────────────────

    def _check_ip_in_url(self):
        ip_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        return 1 if re.search(ip_pattern, self.url) else 0

    def _count_subdomains(self):
        extracted = tldextract.extract(self.url)
        return len(extracted.subdomain.split(".")) if extracted.subdomain else 0

    def _check_suspicious_tld(self):
        suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".pw"]
        domain_lower = self.url.lower()
        return 1 if any(tld in domain_lower for tld in suspicious_tlds) else 0

    def _count_external_links(self):
        links = self.soup.find_all("a", href=True)
        domain = tldextract.extract(self.url).domain
        external = sum(1 for link in links if domain not in link["href"])
        return external

    def _count_hidden_elements(self):
        hidden = self.soup.find_all(
            style=lambda s: s and "display:none" in s.replace(" ", "")
        )
        hidden += self.soup.find_all(type="hidden")
        return len(hidden)

    def _check_urgency(self):
        urgency_words = [
            "urgent", "limited time", "act now", "expires",
            "hurry", "last chance", "immediately", "verify now",
        ]
        text = self.soup.get_text().lower()
        return sum(1 for word in urgency_words if word in text)

    def _check_fake_notifications(self):
        notification_indicators = ["notification", "alert", "warning", "winner", "congratulations"]
        divs = self.soup.find_all("div")
        count = 0
        for div in divs:
            text = div.get_text().lower()
            if any(ind in text for ind in notification_indicators):
                count += 1
        return count

    # ── New private helpers ───────────────────────────────────────────────

    def _url_entropy(self):
        """Calculate Shannon entropy of the URL string."""
        try:
            url = self.url
            if not url:
                return 0.0
            freq = {}
            for ch in url:
                freq[ch] = freq.get(ch, 0) + 1
            length = len(url)
            entropy = -sum(
                (count / length) * math.log2(count / length)
                for count in freq.values()
            )
            return round(entropy, 4)
        except Exception as e:
            logger.warning(f"Entropy calc failed: {e}")
            return 0.0

    def _domain_age_days(self):
        """Return domain age in days using python-whois. Returns -1 on failure."""
        try:
            import whois
            domain = tldextract.extract(self.url).registered_domain
            w = whois.whois(domain)
            creation = w.creation_date
            if isinstance(creation, list):
                creation = creation[0]
            if creation:
                # Make both timezone-aware or both naive
                now = datetime.now(timezone.utc)
                if creation.tzinfo is None:
                    creation = creation.replace(tzinfo=timezone.utc)
                age = (now - creation).days
                return max(0, age)
        except Exception as e:
            logger.warning(f"WHOIS lookup failed for {self.url}: {e}")
        return -1

    def _redirect_chain(self):
        """Count redirects and whether final domain differs from original."""
        try:
            if self.response is None:
                return {"redirect_count": 0, "domain_changed": 0}
            redirect_count = len(self.response.history)
            original_domain = tldextract.extract(self.url).registered_domain
            final_domain = tldextract.extract(self.response.url).registered_domain
            domain_changed = int(
                original_domain != final_domain and bool(final_domain)
            )
            return {"redirect_count": redirect_count, "domain_changed": domain_changed}
        except Exception as e:
            logger.warning(f"Redirect chain check failed: {e}")
            return {"redirect_count": 0, "domain_changed": 0}

    def _dns_signals(self):
        """Check MX, SPF, and DMARC DNS records for the domain."""
        result = {"has_mx": 0, "has_spf": 0, "has_dmarc": 0}
        try:
            import dns.resolver
            domain = tldextract.extract(self.url).registered_domain
            if not domain:
                return result

            # MX records
            try:
                dns.resolver.resolve(domain, "MX", lifetime=5)
                result["has_mx"] = 1
            except Exception:
                pass

            # SPF in TXT records
            try:
                txt_records = dns.resolver.resolve(domain, "TXT", lifetime=5)
                for record in txt_records:
                    record_str = str(record)
                    if "v=spf1" in record_str:
                        result["has_spf"] = 1
                        break
            except Exception:
                pass

            # DMARC record
            try:
                dns.resolver.resolve(f"_dmarc.{domain}", "TXT", lifetime=5)
                result["has_dmarc"] = 1
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"DNS signal check failed: {e}")

        return result

    def _typosquat_check(self):
        """Check if domain closely resembles any top brand (Levenshtein distance 1-2)."""
        try:
            import Levenshtein
            extracted = tldextract.extract(self.url)
            check_domain = (
                f"{extracted.domain}.{extracted.suffix}".lower()
                if extracted.suffix
                else extracted.domain.lower()
            )
            if not check_domain:
                return {"score": 0, "closest_brand": ""}

            min_dist = 999
            closest = ""
            for brand in BRAND_DOMAINS:
                if check_domain == brand:
                    return {"score": 0, "closest_brand": brand}
                dist = Levenshtein.distance(check_domain, brand)
                if dist < min_dist:
                    min_dist = dist
                    closest = brand

            if min_dist == 1:
                return {"score": 2, "closest_brand": closest}
            elif min_dist == 2:
                return {"score": 1, "closest_brand": closest}
            else:
                return {"score": 0, "closest_brand": closest}

        except Exception as e:
            logger.warning(f"Typosquat check failed: {e}")
            return {"score": 0, "closest_brand": ""}

    def _js_obfuscation_count(self):
        """Count suspicious JavaScript patterns in the page source."""
        try:
            if not self.content:
                return 0
            patterns = [
                r"eval\s*\(",
                r"atob\s*\(",
                r"fromCharCode\s*\(",
                r"unescape\s*\(",
                r"[A-Za-z0-9+/]{100,}={0,2}",  # base64 blobs
            ]
            count = 0
            for pattern in patterns:
                matches = re.findall(pattern, self.content)
                count += len(matches)
            return count
        except Exception as e:
            logger.warning(f"JS obfuscation check failed: {e}")
            return 0

    def _ssl_info(self):
        """Fetch SSL certificate info: days remaining and if self-signed."""
        result = {"days_remaining": -1, "self_signed": 0}
        try:
            if self.parsed_url.scheme != "https":
                return result
            hostname = self.parsed_url.hostname
            if not hostname:
                return result

            ctx = ssl.create_default_context()
            conn = ctx.wrap_socket(
                socket.socket(socket.AF_INET),
                server_hostname=hostname,
            )
            conn.settimeout(5)
            conn.connect((hostname, 443))
            cert = conn.getpeercert()
            conn.close()

            # Days until expiry
            expire_str = cert.get("notAfter", "")
            if expire_str:
                expire_dt = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z")
                expire_dt = expire_dt.replace(tzinfo=timezone.utc)
                days = (expire_dt - datetime.now(timezone.utc)).days
                result["days_remaining"] = max(0, days)

            # Self-signed check (issuer == subject)
            issuer = dict(x[0] for x in cert.get("issuer", []))
            subject = dict(x[0] for x in cert.get("subject", []))
            if issuer == subject:
                result["self_signed"] = 1

        except Exception as e:
            logger.warning(f"SSL info check failed for {self.url}: {e}")

        return result