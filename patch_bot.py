"""
patch_bot.py - Patches telegram_bot.py to fix the message formatting.
"""
import re

filepath = "backend/telegram_bot.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace only the broken loop that dumps raw dicts
OLD_LOOP = (
    '    if all_alerts:\n'
    '        msg += "⚠️ <b>Top Warnings</b>\\n"\n'
    '        for a in all_alerts[:5]:\n'
    '            msg += f"• {a}\\n"\n'
    '        msg += "━━━━━━━━━━━━━━━━\\n"'
)

NEW_LOOP = '''    def _fmt(item):
        if isinstance(item, dict):
            title = item.get("type", "")
            desc  = item.get("description", "")
            return f"<b>{title}</b>: {desc}" if (title and desc) else (desc or title or str(item))
        return str(item)

    if issues:
        msg += f"🚨 <b>Critical Issues ({len(issues)})</b>\\n"
        for a in issues[:4]:
            msg += f"  ❗ {_fmt(a)}\\n"
        msg += "\\n"

    if warnings:
        msg += f"⚠️ <b>Warnings ({len(warnings)})</b>\\n"
        for a in warnings[:3]:
            msg += f"  • {_fmt(a)}\\n"
        msg += "━━━━━━━━━━━━━━━━\\n"'''

# Also fix the all_alerts = issues + warnings line since we handle them separately now
content = content.replace(
    "    warnings = result.get(\"warnings\", [])\n"
    "    issues   = result.get(\"issues\", [])\n"
    "    all_alerts = issues + warnings",
    "    issues   = result.get(\"issues\", [])   or []\n"
    "    warnings = result.get(\"warnings\", []) or []"
)

content = content.replace(OLD_LOOP, NEW_LOOP)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Done. Verifying...")
# Verify the fix is applied
with open(filepath, "r", encoding="utf-8") as f:
    check = f.read()
if "all_alerts" in check:
    print("WARNING: all_alerts still present!")
else:
    print("Fix applied successfully - all_alerts removed.")
if "_fmt(a)" in check:
    print("_fmt helper confirmed in place.")
