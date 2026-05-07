"""
app.py — Upgraded Flask API for the Security Scanner Portal.
Extended endpoints: /api/analyze, /api/feedback, /api/history,
/api/bulk, /api/report/<scan_id>, /api/health
"""
import os
import csv
import uuid
import logging
import logging.handlers
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io

from scraper import WebScraper
from ml_model import PhishingDetector
from analyzer import SecurityAnalyzer
from threat_intel import run_all_intel_checks, get_domain_reputation
from report_generator import generate_pdf_report
from config import (
    FLASK_PORT, FLASK_DEBUG, LOGS_DIR, DATA_DIR,
    MODEL_PATH, MODELS_DIR, SCAN_HISTORY_FILE, FEEDBACK_LOG_FILE
)
import tldextract

# ── Logging setup ──────────────────────────────────────────────────────────
os.makedirs(LOGS_DIR, exist_ok=True)
log_file = os.path.join(LOGS_DIR, "scanner.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ── In-memory scan cache (scan_id → result) ────────────────────────────────
_scan_cache: dict = {}
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.csv")

# ── Initialize ML model ────────────────────────────────────────────────────
detector = PhishingDetector()
analyzer = SecurityAnalyzer()


def _initialize_model():
    """Load or train the ML model on startup."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    try:
        if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 0:
            logger.info("Loading existing ML model...")
            detector.load_model(MODEL_PATH)
            logger.info("Model loaded successfully.")
        else:
            raise FileNotFoundError("Model file not found or empty")
    except Exception as e:
        logger.warning(f"Could not load model ({e}). Training fresh model with synthetic data...")
        _train_synthetic()


def _train_synthetic():
    """Train a quick synthetic model so the app starts immediately."""
    import numpy as np
    n = len(detector.feature_names)
    np.random.seed(42)
    n_samples = 400

    # Safe: shorter URLs, HTTPS, low entropy, legitimate DNS
    safe = np.random.uniform(0, 0.3, (n_samples // 2, n))
    safe[:, detector.feature_names.index("has_https")] = 1
    safe[:, detector.feature_names.index("has_mx_record")] = 1
    safe[:, detector.feature_names.index("domain_age_days")] = np.random.randint(365, 3000, n_samples // 2)

    # Malicious: longer URLs, IP-based, new domain, obfuscation
    malicious = np.random.uniform(0.4, 1.0, (n_samples // 2, n))
    malicious[:, detector.feature_names.index("has_https")] = np.random.choice([0, 1], n_samples // 2, p=[0.5, 0.5])
    malicious[:, detector.feature_names.index("domain_age_days")] = np.random.randint(0, 30, n_samples // 2)
    malicious[:, detector.feature_names.index("typosquat_score")] = np.random.choice([1, 2], n_samples // 2)

    X = np.vstack([safe, malicious])
    y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])
    idx = np.random.permutation(n_samples)
    detector.train(X[idx], y[idx])
    detector.save_model(MODEL_PATH)
    logger.info("Synthetic model trained and saved.")


_initialize_model()


# ── CSV helpers ────────────────────────────────────────────────────────────

def _append_csv(filepath: str, row: dict):
    """Append a row to a CSV file, creating headers if new."""
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _read_csv_last_n(filepath: str, n: int = 50) -> list:
    """Read the last N rows from a CSV file."""
    if not os.path.exists(filepath):
        return []
    rows = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        logger.warning(f"CSV read error: {e}")
    return rows[-n:]


# ── Core analysis function ─────────────────────────────────────────────────

def _run_analysis(url: str) -> dict:
    """Run the full analysis pipeline for a single URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    scan_id = str(uuid.uuid4())
    scanned_at = datetime.now(timezone.utc).isoformat()

    # Check whitelist first
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            whitelist_urls = [row.get("url") for row in csv.DictReader(f) if row.get("url")]
            if url in whitelist_urls:
                result = {
                    "url": url,
                    "scan_id": scan_id,
                    "scanned_at": scanned_at,
                    "risk_score": 0,
                    "ml_score": 0.0,
                    "intel_boost": 0.0,
                    "risk_level": "Low 🟢",
                    "issues": [],
                    "warnings": [],
                    "recommendations": ["This site has been verified as a False Positive and marked as safe."],
                    "recommendation": "This site has been verified as a False Positive and marked as safe.",
                    "features": {},
                    "feature_importances": {},
                    "threat_intel": {"urlhaus": {}, "google_sb": {}, "phishtank": False, "openphish": False},
                    "domain_info": {"closest_brand": ""},
                    "key_indicators": {}
                }
                _scan_cache[scan_id] = result
                _append_csv(SCAN_HISTORY_FILE, {"scan_id": scan_id, "url": url, "risk_score": 0, "risk_level": "Low 🟢", "scanned_at": scanned_at})
                return result

    # Scrape
    scraper = WebScraper(url)
    if not scraper.scrape():
        raise ValueError("Unable to access the URL.")

    features = scraper.extract_features()
    if not features:
        raise ValueError("Failed to extract features.")

    # Threat intel
    extracted = tldextract.extract(url)
    domain = extracted.registered_domain or extracted.domain
    intel_result = run_all_intel_checks(url, domain)

    # Domain reputation
    domain_rep = get_domain_reputation(domain)

    # ML prediction
    ml_score = detector.predict(features)
    feature_importances = detector.get_feature_importance(features)

    # Heuristic analysis
    analysis = analyzer.analyze_url(url, features, ml_score, intel_result)

    # Domain info block
    domain_info = {
        "domain_age_days": features.get("domain_age_days", domain_rep.get("domain_age_days", -1)),
        "registrar": domain_rep.get("registrar", "Unknown"),
        "is_new_domain": domain_rep.get("is_new_domain", False),
        "ssl_days_remaining": features.get("ssl_days_remaining", -1),
        "ssl_self_signed": bool(features.get("ssl_self_signed", 0)),
        "redirect_count": features.get("redirect_count", 0),
        "closest_brand": features.get("closest_brand", ""),
        "typosquat_score": features.get("typosquat_score", 0),
    }

    result = {
        "url": url,
        "scan_id": scan_id,
        "scanned_at": scanned_at,
        "risk_score": analysis["risk_score"],
        "ml_score": analysis["ml_score"],
        "intel_boost": analysis["intel_boost"],
        "risk_level": analysis["risk_level"],
        "issues": analysis["issues"],
        "warnings": analysis["warnings"],
        "recommendations": [analysis["recommendation"]],
        "recommendation": analysis["recommendation"],
        "features": features,
        "feature_importances": feature_importances,
        "threat_intel": {
            "urlhaus": intel_result.get("urlhaus", {}),
            "google_sb": intel_result.get("google_sb", {}),
            "phishtank": intel_result.get("phishtank", False),
            "openphish": intel_result.get("openphish", False),
        },
        "domain_info": domain_info,
        # Legacy: key_indicators for backward compatibility
        "key_indicators": feature_importances,
    }

    # Cache for PDF generation
    _scan_cache[scan_id] = result

    # Persist to history
    try:
        _append_csv(SCAN_HISTORY_FILE, {
            "scan_id": scan_id,
            "url": url,
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "scanned_at": scanned_at,
        })
    except Exception as e:
        logger.warning(f"Failed to write history: {e}")

    return result


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/api/analyze", methods=["POST"])
def analyze_url():
    """Analyze a single URL for security threats."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        url = data.get("url", "").strip()
        if not url:
            return jsonify({"error": "URL is required"}), 400

        result = _run_analysis(url)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"analyze_url error: {e}", exc_info=True)
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/api/bulk", methods=["POST"])
def bulk_analyze():
    """Analyze up to 20 URLs concurrently."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        urls = data.get("urls", [])
        if not urls or not isinstance(urls, list):
            return jsonify({"error": "urls list is required"}), 400
        if len(urls) > 20:
            return jsonify({"error": "Maximum 20 URLs per bulk request"}), 400

        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(_run_analysis, u): u for u in urls}
            for future in as_completed(future_to_url):
                original_url = future_to_url[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    errors.append({"url": original_url, "error": str(e)})

        results.sort(key=lambda r: r.get("risk_score", 0), reverse=True)
        return jsonify({"results": results, "errors": errors}), 200

    except Exception as e:
        logger.error(f"bulk_analyze error: {e}", exc_info=True)
        return jsonify({"error": f"Bulk analysis failed: {str(e)}"}), 500


@app.route("/api/history", methods=["GET"])
def get_history():
    """Return the last 50 scan records."""
    try:
        rows = _read_csv_last_n(SCAN_HISTORY_FILE, 50)
        return jsonify({"history": rows}), 200
    except Exception as e:
        logger.error(f"get_history error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Accept user feedback on a scan result for future retraining."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        scan_id = data.get("scan_id", "").strip()
        correct_label = data.get("correct_label")
        if not scan_id or correct_label not in (0, 1):
            return jsonify({"error": "scan_id and correct_label (0 or 1) required"}), 400

        scan_result = _scan_cache.get(scan_id, {})
        url = scan_result.get("url", "")
        
        _append_csv(FEEDBACK_LOG_FILE, {
            "scan_id": scan_id,
            "url": url,
            "correct_label": correct_label,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        })

        if correct_label == 0 and url:
            _append_csv(WHITELIST_FILE, {
                "url": url,
                "added_at": datetime.now(timezone.utc).isoformat(),
                "from_scan_id": scan_id
            })
            
        return jsonify({"message": "Feedback recorded. Thank you!"}), 200

    except Exception as e:
        logger.error(f"submit_feedback error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/report/<scan_id>", methods=["GET"])
def get_pdf_report(scan_id: str):
    """Generate and return a PDF report for a given scan ID."""
    try:
        scan_result = _scan_cache.get(scan_id)
        if not scan_result:
            return jsonify({"error": "Scan not found. Reports expire after server restart."}), 404

        pdf_bytes = generate_pdf_report(scan_result)
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"security_report_{scan_id[:8]}.pdf",
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "Security Portal API is running",
        "model_features": len(detector.feature_names),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), 200


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)