"""
analyzer.py — Upgraded heuristic security analysis engine.
Consumes 20+ features + threat intel to produce warnings, issues,
and a final risk score capped at 100.
"""
import logging

logger = logging.getLogger(__name__)


class SecurityAnalyzer:
    """Rule-based heuristic analyzer that complements the ML model."""

    def analyze_url(self, url: str, features: dict, ml_score: float,
                    intel_result: dict = None) -> dict:
        """
        Generate a complete security analysis report.

        Args:
            url: The full URL string analyzed.
            features: Feature dict returned by scraper.extract_features().
            ml_score: Raw ML probability (0.0 – 1.0).
            intel_result: Optional dict from threat_intel.run_all_intel_checks().

        Returns:
            dict with risk_score, risk_level, issues, warnings, recommendation.
        """
        if intel_result is None:
            intel_result = {
                "urlhaus": {"listed": False, "threat": None, "tags": []},
                "google_sb": {"flagged": False, "threat_type": None},
                "phishtank": False,
                "openphish": False,
                "intel_risk_boost": 0,
            }

        issues = []
        warnings = []

        # ── Original heuristic rules ──────────────────────────────────────

        if features.get("has_ip"):
            issues.append({
                "type": "IP in URL",
                "severity": "high",
                "description": "URL contains IP address instead of domain name",
                "detail": "Legitimate sites use domain names, not IP addresses",
            })

        if features.get("suspicious_tld"):
            issues.append({
                "type": "Suspicious Domain",
                "severity": "medium",
                "description": "Uses suspicious top-level domain (.tk, .ml, .xyz, etc.)",
                "detail": "Free/uncommon TLDs are heavily used in phishing campaigns",
            })

        if not features.get("has_https"):
            issues.append({
                "type": "No HTTPS",
                "severity": "high",
                "description": "Site does not use a secure (HTTPS) connection",
                "detail": "Legitimate sites always use HTTPS for user data protection",
            })

        if features.get("hidden_elements", 0) > 5:
            issues.append({
                "type": "Dark Pattern",
                "severity": "medium",
                "description": f"Found {features['hidden_elements']} hidden elements",
                "detail": "Hidden elements may contain deceptive content or tracking code",
            })

        if features.get("urgency_keywords", 0) > 2:
            issues.append({
                "type": "Urgency Tactics",
                "severity": "medium",
                "description": f"Contains {features['urgency_keywords']} urgency keywords",
                "detail": "High-pressure language is a hallmark of social engineering attacks",
            })

        if features.get("fake_notifications", 0) > 0:
            issues.append({
                "type": "Fake Notifications",
                "severity": "high",
                "description": "Contains fake alert/notification/winner messages",
                "detail": "Deceptive notifications are used to trick users into clicking links",
            })

        if features.get("form_count", 0) > 3:
            warnings.append({
                "type": "Multiple Forms",
                "severity": "low",
                "description": f"Page contains {features['form_count']} forms",
                "detail": "Excessive forms may indicate credential harvesting",
            })

        # ── NEW heuristic rules (extended features) ───────────────────────

        domain_age = features.get("domain_age_days", -1)
        if 0 <= domain_age < 30:
            issues.append({
                "type": "New Domain",
                "severity": "high",
                "description": f"Domain registered very recently ({domain_age} days ago) — high phishing risk",
                "detail": "Phishing domains are typically registered just before attack campaigns",
            })

        typo_score = features.get("typosquat_score", 0)
        closest = features.get("closest_brand", "")
        if typo_score >= 1 and closest:
            issues.append({
                "type": "Typosquatting",
                "severity": "high" if typo_score == 2 else "medium",
                "description": f"Domain closely resembles '{closest}' — possible impersonation",
                "detail": "Typosquatted domains imitate trusted brands to steal credentials",
            })

        entropy = features.get("url_entropy", 0)
        if entropy > 3.8:
            warnings.append({
                "type": "High URL Entropy",
                "severity": "medium",
                "description": f"URL has unusually high character randomness (entropy={entropy:.2f})",
                "detail": "Algorithmically generated URLs are commonly used in phishing kits",
            })

        obfusc = features.get("js_obfuscation_count", 0)
        if obfusc > 3:
            issues.append({
                "type": "JS Obfuscation",
                "severity": "medium",
                "description": f"Heavy JavaScript obfuscation detected ({obfusc} instances)",
                "detail": "Malicious sites hide their true behavior behind obfuscated code",
            })

        redirect_count = features.get("redirect_count", 0)
        if redirect_count > 3:
            warnings.append({
                "type": "Redirect Chain",
                "severity": "medium",
                "description": f"URL passes through {redirect_count} redirects before reaching destination",
                "detail": "Long redirect chains can hide the true final destination",
            })

        if features.get("domain_changed_on_redirect", 0) == 1:
            issues.append({
                "type": "Domain Switch",
                "severity": "high",
                "description": "Final destination domain differs from the submitted URL",
                "detail": "Redirect destination switching is a common cloaking technique",
            })

        if features.get("ssl_self_signed", 0) == 1:
            warnings.append({
                "type": "Self-Signed SSL",
                "severity": "medium",
                "description": "SSL certificate is self-signed — not issued by a trusted authority",
                "detail": "Self-signed certs can be created by anyone and offer no trust guarantee",
            })

        ssl_days = features.get("ssl_days_remaining", -1)
        if 0 <= ssl_days < 10:
            warnings.append({
                "type": "Expiring SSL",
                "severity": "low",
                "description": f"SSL certificate expires in {ssl_days} days",
                "detail": "Legitimate organizations renew SSL certificates well before expiry",
            })

        if features.get("has_mx_record", 1) == 0:
            warnings.append({
                "type": "No MX Record",
                "severity": "low",
                "description": "Domain has no email (MX) records — unusual for a legitimate site",
                "detail": "Most real businesses have email infrastructure configured",
            })

        # ── Threat Intel warnings (prepended with [THREAT INTEL]) ─────────

        urlhaus = intel_result.get("urlhaus", {})
        if urlhaus.get("listed"):
            threat_name = urlhaus.get("threat", "malware")
            issues.insert(0, {
                "type": "Threat Intel: URLhaus",
                "severity": "high",
                "description": f"[THREAT INTEL] URLhaus confirms this URL distributes malware: {threat_name}",
                "detail": "URLhaus is maintained by abuse.ch and tracks active malware distribution URLs",
            })

        google_sb = intel_result.get("google_sb", {})
        if google_sb.get("flagged"):
            threat_type = google_sb.get("threat_type", "UNKNOWN")
            issues.insert(0, {
                "type": "Threat Intel: Google Safe Browsing",
                "severity": "high",
                "description": f"[THREAT INTEL] Google Safe Browsing flagged as: {threat_type}",
                "detail": "Google Safe Browsing protects billions of users from unsafe sites",
            })

        if intel_result.get("phishtank"):
            issues.insert(0, {
                "type": "Threat Intel: PhishTank",
                "severity": "high",
                "description": "[THREAT INTEL] URL is in PhishTank verified phishing database",
                "detail": "PhishTank contains community-verified active phishing URLs",
            })

        if intel_result.get("openphish"):
            issues.insert(0, {
                "type": "Threat Intel: OpenPhish",
                "severity": "high",
                "description": "[THREAT INTEL] URL is in OpenPhish active phishing feed",
                "detail": "OpenPhish uses ML to detect active phishing sites in real-time",
            })

        # ── Final score calculation ────────────────────────────────────────
        ml_score_pct = round(ml_score * 100, 2)
        intel_boost = intel_result.get("intel_risk_boost", 0)
        final_score = min(100, ml_score_pct + intel_boost)

        return {
            "risk_score": round(final_score, 2),
            "ml_score": round(ml_score_pct, 2),
            "intel_boost": intel_boost,
            "risk_level": self._get_risk_level(final_score),
            "issues": issues,
            "warnings": warnings,
            "recommendation": self._get_recommendation(final_score),
        }

    def _get_risk_level(self, score: float) -> str:
        """Map a 0-100 score to a human-readable risk level."""
        if score >= 85:
            return "Critical"
        elif score >= 60:
            return "High"
        elif score >= 30:
            return "Medium"
        else:
            return "Low"

    def _get_recommendation(self, score: float) -> str:
        """Generate a recommendation string based on score."""
        if score >= 85:
            return (
                "CRITICAL RISK: This site is highly likely to be malicious. "
                "Do NOT visit or enter any information. Block this URL immediately."
            )
        elif score >= 60:
            return (
                "HIGH RISK: This site shows multiple red flags. "
                "Do not enter personal or financial information."
            )
        elif score >= 30:
            return (
                "MEDIUM RISK: Exercise caution. Verify the site's legitimacy "
                "through official channels before providing any information."
            )
        else:
            return (
                "LOW RISK: This site appears relatively safe, but always "
                "verify URLs carefully before entering sensitive data."
            )