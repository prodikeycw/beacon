"""
Telegram helper — sends messages to a Telegram chat via Bot API.

Setup (3 steps):
1. Talk to @BotFather in Telegram, create a new bot, copy the token.
2. Send any message to your new bot.
3. Visit https://api.telegram.org/bot<TOKEN>/getUpdates to find your chat_id.

Then add to .env:
  TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
  TELEGRAM_CHAT_ID=987654321
"""

import os
import sys
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
TG_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_LEN = 4000  # Telegram limit is 4096; keep margin for safety


def load_env():
    env = {}
    env_file = SCRIPT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    for key in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]:
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def _split(text, limit=MAX_LEN):
    """Split long text into chunks under Telegram's 4096-char limit, breaking on newlines."""
    chunks = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks


def send_telegram(text, title=None):
    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = env.get("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id or token.startswith("PASTE_"):
        print("TELEGRAM DISABLED: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing in .env")
        return False

    if title:
        text = f"*{title}*\n\n{text}"

    url = TG_API.format(token=token)
    chunks = _split(text)
    all_ok = True
    for i, chunk in enumerate(chunks, 1):
        prefix = f"[{i}/{len(chunks)}] " if len(chunks) > 1 else ""
        try:
            r = requests.post(url, data={
                "chat_id": chat_id,
                "text": prefix + chunk,
                # No parse_mode — keep plain text to avoid Markdown escape pain
            }, timeout=30)
            if r.status_code != 200:
                print(f"Telegram chunk {i} failed: {r.status_code} {r.text[:200]}")
                all_ok = False
        except Exception as e:
            print(f"Telegram error: {e}")
            all_ok = False
    if all_ok:
        print(f"Telegram sent ({len(chunks)} chunk{'s' if len(chunks)>1 else ''})")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 send_telegram.py 'Title' < body.txt")
        sys.exit(1)
    title = sys.argv[1]
    body = sys.stdin.read()
    ok = send_telegram(body, title=title)
    sys.exit(0 if ok else 1)
