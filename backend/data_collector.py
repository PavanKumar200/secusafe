import sys
import os
import csv
import logging
import time

# Add backend to path so we can import scraper and ml_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import WebScraper
from ml_model import PhishingDetector
from config import TRAINING_DATA_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

PHISHING_URLS = [
    "https://airbnb-seven-lime.vercel.app/",
    "https://request-facebook.invoice-ads-manager.com/",
    "https://netflix-kh-one.vercel.app/",
    "http://account-trust-center.pages.dev/appeal_form",
    "http://om-choukse.github.io/new-html",
    "http://bcrenlineass.vercel.app/",
    "http://gemini.588886.xyz/",
    "https://kuwcoinlogin.webflow.io/",
    "https://amazon-clone-only-frontend.vercel.app/",
    "https://paypalfrancetransfert23-cell.github.io/Cr-dit-agricole.-fr-/",
    "https://pt-shopee3335.blogspot.com/",
    "http://amazonwebservices.security-unauthorised-request.com/login/",
    "http://robloxt.cv/users/410369504/profile",
    "https://www.netflix-clone-site.vercel.app/",
    "http://sparkasseonline.org/",
    "http://lnslagram.github.io/lnslagram",
    "http://telkom-logiin-page.weebly.com/",
    "https://user-account.accounts-admin-agency.com/",
    "https://facebook-setting.invoice-ads-process.com/",
    "https://ca-ndax.godaddysites.com/",
    "https://signdocs-beta.vercel.app/",
    "http://www.authentication.ms/E.dbZ0Z8p3BkUiMPU8pQ",
    "https://uerplldd_olgim.godaddysites.com/",
    "https://okos.top/auto_mercari.php/",
    "https://facebookclone-pearl.vercel.app/",
    "https://ferrmainbutcure.wasmer.app/",
    "https://adaest.top/",
    "https://www.elmatesito042.vercel.app/",
    "https://roblox.et/communities/6910245057/BladeBallX",
    "http://meta-msk-us-loggin.godaddysites.com/",
    "http:// gestion365plus.webcindario.com/",
    "https://s4w.in/www-roblox-com-users-8280246711-profile",
    "https://fbgamertopcd.fwh.is/",
    "https://authentication.ms/E.Ua86a7dtqAMJag?56d5-4408-93ea-6f8d55a827dc",
    "https://login.alexa.abductist.duckdns.org/",
    "https://ojin.standard.us-east-1.oortstorages.com/inep.znc",
    "https://mimosawedding.vn/wp-admin/user/ING-/Archive/",
    "https://meta-option.bussines-partner-agency.com/",
    "https://emma-jack84756.pages.dev/help/contact/94713647682710",
    "https://sourcefuel.co.zw/DE33333DHLweb06052026g3mbh/load.php/",
    "http://blue-butterfly-a450.vailtaatpyaixmbldelttde.workers.dev/meta.help",
    "https://safebank.onl/s/63BZGFSVBWSFCDX7Y9/584dd8/90eab167-7429-489f-99f6-ce86e8d0d81a",
    "https://curly-violet-5dd4.jujuan98.workers.dev/0x69c69d7365324bb05a0a5b71",
    "https://yqgqt-mnec-vbcz.c-0zsklfju.workers.dev/l/MCnGAKFKxZE",
    "https://santanderaumenta.pages.dev/index.php",
    "https://cee079b8.wwww3e.pages.dev/freshPO",
    "http://zapview.goserver.sbs/",
    "http://news.primesignals.sbs/",
    "http://stemguard-verify.world/",
    "https://x32bc232.duckdns.org/"
]

BENIGN_URLS = [
    "https://google.com", "https://facebook.com", "https://youtube.com",
    "https://amazon.com", "https://wikipedia.org", "https://twitter.com",
    "https://instagram.com", "https://linkedin.com", "https://github.com",
    "https://microsoft.com", "https://apple.com", "https://netflix.com",
    "https://reddit.com", "https://stackoverflow.com", "https://quora.com",
    "https://medium.com", "https://nytimes.com", "https://bbc.com",
    "https://cnn.com", "https://theguardian.com", "https://forbes.com",
    "https://bloomberg.com", "https://reuters.com", "https://wsj.com",
    "https://usatoday.com", "https://latimes.com", "https://washingtonpost.com",
    "https://huffpost.com", "https://buzzfeed.com", "https://vice.com",
    "https://vox.com", "https://theverge.com", "https://wired.com",
    "https://techcrunch.com", "https://engadget.com", "https://gizmodo.com",
    "https://mashable.com", "https://cnet.com", "https://zdnet.com",
    "https://digitaltrends.com", "https://lifehacker.com", "https://pcworld.com",
    "https://macworld.com", "https://tomsguide.com", "https://ign.com",
    "https://gamespot.com", "https://kotaku.com", "https://polygon.com",
    "https://eurogamer.net", "https://rockpapershotgun.com"
]

def collect_data():
    detector = PhishingDetector()
    all_data = []

    # Process Phishing
    logger.info(f"Collecting features for {len(PHISHING_URLS)} phishing URLs...")
    for url in PHISHING_URLS:
        try:
            scraper = WebScraper(url)
            # Use quick scrape to avoid long timeouts on dead phishing links
            if scraper.scrape():
                features = scraper.extract_features()
                features['label'] = 1
                all_data.append(features)
                logger.info(f"[+] Scraped phishing: {url}")
            else:
                logger.warning(f"[-] Failed phishing: {url}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        time.sleep(1)

    # Process Benign
    logger.info(f"Collecting features for {len(BENIGN_URLS)} benign URLs...")
    for url in BENIGN_URLS:
        try:
            scraper = WebScraper(url)
            if scraper.scrape():
                features = scraper.extract_features()
                features['label'] = 0
                all_data.append(features)
                logger.info(f"[+] Scraped benign: {url}")
            else:
                logger.warning(f"[-] Failed benign: {url}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        time.sleep(1)

    if not all_data:
        logger.error("No data collected!")
        return

    # Save to CSV
    os.makedirs(os.path.dirname(TRAINING_DATA_FILE), exist_ok=True)
    keys = list(all_data[0].keys())
    with open(TRAINING_DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_data)
    
    logger.info(f"Saved {len(all_data)} samples to {TRAINING_DATA_FILE}")

    # Trigger Retrain
    logger.info("Triggering model retraining...")
    detector.retrain()
    logger.info("Model retrained successfully!")

if __name__ == "__main__":
    collect_data()
