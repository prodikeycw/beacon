"""
Slack helper — sends messages to a Slack channel via Incoming Webhook.

Setup:
1. Go to https://api.slack.com/apps
2. Create New App → From scratch → name it "SGX Digest" → pick your workspace
3. From the left sidebar, click "Incoming Webhooks" → toggle "Activate Incoming Webhooks" ON
4. Click "Add New Webhook to Workspace" → choose the channel → Allow
5. Copy the Webhook URL (looks like https://hooks.slack.com/services/T.../B.../...)

Then add to .env:
  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
"""

import os
import sys
import json
import requests
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MAX_LEN = 35000  # Slack limit is 40000; keep margin


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
    for key in ["SLACK_WEBHOOK_URL"]:
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


def send_slack(text, title=None):
    env = load_env()
    url = env.get("SLACK_WEBHOOK_URL", "")
    if not url or url.startswith("PASTE_"):
        print("SLACK DISABLED: SLACK_WEBHOOK_URL missing in .env")
        return False

    if title:
        text = f"*{title}*\n\n{text}"

    chunks = _split(text)
    all_ok = True
    for i, chunk in enumerate(chunks, 1):
        prefix = f"[{i}/{len(chunks)}] " if len(chunks) > 1 else ""
        # Slack supports code blocks via ``` for monospace formatting
        payload = {"text": prefix + "```" + chunk + "```"}
        try:
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code != 200:
                print(f"Slack chunk {i} failed: {r.status_code} {r.text[:200]}")
                all_ok = False
        except Exception as e:
            print(f"Slack error: {e}")
            all_ok = False
    if all_ok:
        print(f"Slack sent ({len(chunks)} chunk{'s' if len(chunks)>1 else ''})")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 send_slack.py 'Title' < body.txt")
        sys.exit(1)
    title = sys.argv[1]
    body = sys.stdin.read()
    ok = send_slack(body, title=title)
    sys.exit(0 if ok else 1)
