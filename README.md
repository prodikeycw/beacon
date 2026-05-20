# 📬 notify

> Universal notification CLI — send messages to **Gmail, Telegram, Slack, and Google Chat** with a single command.

Skip configured channels silently. Auto-splits long messages. No dependencies beyond Python 3 + `requests`.

---

## ⚡ One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/prodikeycw/notify/main/install.sh | bash
```

That's it. The installer will:
1. Clone the repo to `~/notify/`
2. Install Python deps (`requests`)
3. Create `~/notify/.env` from template
4. Add `notify` alias to `~/.zshrc` / `~/.bashrc`

Then edit `~/notify/.env` with your credentials and restart your terminal.

---

## 🚀 Usage

```bash
# Inline subject + body
notify "Build done" "All tests passed ✅"

# Pipe long content
cat report.txt | notify "Daily Report"

# After a long-running task
make build && notify "✅ Build done" "Ready to ship"

# Without alias (full path)
~/notify/notify.sh "Subject" "Body"
```

Each channel reports its status:
```
[email] Email sent to you@example.com: Build done
[telegram] Telegram sent (1 chunk)
[slack] Slack sent (1 chunk)
[gchat] Google Chat sent (1 chunk)
```

Unconfigured channels skip silently:
```
[slack] SLACK DISABLED: SLACK_WEBHOOK_URL missing in .env
```

---

## 🔧 Setup

Each channel is **optional**. Configure only what you need.

### 📧 Gmail

1. Enable 2FA at https://myaccount.google.com/security
2. Create App Password at https://myaccount.google.com/apppasswords
3. Edit `~/notify/.env`:
   ```
   EMAIL_USER=your@gmail.com
   EMAIL_APP_PASSWORD=abcdefghijklmnop   # 16 chars, no spaces
   EMAIL_TO=recipient@gmail.com
   ```

### 📱 Telegram

1. In Telegram, message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
2. **Send any message to your new bot** (this is required!)
3. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` and find `"chat":{"id":NUMBER}`
4. Edit `~/notify/.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=123456789
   ```

> ⚠️ Use `chat.id`, **not** `update_id` (a common mistake).

### 💬 Slack

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**
2. Sidebar → **Incoming Webhooks** → toggle **ON** → **Add New Webhook to Workspace**
3. Pick a channel, copy the webhook URL
4. Edit `~/notify/.env`:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
   ```

### 🗨️ Google Chat (requires Workspace account)

1. In a Chat space → space name → **Apps & integrations** → **Webhooks**
2. **Add webhook** → name it → **Save** → copy the URL (full URL including `?key=...&token=...`)
3. Edit `~/notify/.env`:
   ```
   GCHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=...
   ```

---

## 📂 What's installed

```
~/notify/
├── notify.sh          ← Fan-out wrapper (calls all 4 channels)
├── send_email.py      ← Gmail SMTP sender
├── send_telegram.py   ← Telegram Bot API sender
├── send_slack.py      ← Slack Incoming Webhook sender
├── send_gchat.py      ← Google Chat webhook sender
├── install.sh         ← Installer script
├── .env.template      ← Empty template
└── .env               ← Your credentials (gitignored, never committed)
```

---

## 🧠 Use with Claude / Claude Code

After install, add this to your global `~/.claude/CLAUDE.md` so future Claude sessions know about it:

```markdown
## Notification Tool

`~/notify/notify.sh` is a universal notification CLI that sends to Gmail, Telegram, Slack, and Google Chat at once.

Usage:
  ~/notify/notify.sh "Subject" "Body"
  echo "body" | ~/notify/notify.sh "Subject"

Use it for: long task completion, error alerts, background monitor pings.
```

Now you can tell Claude: *"Run the build then notify me when done"* — it'll know what to do.

---

## 🛡️ Security

- `.env` is **gitignored** — never committed to GitHub
- Each user keeps their own credentials locally
- Unconfigured channels are skipped silently (no crashes, no leaks)
- All credentials stay on your machine

---

## 🔄 Update / Re-install

Re-run the one-line installer — it does `git pull` if already installed:

```bash
curl -fsSL https://raw.githubusercontent.com/prodikeycw/notify/main/install.sh | bash
```

Your existing `~/notify/.env` is preserved.

---

## 🧪 Individual channel tests

If something doesn't work, test channels one by one:

```bash
echo "test" | python3 ~/notify/send_email.py    "📧 Test"
echo "test" | python3 ~/notify/send_telegram.py "📱 Test"
echo "test" | python3 ~/notify/send_slack.py    "💬 Test"
echo "test" | python3 ~/notify/send_gchat.py    "🗨️ Test"
```

---

## License

MIT — free to use, modify, share.
