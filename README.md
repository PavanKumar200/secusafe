# Security Scanner & Phishing Detection Portal

## Project Overview
The project is a comprehensive, full-stack cybersecurity application designed to analyze web URLs in real-time and assess them for phishing attempts, dark patterns, and security vulnerabilities. It combines a seamless React web dashboard, a Python/Flask Machine Learning backend, and a Telegram Bot to provide users with multiple avenues to verify the authenticity and safety of any website.

## Key Features & Capabilities
* **Real-time URL Analysis:** Users can submit any URL to receive an instant security audit.
* **Machine Learning Powered:** Utilizes a trained `scikit-learn` model to calculate an accurate "Risk Score" (0-100%) and classify the site into Risk Levels (Low, Medium, High).
* **Deep Web Scraping:** Extracts over 13 key behavioral and structural features from a website (e.g., hidden elements, countdown timers, fake notifications, form counts, suspicious TLDs, and URL length).
* **Security Heuristics:** Beyond ML, it applies rule-based heuristic analysis to clearly define warnings, specific security issues, and actionable recommendations.
* **Omnichannel Access:** Users can analyze URLs via a modern React-based web dashboard or on-the-go via an integrated Telegram Bot.

## Technology Stack

### Frontend (Web Application)
* **Framework:** React.js (Bootstrapped with Vite/Create React App)
* **Styling & UI:** CSS for creating a dynamic, responsive, and card-based dashboard layout.
* **Libraries:** `axios` for API requests, `recharts` for visualizing security metrics.

### Backend (API & Analysis Core)
* **Framework:** Python with Flask & Flask-CORS.
* **API:** RESTful architecture primarily exposing an `/api/analyze` POST endpoint.
* **Web Scraping Engine:** `BeautifulSoup4` and `requests` to silently fetch and parse HTML DOMs.
* **Security Tools:** `tldextract` and `urlparse3` to dissect domain structures and spot suspicious IP routings or abnormal subdomains.

### Machine Learning Engine
* **Libraries:** `scikit-learn`, `numpy`, `pandas`.
* **Model:** A custom-trained Phishing Detector (`models/trained_model.pkl`) trained on a dataset of safe and malicious site features.
* **Outputs:** Risk predictions and primary feature importances (e.g., highlighting *why* a site was flagged).

### Third-party Integration
* **Platform:** Telegram
* **Library:** `python-telegram-bot` (`asyncio`-driven)
* **Function:** An autonomous bot (`@BotFather` integration) that listens for user messages, hits the internal Flask API, and formats the JSON response into a user-friendly chat report with severity emojis.

## Architectural Data Flow
1. **Input:** A user submits a URL string (e.g., *cloudflare-login-update.com*) via the React Frontend or sending a message to the Telegram Bot.
2. **Scraping Phase (`scraper.py`):** The backend receives the request, prepends `https://` if missing, and scrapes the raw DOM.
3. **Feature Extraction:** The scraper packages the DOM data into a structured vector containing 13 unique data points.
4. **Prediction Phase (`ml_model.py`):** The numerical vector is fed into the ML model to output a `risk_score`.
5. **Heuristic Analysis (`analyzer.py`):** The system cross-references the features and risk score to generate human-readable strings (Warnings, Issues, Recommendations).
6. **Output:** A structured JSON object is returned to the client (Web or Bot) where it is beautifully rendered into a final Security Report.

## Getting Started

### Prerequisites
* Node.js & npm
* Python 3.9+

### Running the Backend
1. Navigate to the `backend` directory.
2. Create and activate a virtual environment (`python -m venv .venv`).
3. Install dependencies: `pip install -r requirements.txt`.
4. Start the Flask server: `python app.py`. (Runs on `http://localhost:5000`)
5. *(Optional)* Start the Telegram bot in a new terminal: `python telegram_bot.py`.

### Running the Frontend
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`.
3. Start the React development server: `npm start`. (Runs on `http://localhost:3000`)
