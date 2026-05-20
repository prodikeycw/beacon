"""
Email helper — sends plain-text emails via Gmail SMTP.

Requires in .env:
  EMAIL_USER=your@gmail.com
  EMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx     (Gmail App Password, NOT your regular password)
  EMAIL_TO=your@gmail.com

Get an App Password here (after enabling 2FA):
  https://myaccount.google.com/apppasswords
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


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
    # Env overrides
    for key in ["EMAIL_USER", "EMAIL_APP_PASSWORD", "EMAIL_TO"]:
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def send_email(subject, body, to=None):
    env = load_env()
    user = env.get("EMAIL_USER", "")
    pw = env.get("EMAIL_APP_PASSWORD", "")
    recipient = to or env.get("EMAIL_TO", user)

    if not user or not pw:
        print("EMAIL DISABLED: EMAIL_USER or EMAIL_APP_PASSWORD missing in .env")
        return False

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as srv:
            srv.starttls()
            srv.login(user, pw)
            srv.send_message(msg)
        print(f"Email sent to {recipient}: {subject}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False


if __name__ == "__main__":
    # CLI usage: cat body.txt | python3 send_email.py "Subject line"
    if len(sys.argv) < 2:
        print("Usage: python3 send_email.py 'Subject line' < body.txt")
        sys.exit(1)
    subject = sys.argv[1]
    body = sys.stdin.read()
    ok = send_email(subject, body)
    sys.exit(0 if ok else 1)
