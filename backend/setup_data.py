"""
setup_data.py — One-time data download and model retraining script.
Downloads PhishTank, OpenPhish, Tranco top-100k, and UCI phishing dataset.
Merges into training_data.csv and retrains the ML model.

Run once: python setup_data.py
"""
import os
import csv
import zipfile
import io
import logging
import requests
from config import DATA_DIR, TRAINING_DATA_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

os.makedirs(DATA_DIR, exist_ok=True)

PHISHTANK_URL  = "http://data.phishtank.com/data/online-valid.csv"
OPENPHISH_URL  = "https://openphish.com/feed.txt"
TRANCO_URL     = "https://tranco-list.eu/top-1m.csv.zip"
UCI_ARFF_URL   = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00327/Training%20Dataset.arff"
)


def download(url: str, dest: str, timeout: int = 30) -> bool:
    """Download a file from URL to dest path. Returns True on success."""
    logger.info(f"Downloading {url} → {dest}")
    try:
        resp = requests.get(url, timeout=timeout, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
        logger.info(f"  Saved {os.path.getsize(dest):,} bytes")
        return True
    except Exception as e:
        logger.warning(f"  Download failed: {e}")
        return False


def download_phishtank():
    """Download PhishTank verified phishing feed."""
    dest = os.path.join(DATA_DIR, "phishtank_feed.csv")
    return download(PHISHTANK_URL, dest, timeout=60)


def download_openphish():
    """Download OpenPhish plain-text feed."""
    dest = os.path.join(DATA_DIR, "openphish_feed.txt")
    return download(OPENPHISH_URL, dest, timeout=30)


def download_tranco():
    """Download Tranco top-1M, unzip, save first 100,000 rows."""
    zip_dest = os.path.join(DATA_DIR, "tranco_top1m.zip")
    csv_dest = os.path.join(DATA_DIR, "tranco_top100k.csv")
    if not download(TRANCO_URL, zip_dest, timeout=120):
        return False
    try:
        with zipfile.ZipFile(zip_dest, "r") as zf:
            name = zf.namelist()[0]
            with zf.open(name) as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= 100_000:
                        break
                    lines.append(line.decode("utf-8").strip())
        with open(csv_dest, "w", encoding="utf-8") as f:
            f.write("rank,domain\n")
            f.writelines(l + "\n" for l in lines)
        os.remove(zip_dest)
        logger.info(f"  Tranco top-100k saved ({len(lines)} rows)")
        return True
    except Exception as e:
        logger.warning(f"  Tranco extraction failed: {e}")
        return False


def download_uci_arff():
    """Download UCI phishing dataset and convert ARFF to CSV."""
    arff_dest = os.path.join(DATA_DIR, "uci_phishing.arff")
    csv_dest  = os.path.join(DATA_DIR, "uci_phishing.csv")
    if not download(UCI_ARFF_URL, arff_dest, timeout=60):
        return False
    try:
        rows = []
        header = []
        in_data = False
        with open(arff_dest, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.lower().startswith("@attribute"):
                    parts = line.split()
                    header.append(parts[1])
                elif line.lower() == "@data":
                    in_data = True
                elif in_data and line and not line.startswith("%"):
                    rows.append(line.split(","))
        with open(csv_dest, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        logger.info(f"  UCI dataset converted: {len(rows)} rows")
        return True
    except Exception as e:
        logger.warning(f"  UCI conversion failed: {e}")
        return False


def build_training_data():
    """
    Merge phishing and benign URLs into training_data.csv.
    Uses PhishTank + OpenPhish URLs as phishing, Tranco as benign.
    Output: CSV with feature cols matching FEATURE_NAMES + 'label'.
    """
    from ml_model import FEATURE_NAMES

    phishing_urls = set()
    pt_path = os.path.join(DATA_DIR, "phishtank_feed.csv")
    op_path = os.path.join(DATA_DIR, "openphish_feed.txt")

    if os.path.exists(pt_path):
        with open(pt_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row.get("url", "").strip()
                if u:
                    phishing_urls.add(u)

    if os.path.exists(op_path):
        with open(op_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                u = line.strip()
                if u:
                    phishing_urls.add(u)

    benign_domains = []
    tr_path = os.path.join(DATA_DIR, "tranco_top100k.csv")
    if os.path.exists(tr_path):
        with open(tr_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                d = row.get("domain", "").strip()
                if d:
                    benign_domains.append(f"https://{d}")

    rows = []
    # Phishing rows: use URL-level heuristics (no live scraping)
    for url in list(phishing_urls)[:5000]:
        from urllib.parse import urlparse
        import math, re
        p = urlparse(url)
        freq = {}
        for ch in url: freq[ch] = freq.get(ch, 0) + 1
        length = len(url)
        entropy = -sum((c/length)*math.log2(c/length) for c in freq.values()) if length > 0 else 0
        row = {k: 0 for k in FEATURE_NAMES}
        row["url_length"] = length
        row["has_https"] = int(p.scheme == "https")
        row["url_entropy"] = round(entropy, 4)
        row["has_ip"] = int(bool(re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url)))
        row["label"] = 1
        rows.append(row)

    # Benign rows
    for url in list(benign_domains)[:5000]:
        from urllib.parse import urlparse
        import math
        p = urlparse(url)
        freq = {}
        for ch in url: freq[ch] = freq.get(ch, 0) + 1
        length = len(url)
        entropy = -sum((c/length)*math.log2(c/length) for c in freq.values()) if length > 0 else 0
        row = {k: 0 for k in FEATURE_NAMES}
        row["url_length"] = length
        row["has_https"] = 1
        row["has_mx_record"] = 1
        row["has_spf_record"] = 1
        row["has_dmarc_record"] = 1
        row["domain_age_days"] = 1000
        row["url_entropy"] = round(entropy, 4)
        row["label"] = 0
        rows.append(row)

    if not rows:
        logger.warning("No data to write to training_data.csv")
        return False

    with open(TRAINING_DATA_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FEATURE_NAMES + ["label"])
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"training_data.csv written: {len(rows)} rows")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Security Scanner — Data Setup")
    print("=" * 60)

    print("\n[1/4] Downloading PhishTank feed...")
    download_phishtank()

    print("\n[2/4] Downloading OpenPhish feed...")
    download_openphish()

    print("\n[3/4] Downloading Tranco top-100k...")
    download_tranco()

    print("\n[4/4] Downloading UCI phishing dataset...")
    download_uci_arff()

    print("\n[5/5] Building training_data.csv...")
    if build_training_data():
        print("\n[6/6] Retraining ML model...")
        from ml_model import PhishingDetector
        det = PhishingDetector()
        det.retrain()
        print("\nSetup complete! Restart app.py to use the new model.")
    else:
        print("\nSkipped retraining — no training data available.")

    print("=" * 60)
