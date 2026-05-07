"""
telegram_bot.py — Upgraded Telegram bot with richer Markdown formatting,
inline keyboards, /history command, and /help command.
"""
import logging
import os
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler,
)
from config import TELEGRAM_BOT_TOKEN, FLASK_PORT

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# When deployed, set BACKEND_URL env var to the Render Flask service URL
# e.g. https://secusafe-api.onrender.com/api
_default_api = f"http://localhost:{FLASK_PORT}/api"
BASE_API = os.getenv("BACKEND_URL", _default_api)

# ── Helpers ────────────────────────────────────────────────────────────────

def _level_emoji(level: str) -> str:
    return {"Low": "🟢", "Medium": "🟡", "High": "🔴", "Critical": "💀"}.get(level, "⚪")


def _intel_badge(flagged: bool, label: str) -> str:
    return f"🚨 {label}: FLAGGED" if flagged else f"✅ {label}: Clean"


def _analyze_url_api(url: str) -> tuple:
    """Call the Flask backend. Returns (result_dict, error_str)."""
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        resp = requests.post(f"{BASE_API}/analyze", json={"url": url}, timeout=30)
        if resp.status_code == 200:
            return resp.json(), None
        return None, resp.json().get("error", "Unknown error")
    except requests.exceptions.Timeout:
        return None, "Request timed out. The site may be slow or unreachable."
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to backend. Is app.py running?"
    except Exception as e:
        return None, f"Error: {str(e)}"


def _format_scan_result(result: dict) -> str:
    """Format scan result as rich Telegram HTML message."""
    url = result.get("url", "N/A")
    score = result.get("risk_score", 0)
    level = result.get("risk_level", "Unknown")
    emoji = _level_emoji(level)
    rec = result.get("recommendation", "")

    intel = result.get("threat_intel", {})
    urlhaus = intel.get("urlhaus", {})
    google  = intel.get("google_sb", {})

    domain_info = result.get("domain_info", {})
    age = domain_info.get("domain_age_days", -1)
    domain_str = f"{age} days" if age >= 0 else "Unknown"
    ssl_days = domain_info.get("ssl_days_remaining", -1)
    ssl_str = f"{ssl_days} days" if ssl_days >= 0 else "No SSL"

    issues   = result.get("issues", [])   or []
    warnings = result.get("warnings", []) or []

    msg = (
        f"🔍 <b>Security Scan Report</b>\n"
        f"🌐 URL: <code>{url}</code>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🎯 Risk Score: <b>{score}/100</b>\n"
        f"🚦 Level: <b>{level}</b> {emoji}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🛡️ <b>Threat Intel</b>\n"
        f"• {_intel_badge(urlhaus.get('listed', False), 'URLhaus')}\n"
        f"• {_intel_badge(google.get('flagged', False), 'Google SB')}\n"
        f"• {_intel_badge(intel.get('phishtank', False), 'PhishTank')}\n"
        f"• {_intel_badge(intel.get('openphish', False), 'OpenPhish')}\n"
        f"━━━━━━━━━━━━━━━━\n"
    )

    def _fmt(item):
        if isinstance(item, dict):
            title = item.get("type", "")
            desc  = item.get("description", "")
            return f"<b>{title}</b>: {desc}" if (title and desc) else (desc or title or str(item))
        return str(item)

    if issues:
        msg += f"🚨 <b>Critical Issues ({len(issues)})</b>\n"
        for a in issues[:4]:
            msg += f"  ❗ {_fmt(a)}\n"
        msg += "\n"

    if warnings:
        msg += f"⚠️ <b>Warnings ({len(warnings)})</b>\n"
        for a in warnings[:3]:
            msg += f"  • {_fmt(a)}\n"
        msg += "━━━━━━━━━━━━━━━━\n"

    msg += (
        f"🌍 Domain Age: {domain_str}\n"
        f"🔒 SSL: {ssl_str}\n\n"
        f"<i>💡 {rec}</i>"
    )
    return msg


def _build_inline_keyboard(scan_id: str, url: str) -> InlineKeyboardMarkup:
    """Build inline keyboard after a scan result."""
    keyboard = [
        [
            InlineKeyboardButton("📄 Get PDF Report", callback_data=f"pdf:{scan_id}"),
            InlineKeyboardButton("🔁 Scan Another", callback_data="scan_another"),
        ],
        [
            InlineKeyboardButton("⚠️ Report False Positive", callback_data=f"fp:{scan_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ── Command handlers ───────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    msg = (
        "<b>🔒 Security Scanner Bot</b>\n\n"
        "I analyze URLs for phishing, malware, and security threats using "
        "ML + threat intelligence.\n\n"
        "<b>How to use:</b>\n"
        "1. Send me any URL (e.g., <code>google.com</code>)\n"
        "2. Get a full security report in seconds\n\n"
        "<b>Commands:</b>\n"
        "/start - Show this message\n"
        "/help - Detailed usage guide\n"
        "/history - Your last 5 scans\n\n"
        "Just send me a URL to get started! 🚀"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    msg = (
        "<b>Security Scanner Bot — Help</b>\n\n"
        "🔍 <b>What I check:</b>\n"
        "• ML phishing detection (20+ signals)\n"
        "• URLhaus malware database\n"
        "• Google Safe Browsing\n"
        "• PhishTank & OpenPhish feeds\n"
        "• SSL certificate validity\n"
        "• DNS records (MX, SPF, DMARC)\n"
        "• Typosquatting detection\n"
        "• Domain age & redirect chain\n\n"
        "🟢 <b>Risk Levels:</b>\n"
        "• Low (0-29) — Generally safe\n"
        "• Medium (30-59) — Caution advised\n"
        "• High (60-84) — Avoid this site\n"
        "• Critical (85+) — Confirmed threat\n\n"
        "📄 After scanning, tap <b>Get PDF Report</b> for a downloadable report."
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history command — show last 5 scans."""
    try:
        resp = requests.get(f"{BASE_API}/history", timeout=5)
        if resp.status_code == 200:
            scans = resp.json().get("history", [])[-5:]
            if not scans:
                await update.message.reply_text("No scan history yet. Send me a URL to analyze!")
                return
            msg = "📋 <b>Your Last 5 Scans</b>\n\n"
            for s in reversed(scans):
                lvl = s.get("risk_level", "?")
                score = s.get("risk_score", "?")
                url = s.get("url", "")[:50]
                ts = s.get("scanned_at", "")[:10]
                emoji = _level_emoji(lvl)
                msg += f"{emoji} <code>{url}</code>\n   Score: <b>{score}</b> | {lvl} | {ts}\n\n"
            await update.message.reply_text(msg, parse_mode="HTML")
        else:
            await update.message.reply_text("Could not fetch history. Is the backend running?")
    except Exception as e:
        await update.message.reply_text(f"Error fetching history: {e}")


async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Analyze a URL sent as a plain message."""
    user_message = update.message.text.strip()

    if not any(ch in user_message for ch in [".", "/", ":"]):
        await update.message.reply_text(
            "⚠️ This doesn't look like a valid URL.\n\n"
            "Try: <code>google.com</code> or <code>https://example.com</code>",
            parse_mode="HTML",
        )
        return

    progress_msg = await update.message.reply_text(
        "🔍 <b>Analyzing URL...</b>\nRunning ML model + threat intelligence checks ⏳",
        parse_mode="HTML",
    )

    result, error = _analyze_url_api(user_message)

    if error:
        await progress_msg.edit_text(
            f"❌ <b>Analysis Failed</b>\n\n<code>{error}</code>\n\n<i>Check that the URL is correct and accessible.</i>",
            parse_mode="HTML",
        )
        return

    msg = _format_scan_result(result)
    scan_id = result.get("scan_id", "")
    keyboard = _build_inline_keyboard(scan_id, user_message)

    await progress_msg.edit_text(msg, parse_mode="HTML", reply_markup=keyboard)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "scan_another":
        await query.message.reply_text(
            "Send me the next URL to analyze 🔍", parse_mode="Markdown"
        )

    elif data.startswith("pdf:"):
        scan_id = data[4:]
        pdf_url = f"{BASE_API}/report/{scan_id}"
        await query.message.reply_text(
            f"📄 *Download your PDF report:*\n[Click here]({pdf_url})\n\n"
            f"_(Link works while the backend is running)_",
            parse_mode="Markdown",
        )

    elif data.startswith("fp:"):
        scan_id = data[3:]
        try:
            requests.post(
                f"{BASE_API}/feedback",
                json={"scan_id": scan_id, "correct_label": 0},
                timeout=5,
            )
        except Exception:
            pass
        await query.message.reply_text(
            "⚠️ *False positive reported.* Thank you — this helps improve accuracy!",
            parse_mode="Markdown",
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.warning(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "😕 Something went wrong. Please try again."
        )


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("history", history_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot started!")
    print("\n" + "=" * 50)
    print("TELEGRAM BOT IS RUNNING")
    print("=" * 50)
    print("Search for your bot on Telegram and send /start")
    print("Press Ctrl+C to stop\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()