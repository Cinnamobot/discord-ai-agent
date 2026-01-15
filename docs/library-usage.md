# Discord AI Agent - Library Usage Guide

This guide explains how to use `discord-ai-agent` as a Python library to create and manage Discord AI agent bots.

## Installation

### From PyPI (when published)

```bash
pip install discord-ai-agent
```

### From Source

```bash
git clone https://github.com/yourusername/discord-ai-agent.git
cd discord-ai-agent
pip install -e .
```

## Quick Start

### 1. CLI Usage (Simplest)

```bash
# Single bot
discord-ai-agent --agent ./agents/market-analyst

# Multiple bots
discord-ai-agent --config bots.yaml
```

### 2. Python Script Usage

```python
from discord_ai_agent import DiscordAIBot, load_agent_config

# Load agent configuration
config = load_agent_config("./agents/market-analyst")

# Create and run bot
bot = DiscordAIBot(config)
bot.run("YOUR_DISCORD_BOT_TOKEN")
```

## Usage Patterns

### Pattern 1: Simple Single Bot

```python
import os
from discord_ai_agent import DiscordAIBot, load_agent_config
from dotenv import load_dotenv

load_dotenv()

agent_config = load_agent_config("./agents/my-agent")
bot = DiscordAIBot(agent_config)
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
```

### Pattern 2: Custom Configuration

```python
import discord
from discord_ai_agent import DiscordAIBot, load_agent_config

# Load agent
agent_config = load_agent_config("./agents/market-analyst")

# Custom intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Create bot with custom settings
bot = DiscordAIBot(agent_config, intents=intents)
bot.run(token)
```

### Pattern 3: Multiple Bots Programmatically

```python
import asyncio
from discord_ai_agent import DiscordAIBot, load_agent_config

async def run_multiple_bots():
    # Load configs
    bot1_config = load_agent_config("./agents/market-analyst")
    bot2_config = load_agent_config("./agents/general-assistant")
    
    # Create bots
    bot1 = DiscordAIBot(bot1_config)
    bot2 = DiscordAIBot(bot2_config)
    
    # Run in parallel
    await asyncio.gather(
        bot1.start(TOKEN1),
        bot2.start(TOKEN2)
    )

asyncio.run(run_multiple_bots())
```

### Pattern 4: Multiple Bots with YAML Config

Create `bots.yaml`:

```yaml
env_file: .env

bots:
  - name: "Market Analyst"
    agent: ./agents/market-analyst
    token_env: DISCORD_BOT_TOKEN_MARKET
    enabled: true
    
  - name: "General Assistant"
    agent: ./agents/general-assistant
    token_env: DISCORD_BOT_TOKEN_GENERAL
    enabled: true
```

Run with CLI:

```bash
discord-ai-agent --config bots.yaml
```

Or programmatically:

```python
from discord_ai_agent.multi_bot import MultiBotManager

manager = MultiBotManager("bots.yaml")
manager.run()
```

## API Reference

### `load_agent_config(agent_path)`

Load agent configuration from directory.

**Parameters:**
- `agent_path` (str | Path): Path to agent directory

**Returns:**
- `AgentConfig`: Agent configuration object

**Example:**
```python
config = load_agent_config("./agents/my-agent")
print(config.name)  # Agent name
print(config.workspace)  # Workspace path
print(config.system_prompt)  # System prompt
```

### `DiscordAIBot(agent_config_or_path, intents=None)`

Discord AI agent bot class.

**Parameters:**
- `agent_config_or_path` (AgentConfig | str | Path): Agent config or path to agent
- `intents` (discord.Intents, optional): Discord intents

**Methods:**
- `run(token)`: Start bot with token (blocking)
- `start(token)`: Start bot with token (async)
- `close()`: Close bot connection (async)

**Example:**
```python
config = load_agent_config("./agents/my-agent")
bot = DiscordAIBot(config)

# Blocking run
bot.run(token)

# Or async
await bot.start(token)
```

### `MultiBotManager(config_file)`

Manager for running multiple bots.

**Parameters:**
- `config_file` (str): Path to YAML configuration file

**Methods:**
- `run()`: Start all bots (blocking)
- `start_all()`: Start all bots (async)
- `stop_all()`: Stop all bots (async)

**Example:**
```python
manager = MultiBotManager("bots.yaml")
manager.run()  # Blocks until stopped
```

## Advanced Features

### Custom Event Handlers

```python
bot = DiscordAIBot(agent_config)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name}")

bot.run(token)
```

### Custom Workspace

Set workspace in `agent.yaml`:

```yaml
name: "My Agent"
workspace: /data/my-agent-workspace

system_prompt: |
  You are a helpful assistant...
```

Or via environment:

```bash
export AGENT_WORKSPACE_ROOT=/data/workspaces
```

### Rate Limiting

Rate limiting is built-in and configured in `config.yaml`:

```yaml
rate_limit:
  requests_per_minute: 10
  requests_per_hour: 100
```

### Session Management

Sessions are automatically managed with TTL configuration:

```yaml
session:
  ttl_minutes: 30
  cleanup_interval: 300
  max_history_length: 50
```

## Deployment Examples

### systemd Service (Single Bot)

```ini
[Unit]
Description=Discord AI Agent Bot
After=network-online.target

[Service]
Type=simple
User=discord-bot
WorkingDirectory=/opt/discord-ai-agent
EnvironmentFile=/opt/discord-ai-agent/.env
ExecStart=/opt/discord-ai-agent/venv/bin/discord-ai-agent --agent ./agents/market-analyst
Restart=always

[Install]
WantedBy=multi-user.target
```

### Docker Compose (Multiple Bots)

```yaml
version: '3.8'

services:
  market-analyst:
    image: discord-ai-agent:latest
    command: discord-ai-agent --agent ./agents/market-analyst
    env_file: .env.market
    volumes:
      - ./agents:/app/agents
      - ./data/market:/app/data
    restart: unless-stopped
  
  general-assistant:
    image: discord-ai-agent:latest
    command: discord-ai-agent --agent ./agents/general-assistant
    env_file: .env.general
    volumes:
      - ./agents:/app/agents
      - ./data/general:/app/data
    restart: unless-stopped
```

## Troubleshooting

### Import Error

```python
# Error: ModuleNotFoundError: No module named 'discord_ai_agent'

# Solution: Install package
pip install -e .  # Development mode
# or
pip install discord-ai-agent  # From PyPI
```

### Token Error

```python
# Error: discord.LoginFailure: Improper token has been passed

# Solution: Check .env file
cat .env | grep DISCORD_BOT_TOKEN
# Ensure token is valid and not expired
```

### Agent Not Found

```python
# Error: FileNotFoundError: Agent directory not found

# Solution: Check path
ls -la ./agents/my-agent
# Ensure agent.yaml exists
```

## Examples

Full examples are available in the `examples/` directory:

- `simple_bot.py` - Basic single bot
- `custom_bot.py` - Advanced configuration
- `bots.yaml` - Multi-bot configuration

## Links

- GitHub: https://github.com/yourusername/discord-ai-agent
- Documentation: https://github.com/yourusername/discord-ai-agent/blob/main/README.md
- Issues: https://github.com/yourusername/discord-ai-agent/issues
