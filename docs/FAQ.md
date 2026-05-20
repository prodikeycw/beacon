# 📡 beacon · FAQ

Complete setup, usage, and troubleshooting guide for the `beacon` universal notification CLI.

---

## 目录速查

| 主题 | 涵盖问题 |
|------|---------|
| [⚡ 安装与基本使用](#-安装与基本使用q1q4) | Q1–Q4：installer、alias、测试、卸载 |
| [📧 Gmail 设置](#-gmail-设置q5q7) | Q5–Q7：App Password、测试、常见错误 |
| [📱 Telegram 设置](#-telegram-设置q8q11) | Q8–Q11：建 Bot、找 chat_id、群组通知、错误 |
| [💬 Slack 设置](#-slack-设置q12q14) | Q12–Q14：Webhook、测试、错误 |
| [🗨️ Google Chat 设置](#-google-chat-设置q15q17) | Q15–Q17：Workspace、Webhook、错误 |
| [🛠️ 进阶用法](#-进阶用法q18q22) | Q18–Q22：脚本整合、批次通知、跨机器、Claude 整合 |

---

## ⚡ 安装与基本使用（Q1–Q4）

### Q1：如何安装 beacon？

**TL;DR：一行指令搞定。**

```bash
curl -fsSL https://raw.githubusercontent.com/prodikeycw/beacon/main/install.sh | bash
```

安装程序会自动：
1. Clone 到 `~/beacon/`
2. 安装 Python 依赖（`requests`）
3. 从 template 建立 `~/beacon/.env`
4. 加 `beacon` alias 到你的 `~/.zshrc` 或 `~/.bashrc`

安装后：
1. 编辑 `~/beacon/.env` 填入凭证
2. 重启终端（或执行 `source ~/.zshrc`）
3. 测试：`beacon "Hello" "World"`

### Q2：如何使用 beacon？

**TL;DR：`beacon "标题" "内容"` 或用 pipe。**

```bash
# 行内参数
beacon "Build complete" "All tests passed ✅"

# 透过 stdin（适合长内容）
echo "long content here" | beacon "Report"
cat report.txt | beacon "Daily Report"

# 在工作流程结尾
make build && beacon "✅ Build OK" "Ready to ship"

# 不用 alias（完整路径）
~/beacon/beacon.sh "Subject" "Body"
```

每个通道会回报状态：
```
[email] Email sent to you@example.com: Build complete
[telegram] Telegram sent (1 chunk)
[slack] Slack sent (1 chunk)
[gchat] Google Chat sent (1 chunk)
```

未设置的通道会自动跳过：
```
[slack] SLACK DISABLED: SLACK_WEBHOOK_URL missing in .env
```

### Q3：如何更新到最新版？

**TL;DR：重新跑一次 installer，`.env` 不会被覆盖。**

```bash
curl -fsSL https://raw.githubusercontent.com/prodikeycw/beacon/main/install.sh | bash
```

Installer 会侦测已存在的安装并执行 `git pull`，**你现有的 `.env` 保留**。

### Q4：如何卸载？

**TL;DR：删目录 + 移除 alias。**

```bash
# 删除整个安装
rm -rf ~/beacon

# 从 shell rc 移除 alias（手动编辑）
nano ~/.zshrc   # 找到 'alias beacon=' 那一行删掉
```

---

## 📧 Gmail 设置（Q5–Q7）

### Q5：如何取得 Gmail App Password？

**TL;DR：Gmail 不接受一般密码，必须先开 2FA 再申请 App Password。**

> 📌 **为什么需要：** 一般 Gmail 密码无法用于第三方程序登录。Google 要求使用 App Password（16 位字符）。

**操作步骤：**

1. **开启两步验证**（若已开启可跳过）：
   - 网址：https://myaccount.google.com/security
   - 找到「两步验证」，按指示完成

2. **创建 App Password：**
   - 网址：https://myaccount.google.com/apppasswords
   - 在「应用名称」框中输入 `beacon`（任何名字都可以）
   - 点击 **Create**
   - 复制显示的 16 字符密码（如 `abcd efgh ijkl mnop`）
   - ⚠️ Google 只显示一次，关掉后无法再看

3. **更新 `~/beacon/.env`：**
   ```
   EMAIL_USER=your@gmail.com
   EMAIL_APP_PASSWORD=abcdefghijklmnop   # 去掉空格
   EMAIL_TO=recipient@gmail.com
   ```

### Q6：如何测试 Gmail？

**TL;DR：用 send_email.py 单独测试。**

```bash
echo "test" | python3 ~/beacon/send_email.py "📧 Gmail Test"
```

- 收到邮件 → ✅ 成功
- 错误 `5.7.8 Username and Password not accepted` → 密码错了，重新检查

### Q7：Gmail 常见错误？

**TL;DR：90% 是 App Password 贴错或没开 2FA。**

| 错误 | 原因 | 解决 |
|------|------|------|
| `5.7.8 Username and Password not accepted` | 密码错误或用了一般密码 | 重新生成 App Password |
| `Application-specific password required` | 没开 2FA | 先开 2FA |
| `Less secure app blocked` | Gmail 安全设定 | 必须用 App Password，不能用 OAuth-less 登录 |
| 邮件没收到 | 进了垃圾邮件 | 检查 spam 资料夹 |

> ⚠️ **重要：** App Password 中的空格可以保留也可以去掉，但**不要加引号**：
> - ❌ `EMAIL_APP_PASSWORD="abcd..."` （错）
> - ✅ `EMAIL_APP_PASSWORD=abcdefghijklmnop` （对）

---

## 📱 Telegram 设置（Q8–Q11）

### Q8：如何建立 Telegram Bot？

**TL;DR：跟 @BotFather 对话 `/newbot` 即可。**

1. 在 Telegram 中搜寻 **@BotFather**
2. 发送 `/newbot`
3. 跟随指示，输入 Bot 名称（如「My Notify Bot」）和用户名（必须以 `_bot` 结尾，如 `my_notify_bot`）
4. BotFather 会回复一个 **Token**：
   ```
   8123456789:AAH-AbCdEfGhIjKlMnOpQrStUvWxYzAbCd
   ```
5. **复制这个 Token**，待会要贴到 `.env`

### Q9：如何找到 Chat ID？

**TL;DR：先跟你的 Bot 对话，再用 getUpdates 找出 chat.id。**

> ⚠️ **重要步骤：** 你必须先**主动发讯息**给你的 Bot，否则它无法回讯息给你。

1. 在 Telegram 搜寻刚才建的 Bot
2. 按 **Start** 或发送任意讯息（如 `hi`）
3. 在浏览器开启（把 `<TOKEN>` 换成你的 Bot Token）：
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
4. 找到这一段：
   ```json
   "chat": {
     "id": 123456789,
     ...
   }
   ```
5. **复制 `"id"` 后面的数字**

> ⚠️ **常见错误：** 不要贴成 `update_id`（那是讯息更新计数器，不是聊天室 ID）。

更新 `~/beacon/.env`：
```
TELEGRAM_BOT_TOKEN=8123456789:AAH-AbCdEfGhIjKlMnOpQrStUvWxYzAbCd
TELEGRAM_CHAT_ID=123456789
```

### Q10：如何发到 Telegram 群组？

**TL;DR：把 Bot 加入群组，找出群组的 chat.id（负数）。**

1. 把 Bot 加入 Telegram 群组（在群组设定 → Add members → 搜寻 Bot 用户名）
2. 在群组中发一则讯息提到 Bot：`@your_bot_name 测试`
3. 重新执行 `getUpdates`
4. 找到群组的 `chat.id`（**群组 ID 是负数**，如 `-987654321`）
5. 把 `TELEGRAM_CHAT_ID` 换成这个负数

### Q11：Telegram 常见错误？

**TL;DR：90% 是没先跟 Bot 对话过或贴错 chat_id。**

| 错误 | 原因 | 解决 |
|------|------|------|
| `chat not found` | 还没跟 Bot 对话过 OR chat_id 错误 | 回到 Q9 第 2 步 |
| `unauthorized` | Bot Token 错误 | 从 BotFather 重新复制 |
| `bot was blocked by the user` | 你封锁了自己的 Bot | 解除封锁 |
| `message is too long` | 单则讯息超过 4096 字 | beacon 会自动切分，但若仍失败请缩短内容 |

---

## 💬 Slack 设置（Q12–Q14）

### Q12：如何设置 Slack Webhook？

**TL;DR：在 api.slack.com/apps 建 App，启用 Incoming Webhook，复制 URL。**

1. 登录 Slack，打开 https://api.slack.com/apps
2. **Create New App** → **From scratch**
3. 名称输入 `beacon`，选择你的 Workspace，点 **Create App**
4. 左侧栏点 **Incoming Webhooks** → 切到 **On**
5. 滚到底，点 **Add New Webhook to Workspace**
6. 选择频道（如 `#general` 或私讯给自己），点 **Allow**
7. 复制 Webhook URL（格式类似 `https://hooks.slack.com/services/T.../B.../...`）
8. 更新 `~/beacon/.env`：
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
   ```

### Q13：如何测试 Slack？

**TL;DR：用 send_slack.py 单独测试。**

```bash
echo "test" | python3 ~/beacon/send_slack.py "💬 Slack Test"
```

- Slack 频道收到讯息 → ✅ 成功
- 看到 `Slack sent (1 chunk)` 但讯息没出现 → 频道权限问题

### Q14：Slack 常见错误？

| 错误 | 原因 | 解决 |
|------|------|------|
| `invalid_payload` | URL 贴错或频道已删除 | 重新复制 URL |
| `channel_not_found` | Webhook 被吊销 | 重新加 Webhook（Q12 第 5 步） |
| `no_service` | URL 末段错误 | 完整重新复制 URL |
| HTTP 200 但讯息没出现 | 频道私密且 Bot 没加入 | 改用公开频道或邀请 Bot |

---

## 🗨️ Google Chat 设置（Q15–Q17）

### Q15：如何设置 Google Chat Webhook？

**TL;DR：在 Workspace 的 Chat space 中加 Webhook（个人 Gmail 无法用）。**

> ⚠️ **先决条件：** 必须使用 **Google Workspace 帐户**（公司、学校 Gmail）。**个人 Gmail 不能建立 Webhook**。

1. 打开 https://chat.google.com
2. 进入或创建一个 Space（群组聊天室）：
   - 左下角 **+** → **Create a space**
   - 名称随意（如「Notifications」）
3. 添加 Webhook：
   - 点空间名称顶部 → **Apps & integrations**
   - **Webhooks** → **Add webhook**
   - 名称输入 `beacon`
   - 点 **Save**
4. 复制 Webhook URL（**整段都要**，包括 `?key=...&token=...`）：
   ```
   https://chat.googleapis.com/v1/spaces/AAAA1234/messages?key=ABC...&token=XYZ...
   ```
5. 更新 `~/beacon/.env`：
   ```
   GCHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/.../messages?key=...&token=...
   ```

### Q16：如何测试 Google Chat？

**TL;DR：用 send_gchat.py 单独测试。**

```bash
echo "test" | python3 ~/beacon/send_gchat.py "🗨️ Gchat Test"
```

- Google Chat 空间收到讯息 → ✅ 成功

### Q17：Google Chat 常见错误？

| 错误 | 原因 | 解决 |
|------|------|------|
| `403 Forbidden` | 账户没有 Workspace 权限 | 改用 Workspace 帐户 |
| `404 Not Found` | URL 不完整 | 确认 `?key=` 和 `&token=` 都包含 |
| 讯息没出现 | 看错 Space | 确认 Webhook 建在哪个 Space |

---

## 🛠️ 进阶用法（Q18–Q22）

### Q18：如何在脚本中使用 beacon？

**TL;DR：直接当作 shell 指令呼叫即可。**

```bash
#!/bin/bash
# 长任务完成通知
./long_running_job.sh && beacon "✅ Job done" "Result: $(cat output.txt | head -1)"

# 错误监控
if ! ./deploy.sh; then
    beacon "🚨 Deploy failed" "Check logs at /var/log/deploy.log"
    exit 1
fi

# 定时任务（cron）结尾
0 9 * * * /path/to/daily-task.sh > /tmp/output.txt && cat /tmp/output.txt | beacon "Daily Report"
```

### Q19：如何只用其中一个通道？

**TL;DR：直接呼叫单一通道的 send_*.py。**

```bash
# 只发 Email
echo "content" | python3 ~/beacon/send_email.py "Subject"

# 只发 Telegram
echo "content" | python3 ~/beacon/send_telegram.py "Subject"

# 只发 Slack
echo "content" | python3 ~/beacon/send_slack.py "Subject"

# 只发 Google Chat
echo "content" | python3 ~/beacon/send_gchat.py "Subject"
```

未配置的通道会跳过；只要 `.env` 里有对应字段就会发送。

### Q20：长内容会怎么处理？

**TL;DR：超长讯息会自动切分成多则。**

各通道字数上限：

| 通道 | 单则上限 | 超过时 |
|------|---------|--------|
| Email | 无限制 | — |
| Telegram | 4,096 字符 | 切成 `[1/N]`, `[2/N]` 多则 |
| Slack | 40,000 字符 | 切成多则 |
| Google Chat | 4,096 字符 | 切成多则 |

切分时会在每则前加 `[1/3] ...` 编号，方便阅读。

### Q21：如何在多台机器同步使用？

**TL;DR：每台机器跑一次 installer + 各自填 .env。**

每台机器：
```bash
curl -fsSL https://raw.githubusercontent.com/prodikeycw/beacon/main/install.sh | bash
open -e ~/beacon/.env   # 填入凭证
```

各机器的 `.env` **独立**——可以发到不同的 Telegram chat、不同的 Slack 频道。

凭证更新时手动同步即可（或用云端笔记保存一份 backup）。

### Q22：如何让 Claude / Claude Code 自动用 beacon？

**TL;DR：把使用说明加进 `~/.claude/CLAUDE.md`。**

加到你的全域 `~/.claude/CLAUDE.md`：

```markdown
## Notification Tool

`~/beacon/beacon.sh` is a universal notification CLI that sends to
Gmail, Telegram, Slack, and Google Chat at once.

Usage:
  ~/beacon/beacon.sh "Subject" "Body"
  echo "body" | ~/beacon/beacon.sh "Subject"

Use it for: long task completion, error alerts, background monitor pings.
```

之后任何 Claude session 都会知道：
- *"Run the build then notify me when done"* → Claude 会自动用 beacon
- *"Watch this log and ping me if there's an error"* → 同上
- 不需要每次解释这个工具

---

## 🆘 还是不会用？

1. 检查 `.env` 没有引号、`=` 旁边没有空格
2. 单独测试每个通道的 `send_*.py` 脚本（见 Q6/Q13 等）
3. 确认 Python 3 + `requests` 套件已装好：
   ```bash
   python3 -c "import requests; print('ok')"
   ```
4. 重新跑 installer：
   ```bash
   curl -fsSL https://raw.githubusercontent.com/prodikeycw/beacon/main/install.sh | bash
   ```
5. 在 GitHub 开 issue：https://github.com/prodikeycw/beacon/issues
