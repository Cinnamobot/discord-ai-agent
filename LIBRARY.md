# Discord AI Agent - ライブラリとして使用する

`discord-ai-agent` をPythonライブラリとして使用し、複数のbotを簡単に起動できます。

## インストール

### ソースからインストール

```bash
git clone https://github.com/yourusername/discord-ai-agent.git
cd discord-ai-agent
pip install -e .
```

### PyPIからインストール（公開後）

```bash
pip install discord-ai-agent
```

## 使い方

### 1. CLIコマンド（最もシンプル）

#### 単一bot起動

```bash
# デフォルトエージェント
discord-ai-agent

# 特定のエージェント
discord-ai-agent --agent ./agents/market-analyst

# トークンを直接指定
discord-ai-agent --agent ./agents/my-agent --token YOUR_TOKEN
```

#### 複数bot起動

`bots.yaml` を作成：

```yaml
env_file: .env

bots:
  - name: "マーケットアナリスト"
    agent: ./agents/market-analyst
    token_env: DISCORD_BOT_TOKEN_MARKET
    enabled: true
    
  - name: "汎用アシスタント"
    agent: ./agents/general-assistant
    token_env: DISCORD_BOT_TOKEN_GENERAL
    enabled: true
```

起動：

```bash
discord-ai-agent --config bots.yaml
```

### 2. Pythonスクリプトから使用

#### シンプルな例

```python
from discord_ai_agent import DiscordAIBot, load_agent_config
import os
from dotenv import load_dotenv

load_dotenv()

# エージェント設定を読み込み
config = load_agent_config("./agents/market-analyst")

# Bot作成・起動
bot = DiscordAIBot(config)
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
```

#### カスタム設定の例

```python
import discord
from discord_ai_agent import DiscordAIBot, load_agent_config

# エージェント読み込み
config = load_agent_config("./agents/market-analyst")

# カスタムIntents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Botを作成
bot = DiscordAIBot(config, intents=intents)

# イベントハンドラを追加
@bot.event
async def on_ready():
    print(f"ログイン: {bot.user}")

bot.run(token)
```

#### 複数botをプログラムで起動

```python
import asyncio
from discord_ai_agent import DiscordAIBot, load_agent_config

async def run_multiple():
    # 設定読み込み
    config1 = load_agent_config("./agents/market-analyst")
    config2 = load_agent_config("./agents/general-assistant")
    
    # Bot作成
    bot1 = DiscordAIBot(config1)
    bot2 = DiscordAIBot(config2)
    
    # 並行起動
    await asyncio.gather(
        bot1.start(TOKEN1),
        bot2.start(TOKEN2)
    )

asyncio.run(run_multiple())
```

### 3. マルチBot マネージャーを使用

```python
from discord_ai_agent.multi_bot import MultiBotManager

# YAML設定ファイルから起動
manager = MultiBotManager("bots.yaml")
manager.run()  # 全てのbotを起動（ブロッキング）
```

## 設定ファイル例

### bots.yaml（複数bot設定）

```yaml
# 環境変数ファイル
env_file: .env

# Bot一覧
bots:
  # Bot 1: マーケットアナリスト
  - name: "マーケットアナリスト"
    agent: ./agents/market-analyst
    token_env: DISCORD_BOT_TOKEN_MARKET
    enabled: true
  
  # Bot 2: 汎用アシスタント
  - name: "汎用アシスタント"
    agent: ./agents/general-assistant
    token_env: DISCORD_BOT_TOKEN_GENERAL
    enabled: true
  
  # Bot 3: コードヘルパー（無効）
  - name: "コードヘルパー"
    agent: ./agents/code-helper
    token_env: DISCORD_BOT_TOKEN_CODE
    enabled: false  # 無効化されているので起動しない
```

### .env（環境変数）

```bash
# Bot 1のトークン
DISCORD_BOT_TOKEN_MARKET=your_token_here

# Bot 2のトークン
DISCORD_BOT_TOKEN_GENERAL=your_token_here

# Bot 3のトークン
DISCORD_BOT_TOKEN_CODE=your_token_here

# Anthropic APIキー（全botで共有）
ANTHROPIC_API_KEY=your_api_key_here

# ワークスペースのルート（オプション）
AGENT_WORKSPACE_ROOT=/data/agent-workspaces
```

## systemdでの起動

### 単一Bot

`/etc/systemd/system/discord-bot-market.service`:

```ini
[Unit]
Description=Discord AI Agent - Market Analyst
After=network-online.target

[Service]
Type=simple
User=discord-bot
WorkingDirectory=/opt/discord-ai-agent
EnvironmentFile=/opt/discord-ai-agent/.env
ExecStart=/opt/discord-ai-agent/venv/bin/discord-ai-agent \
    --agent ./agents/market-analyst
Restart=always

[Install]
WantedBy=multi-user.target
```

起動：

```bash
sudo systemctl enable discord-bot-market
sudo systemctl start discord-bot-market
```

### 複数Bot（1つのサービスで）

`/etc/systemd/system/discord-bots.service`:

```ini
[Unit]
Description=Discord AI Agents (Multiple)
After=network-online.target

[Service]
Type=simple
User=discord-bot
WorkingDirectory=/opt/discord-ai-agent
EnvironmentFile=/opt/discord-ai-agent/.env
ExecStart=/opt/discord-ai-agent/venv/bin/discord-ai-agent \
    --config bots.yaml
Restart=always

[Install]
WantedBy=multi-user.target
```

### 複数Bot（個別サービス）

Bot毎に個別のサービスファイルを作成：

```bash
# Bot 1
sudo systemctl enable discord-bot-market
sudo systemctl start discord-bot-market

# Bot 2
sudo systemctl enable discord-bot-general
sudo systemctl start discord-bot-general
```

## API リファレンス

### `load_agent_config(agent_path)`

エージェント設定を読み込む。

```python
config = load_agent_config("./agents/my-agent")
```

### `DiscordAIBot(agent_config, intents=None)`

Discord AI エージェントbot。

```python
bot = DiscordAIBot(config)
bot.run(token)
```

### `MultiBotManager(config_file)`

複数bot管理マネージャー。

```python
manager = MultiBotManager("bots.yaml")
manager.run()
```

## 高度な使い方

### ワークスペースのカスタマイズ

```yaml
# agents/market-analyst/agent.yaml
name: "Market Analyst"
workspace: /mnt/ssd/market-analyst-workspace

system_prompt: |
  You are a market analyst...
```

### レート制限の設定

```yaml
# config.yaml
rate_limit:
  requests_per_minute: 10
  requests_per_hour: 100
```

### セッション管理の設定

```yaml
# config.yaml
session:
  ttl_minutes: 30
  cleanup_interval: 300
  max_history_length: 50
```

## トラブルシューティング

### インポートエラー

```bash
# エラー: ModuleNotFoundError: No module named 'discord_ai_agent'

# 解決: パッケージをインストール
pip install -e .
```

### トークンエラー

```bash
# エラー: discord.LoginFailure

# 解決: .envファイルを確認
cat .env | grep DISCORD_BOT_TOKEN
```

### エージェントが見つからない

```bash
# エラー: FileNotFoundError: Agent directory not found

# 解決: パスを確認
ls -la ./agents/my-agent
# agent.yamlが存在することを確認
```

## サンプルコード

`examples/` ディレクトリに完全なサンプルがあります：

- `simple_bot.py` - シンプルな単一bot
- `custom_bot.py` - カスタム設定の例
- `bots.yaml` - 複数bot設定例

## リンク

- ドキュメント: `docs/library-usage.md`
- GitHub: https://github.com/yourusername/discord-ai-agent
