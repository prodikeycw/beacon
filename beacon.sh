#!/bin/bash
# Universal notification — sends to all 4 channels at once.
# Usage:
#   ~/beacon/beacon.sh "Subject" "Body text"
#   echo "body text" | ~/beacon/beacon.sh "Subject"
#   ~/beacon/beacon.sh "Subject" < /path/to/file.txt
#   ~/beacon/beacon.sh "Subject" "Body" --to recipient@email.com
#
# Skips any channel whose credentials aren't configured in ~/beacon/.env

BEACON_DIR="$HOME/beacon"
PY=/opt/homebrew/bin/python3

if [ ! -f "$BEACON_DIR/.env" ]; then
    echo "Error: $BEACON_DIR/.env not found"
    exit 1
fi

SUBJECT="${1:-Notification}"

# Parse --to argument for custom email recipient
TO_EMAIL=""
for i in "$@"; do
    if [ "$PREV" = "--to" ]; then
        TO_EMAIL="$i"
    fi
    PREV="$i"
done

# If $2 is given (and not --to), use it. Otherwise read from stdin.
if [ -n "$2" ] && [ "$2" != "--to" ]; then
    BODY="$2"
else
    BODY=$(cat)
fi

# Pipe body to each sender
cd "$BEACON_DIR"
if [ -n "$TO_EMAIL" ]; then
    echo "$BODY" | $PY send_email.py "$SUBJECT" --to "$TO_EMAIL" 2>&1 | sed 's/^/[email] /'
else
    echo "$BODY" | $PY send_email.py "$SUBJECT" 2>&1 | sed 's/^/[email] /'
fi
echo "$BODY" | $PY send_telegram.py "$SUBJECT" 2>&1 | sed 's/^/[telegram] /'
echo "$BODY" | $PY send_slack.py    "$SUBJECT" 2>&1 | sed 's/^/[slack] /'
echo "$BODY" | $PY send_gchat.py    "$SUBJECT" 2>&1 | sed 's/^/[gchat] /'
