# エージェントワークスペース設定ガイド

特定のワークスペースに特定のエージェントを配置する方法を説明します。

## 設定方法の優先順位

ワークスペースは以下の優先順位で決定されます：

1. **agent.yaml の workspace フィールド**（最優先）
2. **環境変数 AGENT_WORKSPACE_ROOT**（全エージェント共通）
3. **デフォルト**（各エージェントディレクトリ内の workspace/）

## 方法1: agent.yaml で個別指定（推奨）

特定のエージェントだけ別のワークスペースを使いたい場合に最適です。

### 絶対パスで指定

`agents/market-analyst/agent.yaml`:
```yaml
name: "Market Analyst"
workspace: /data/market-analyst-workspace

system_prompt: |
  You are a Market Analyst...
```

### 相対パスで指定

エージェントディレクトリからの相対パスも使用可能：

`agents/market-analyst/agent.yaml`:
```yaml
name: "Market Analyst"
workspace: ../shared-workspace/market-analyst

system_prompt: |
  You are a Market Analyst...
```

## 方法2: 環境変数で全体設定

全てのエージェントを同じルートディレクトリ配下に配置したい場合。

`.env`:
```bash
AGENT_WORKSPACE_ROOT=/data/agent-workspaces
```

結果のディレクトリ構造：
```
/data/agent-workspaces/
├── Market Analyst/
│   └── workspace/
├── General Assistant/
│   └── workspace/
└── Code Helper/
    └── workspace/
```

## 方法3: 混在設定（高度な使い方）

一部のエージェントだけ特別なワークスペースを使う場合。

`.env`:
```bash
# デフォルトのワークスペースルート
AGENT_WORKSPACE_ROOT=/data/agent-workspaces
```

`agents/market-analyst/agent.yaml`:
```yaml
name: "Market Analyst"
# このエージェントだけ別の場所
workspace: /mnt/ssd/market-analyst-workspace

system_prompt: |
  You are a Market Analyst...
```

`agents/general-assistant/agent.yaml`:
```yaml
name: "General Assistant"
# workspace フィールドなし → AGENT_WORKSPACE_ROOT を使用
# 結果: /data/agent-workspaces/General Assistant/workspace/

system_prompt: |
  You are a helpful assistant...
```

## systemd での設定例

### パターン1: .env で設定（推奨）

`/opt/discord-ai-bot/.env`:
```bash
DISCORD_BOT_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_api_key_here
AGENT_WORKSPACE_ROOT=/data/agent-workspaces
```

systemdファイルは変更不要。

### パターン2: systemd で環境変数を直接設定

`deployment/discord-ai-bot@.service`:
```ini
[Service]
Environment="PATH=/opt/discord-ai-bot/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="AGENT_WORKSPACE_ROOT=/data/agent-workspaces"
EnvironmentFile=/opt/discord-ai-bot/.env
```

## 実践例

### 例1: マーケットアナリストだけSSDに配置

```yaml
# agents/market-analyst/agent.yaml
name: "Market Analyst"
workspace: /mnt/ssd/market-analyst

allowed_commands:
  - python
  - curl
  - wget
```

理由：
- 大量のニュースデータを扱うため高速SSDを使用
- 他のエージェントは通常のHDDで十分

### 例2: 開発環境と本番環境で切り替え

**開発環境** (`.env.development`):
```bash
AGENT_WORKSPACE_ROOT=./workspaces-dev
```

**本番環境** (`.env.production`):
```bash
AGENT_WORKSPACE_ROOT=/data/agent-workspaces
```

### 例3: エージェント毎に完全に独立

```yaml
# agents/market-analyst/agent.yaml
workspace: /data/market-analyst

# agents/code-helper/agent.yaml
workspace: /data/code-helper

# agents/general-assistant/agent.yaml
workspace: /data/general-assistant
```

## ディレクトリの準備

### 手動で作成する場合

```bash
# ディレクトリ作成
sudo mkdir -p /data/market-analyst-workspace
sudo mkdir -p /data/general-assistant-workspace

# 権限設定
sudo chown -R discord-bot:discord-bot /data/market-analyst-workspace
sudo chown -R discord-bot:discord-bot /data/general-assistant-workspace
sudo chmod -R 755 /data/market-analyst-workspace
sudo chmod -R 755 /data/general-assistant-workspace
```

### 自動作成される場合

コードが自動的にディレクトリを作成しますが、親ディレクトリは事前に作成が必要：

```bash
# 親ディレクトリだけ作成
sudo mkdir -p /data
sudo chown discord-bot:discord-bot /data
sudo chmod 755 /data
```

## トラブルシューティング

### ワークスペースが作成されない

**症状**: Bot起動時にエラー

**確認項目**:
1. 親ディレクトリが存在するか
2. 書き込み権限があるか
3. パスが正しいか（typoなど）

```bash
# 権限確認
ls -ld /data

# 手動でテスト作成
sudo -u discord-bot mkdir -p /data/test-workspace
```

### 設定が反映されない

**確認手順**:
1. systemd再読み込み: `sudo systemctl daemon-reload`
2. サービス再起動: `sudo systemctl restart discord-ai-bot@default`
3. ログ確認: `sudo journalctl -u discord-ai-bot@default -f`

ログに表示されるワークスペースパスを確認：
```
INFO - ワークスペース: /data/market-analyst-workspace
```

## まとめ

| ユースケース | 推奨方法 |
|-------------|---------|
| 全エージェント同じ場所 | 環境変数 `AGENT_WORKSPACE_ROOT` |
| 特定エージェントだけ別の場所 | agent.yaml の `workspace` フィールド |
| エージェント毎に完全独立 | 各 agent.yaml で個別指定 |
| 開発/本番で切り替え | 環境変数 + .env ファイル切り替え |

**推奨**: agent.yaml で個別指定する方法が最も柔軟で明示的です。
