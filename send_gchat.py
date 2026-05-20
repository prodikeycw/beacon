"""
Google Chat helper — sends messages to a Google Chat space via Incoming Webhook.

Setup (requires Google Workspace account):
1. Open Google Chat (mail.google.com or chat.google.com)
2. Open the space (group chat) where you want notifications
3. Click the space name at the top → "Apps & integrations" → "Webhooks"
4. Click "Add webhook" → name it "SGX Digest" → Save
5. Copy the Webhook URL (looks like https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=...)

Then add to .env:
  GCHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=...

Note: Personal Gmail accounts cannot create webhooks — you need a Workspace account.
"""

import os
import sys
import json
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MAX_LEN = 3800  # Google Chat limit is 4096; keep margin


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
    for key in ["GCHAT_WEBHOOK_URL"]:
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def _split(text, limit=MAX_LEN):
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


def send_gchat(text, title=None):
    env = load_env()
    url = env.get("GCHAT_WEBHOOK_URL", "")
    if not url or url.startswith("PASTE_"):
        print("GCHAT DISABLED: GCHAT_WEBHOOK_URL missing in .env")
        return False

    if title:
        text = f"*{title}*\n\n{text}"

    chunks = _split(text)
    all_ok = True
    for i, chunk in enumerate(chunks, 1):
        prefix = f"[{i}/{len(chunks)}] " if len(chunks) > 1 else ""
        # Google Chat supports markdown-like formatting in plain text
        payload = {"text": prefix + chunk}
        try:
            r = requests.post(url, json=payload, timeout=30,
                              headers={"Content-Type": "application/json"})
            if r.status_code != 200:
                print(f"Gchat chunk {i} failed: {r.status_code} {r.text[:200]}")
                all_ok = False
        except Exception as e:
            print(f"Gchat error: {e}")
            all_ok = False
    if all_ok:
        print(f"Google Chat sent ({len(chunks)} chunk{'s' if len(chunks)>1 else ''})")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 send_gchat.py 'Title' < body.txt")
        sys.exit(1)
    title = sys.argv[1]
    body = sys.stdin.read()
    ok = send_gchat(body, title=title)
    sys.exit(0 if ok else 1)
