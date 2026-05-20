#!/bin/bash
# Universal notification — sends to all 4 channels at once.
# Usage:
#   ~/notify/notify.sh "Subject" "Body text"
#   echo "body text" | ~/notify/notify.sh "Subject"
#   ~/notify/notify.sh "Subject" < /path/to/file.txt
#
# Skips any channel whose credentials aren't configured in ~/notify/.env

NOTIFY_DIR="$HOME/notify"
PY=/opt/homebrew/bin/python3

if [ ! -f "$NOTIFY_DIR/.env" ]; then
    echo "Error: $NOTIFY_DIR/.env not found"
    exit 1
fi

SUBJECT="${1:-Notification}"

# If $2 is given, use it. Otherwise read from stdin.
if [ -n "$2" ]; then
    BODY="$2"
else
    BODY=$(cat)
fi

# Pipe body to each sender (each one reads from stdin)
cd "$NOTIFY_DIR"
echo "$BODY" | $PY send_email.py    "$SUBJECT" 2>&1 | sed 's/^/[email] /'
echo "$BODY" | $PY send_telegram.py "$SUBJECT" 2>&1 | sed 's/^/[telegram] /'
echo "$BODY" | $PY send_slack.py    "$SUBJECT" 2>&1 | sed 's/^/[slack] /'
echo "$BODY" | $PY send_gchat.py    "$SUBJECT" 2>&1 | sed 's/^/[gchat] /'
