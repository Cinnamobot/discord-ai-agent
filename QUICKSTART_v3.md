# Discord AI Agent Bot v3.0 - Quick Start Guide

**Version**: 3.0.0  
**Last Updated**: 2025-01-15

---

## 🚀 5-Minute Quick Start

### Prerequisites

- Python 3.10+
- Discord Bot Token
- Z.AI API Key (Claude access)
- Claude CLI installed

### Step 1: Clone and Install

```bash
cd discord-AI-agent
uv sync
# Or: pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `.env` file:

```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_z_ai_api_key
ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
```

### Step 3: Test Agent SDK

```bash
uv run python test_agent_sdk_simple.py
```

Expected output:
```
Agent response: Hello! How can I help you today?
```

### Step 4: Start Bot

**重要**: リアルタイム表示を有効にするため、環境変数を設定してください。

```bash
# Windows (PowerShell)
$env:PYTHONUNBUFFERED = "1"
uv run python run.py

# Linux/Mac
PYTHONUNBUFFERED=1 uv run python run.py

# または、Pythonオプションを使用
uv run python -u run.py

# Specify agent (optional)
uv run python -u run.py ./agents/python-tutor
```

Expected logs:
```
INFO - ログイン成功: YourBot#1234 (ID: 123456789)
INFO - エージェント名: Default Agent
INFO - ワークスペース: C:\...\agents\default\workspace
INFO - Bot準備完了
```

**Note**: リアルタイム表示されない場合は `REALTIME_DISPLAY.md` を参照してください。

### Step 5: Test on Discord

**New Conversation:**
```
@ai-agent Hello! Can you help me with Python?
```

**Continue Conversation (reply to bot's message):**
```
@ai-agent Yes, please explain more
```

---

## 📋 What's New in v3.0

### ✅ Completed Features

1. **Agent SDK Integration**
   - 68% code reduction (1,470 → 470 lines)
   - Enterprise-grade security
   - Advanced tool support

2. **Session Continuity** (v3.0.2)
   - Full conversation history
   - Agent remembers context across replies
   - 30-minute session TTL
   - **Fixed**: Reply detection now works correctly

3. **Production-Safe Permissions**
   - `acceptEdits` mode (file ops auto-approved)
   - Bash commands need confirmation (future UI)

4. **Multiple Agent Profiles** (v3.0.2)
   - **Default** - Balanced general-purpose
   - **Minimal** - Minimal constraints
   - **Creative** - Creative thinking
   - **Technical** - Technical expert
   - **Python Tutor** - Python learning
   
   **See:** `docs/AGENT_PROFILES.md`

5. **Optimized System Prompts** (v3.0.2)
   - Short, goal-oriented prompts
   - Maximizes Agent SDK autonomy
   - No micro-management of tools

6. **Enhanced Features**
   - File attachment support (1MB limit)
   - Rate limiting (10/min, 100/hr)
   - Real-time process display
   - Debug logging
   - Error handling

---

## 🎯 Common Use Cases

### 1. Code Review

```
User: @ai-agent Can you review this code?
      [Attach: main.py]

Bot:  I've analyzed your code. Here are my findings:
      1. Line 15: Consider using context manager for file handling
      2. Line 42: This function could be simplified with list comprehension
      ...

User: (Reply) Can you show me the refactored version?

Bot:  Here's the improved code:
      ```python
      # Refactored main.py
      ...
```

### 2. File Analysis

```
User: @ai-agent What files are in the workspace?

Bot:  Let me check the workspace directory...
      Found 5 files:
      - config.yaml
      - main.py
      - utils.py
      - README.md
      - requirements.txt
```

### 3. Multi-Turn Problem Solving

```
User: @ai-agent I have a bug in my Python script

Bot:  I'd be happy to help! Can you share the error message?

User: (Reply) AttributeError: 'NoneType' object has no attribute 'value'

Bot:  This error typically occurs when... [analysis]
      Can you show me the code around line X?

User: (Reply) [Attach: snippet.py]

Bot:  I see the issue! On line 12, you're calling .value on a variable
      that might be None. Here's the fix... [solution]
```

---

## 🔧 Configuration Options

### Permission Modes (src/discord_bot.py:289)

```python
# Current: Production-safe
permission_mode="acceptEdits"

# Alternative: Development (auto-approve all)
# permission_mode="bypassPermissions"

# Alternative: Strict (confirm everything)
# permission_mode="default"
```

**See:** `docs/PERMISSIONS.md` for details

### Rate Limiting (src/discord_bot.py:81)

```python
RateLimiter(
    per_minute=10,   # Adjust as needed
    per_hour=100,    # Adjust as needed
)
```

### Session TTL (src/discord_bot.py:76)

```python
DiscordSessionManager(
    ttl_minutes=30,         # Session expiration
    cleanup_interval=300,   # Cleanup every 5 minutes
)
```

### Allowed Tools (src/discord_bot.py:286)

```python
allowed_tools=[
    "Read",     # Read files
    "Write",    # Write files
    "Edit",     # Edit files
    "Bash",     # Run commands
    "Glob",     # Search files
    "Grep",     # Search content
]
```

---

## 🐛 Troubleshooting

### Bot doesn't start

**Check:**
1. `.env` file exists and has valid tokens
2. Python 3.10+ installed
3. Dependencies installed (`uv sync`)

**Fix:**
```bash
# Reinstall dependencies
uv sync --reinstall

# Check Python version
python --version

# Test .env loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DISCORD_BOT_TOKEN'))"
```

### Bot doesn't respond to mentions

**Check:**
1. Bot has `message_content` intent enabled on Discord Developer Portal
2. Bot has proper role permissions in Discord server
3. Using correct mention format (`@botname message`)

**Fix:**
```python
# Verify intents (src/discord_bot.py:52)
intents = discord.Intents.default()
intents.message_content = True  # Required
intents.messages = True         # Required
intents.members = True          # Required for mentions
```

### Session not continuing

**Check:**
1. Replying to bot's message (not your own message)
2. Including bot mention in reply (`@botname`)
3. Session hasn't expired (30 min TTL)

**Debug:**
```python
# Check logs for:
INFO - セッション作成: session_id=123-456, sdk_session_id=abc123
INFO - セッション継続: sdk_session_id=abc123
INFO - セッション更新: bot_message_id=789, メッセージ数=4
```

### Agent SDK errors

**Check:**
1. Z.AI API key is valid
2. `ANTHROPIC_BASE_URL` set correctly
3. Claude CLI installed and accessible

**Fix:**
```bash
# Test Agent SDK directly
uv run python test_agent_sdk_simple.py

# Check Claude CLI
C:\Users\szk27\.local\bin\claude.exe --version

# Verify environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_BASE_URL'))"
```

### Rate limit errors

**Symptoms:**
```
⚠️ レート制限: 1分あたり10回まで
```

**Fix:**
```python
# Adjust limits in src/discord_bot.py:81
RateLimiter(
    per_minute=20,   # Increase if needed
    per_hour=200,    # Increase if needed
)
```

---

## 📁 File Structure

```
discord-AI-agent/
├── .env                           # Environment variables (create this)
├── config.yaml                    # Bot configuration
├── pyproject.toml                 # Python dependencies
├── requirements.txt               # Pip dependencies
│
├── run.py                  # 🚀 Start here
├── test_agent_sdk_simple.py       # SDK test
├── prototype_agent_loader.py      # Config loader
│
├── src/
│   ├── discord_bot.py                  # Main bot implementation
│   ├── session_adapter.py         # Session management
│   ├── rate_limit.py              # Rate limiting
│   └── file_manager.py            # File handling
│
├── agents/
│   ├── default/
│   │   ├── agent.yaml             # Agent config
│   │   ├── system_prompt.txt      # System prompt
│   │   └── workspace/             # Working directory
│   └── python-tutor/              # Example agent
│
└── docs/
    ├── PERMISSIONS.md             # Permission modes guide
    ├── CHANGELOG_v3.md            # Version 3.0 changes
    └── QUICKSTART_v3.md           # This file
```

---

## 🎓 Learning Path

### Beginner (Day 1)

1. ✅ Complete Quick Start (above)
2. ✅ Test basic mentions and replies
3. ✅ Upload a file and analyze it
4. ✅ Check logs to understand session flow

### Intermediate (Day 2-3)

1. Read `docs/PERMISSIONS.md`
2. Customize `agents/default/system_prompt.txt`
3. Create a new agent profile (e.g., `agents/code-reviewer/`)
4. Experiment with permission modes

### Advanced (Week 1+)

1. Implement Discord Reactions approval UI
2. Add custom permission hook
3. Implement per-user workspace isolation
4. Add audit logging
5. Deploy to production server

---

## 🔐 Security Checklist

### Before Production Deployment

- [ ] Change `permission_mode` to `acceptEdits` (already done ✅)
- [ ] Implement Bash command confirmation UI (future)
- [ ] Review `allowed_tools` list
- [ ] Set up rate limiting appropriate for your server
- [ ] Configure session TTL
- [ ] Enable audit logging
- [ ] Test with untrusted users
- [ ] Set up monitoring/alerting
- [ ] Document incident response procedures

### Development vs Production

| Setting | Development | Production |
|---------|-------------|------------|
| Permission Mode | `bypassPermissions` | `acceptEdits` ✅ |
| Rate Limit | Disabled / High | 10/min, 100/hr ✅ |
| Logging Level | DEBUG ✅ | INFO |
| Workspace Isolation | Per-agent | Per-user (future) |
| File Size Limit | High | 1MB ✅ |

---

## 📚 Next Steps

### Immediate

1. Test the bot on your Discord server
2. Experiment with different agent configurations
3. Review conversation history in logs
4. Test session continuity by replying to bot messages

### Short Term (This Week)

1. Read full documentation:
   - `docs/PERMISSIONS.md` - Understand security
   - `CHANGELOG_v3.md` - See all changes
   - `PLANS.md` - Understand architecture

2. Customize your agent:
   - Edit `agents/default/system_prompt.txt`
   - Add allowed commands in `agent.yaml`
   - Create workspace subdirectories

3. Monitor performance:
   - Check logs for errors
   - Observe session creation/continuation
   - Track rate limit hits

### Long Term (This Month)

1. Implement Discord Reactions approval UI
2. Add per-user workspace isolation
3. Create custom agent profiles
4. Set up production deployment
5. Contribute improvements back to project

---

## 💡 Tips & Tricks

### Tip 1: Check Session Status

Add this to your agent to show session info:
```
@ai-agent /status
```

Bot can respond with current session details (future feature).

### Tip 2: Clear Session

To start fresh conversation without waiting for TTL:
```
@ai-agent /reset
```

(Implement this command in discord_bot.py as future enhancement)

### Tip 3: Debug Mode

Enable detailed logging:
```python
# src/discord_bot.py:35
logging.basicConfig(
    level=logging.DEBUG,  # Already enabled
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

### Tip 4: Multiple Agents

Run multiple bot instances with different agents:
```bash
# Terminal 1
uv run python run.py ./agents/default

# Terminal 2 (different bot token)
uv run python run.py ./agents/python-tutor
```

### Tip 5: Workspace Management

Clean workspace periodically:
```bash
# Add to agents/default/workspace/.gitignore
*
!.gitignore

# Manual cleanup
rm -rf agents/default/workspace/*
```

---

## 🎉 Success!

You now have a production-ready Discord AI Agent Bot v3.0 with:

- ✅ Claude Agent SDK integration
- ✅ Full session continuity
- ✅ Production-safe permissions
- ✅ Conversation history tracking
- ✅ Rate limiting & security
- ✅ File attachment support

**Next**: Try mentioning your bot on Discord and start a conversation!

---

## 📞 Support

### Questions?

1. Check `docs/PERMISSIONS.md` for security questions
2. Check `CHANGELOG_v3.md` for feature details
3. Check logs for runtime issues
4. Open issue on GitHub for bugs

### Contributing

Contributions welcome! Areas for improvement:

- Discord Reactions approval UI
- Per-user workspace isolation
- Slash command support
- Agent switching commands
- pytest test suite
- CI/CD pipeline

---

**Happy Coding!** 🚀
