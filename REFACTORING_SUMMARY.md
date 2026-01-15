# ファイル名リファクタリング

**実行日**: 2025-01-15  
**理由**: `bot_v3.py`や`run_bot_v3.py`という暫定的な命名を改善

---

## 📝 リネームしたファイル

### コアファイル

| 旧ファイル名 | 新ファイル名 | 理由 |
|-------------|-------------|------|
| `run_bot_v3.py` | `run.py` | シンプルで明確 |
| `src/bot_v3.py` | `src/discord_bot.py` | v3という暫定名を削除 |

### クラス名

| 旧クラス名 | 新クラス名 | 理由 |
|-----------|-----------|------|
| `DiscordAIBotV3` | `DiscordAIBot` | バージョン番号をクラス名から削除 |

---

## ✅ 更新した内容

### 1. ファイル名の変更

```bash
mv src/bot_v3.py src/discord_bot.py
mv run_bot_v3.py run.py
```

### 2. インポート文の更新

**run.py**:
```python
# Before
from src.bot_v3 import main

# After
from src.discord_bot import main
```

### 3. クラス名の変更

**src/discord_bot.py**:
```python
# Before
class DiscordAIBotV3(commands.Bot):
    """Discord AI Agent Bot v3.0 - Agent SDK統合版"""

# After
class DiscordAIBot(commands.Bot):
    """Discord AI Agent Bot - Agent SDK Integration"""
```

### 4. ドキュメントの一括更新

全てのMarkdownファイル内の参照を更新：
- `run_bot_v3.py` → `run.py`
- `bot_v3.py` → `discord_bot.py`

**更新されたファイル**:
- README.md
- CHANGELOG_v3.md
- QUICKSTART_v3.md
- PLANS.md
- REALTIME_DISPLAY.md
- AGENTS_SUMMARY.md
- docs/AGENT_PROFILES.md
- docs/SPECIALIZED_AGENTS.md
- docs/PROCESS_DISPLAY.md
- docs/PERMISSIONS.md
- agents/market-analyst/README.md

---

## 🚀 新しい使い方

### 起動コマンド

**Before**:
```bash
uv run python run_bot_v3.py ./agents/default
```

**After**:
```bash
uv run python run.py ./agents/default
```

### インポート

**Before**:
```python
from src.bot_v3 import DiscordAIBotV3
```

**After**:
```python
from src.discord_bot import DiscordAIBot
```

---

## 📊 影響範囲

### 更新が必要なもの

✅ **完了済み**:
- コアファイル名
- インポート文
- クラス名
- 全ドキュメント
- エラーメッセージ

### 更新不要なもの

- 環境変数設定（.env）
- エージェント設定（agent.yaml）
- 依存関係（requirements.txt, pyproject.toml）
- ワークスペース構造

---

## 🎯 メリット

### 1. **わかりやすさ**
- ❌ `bot_v3.py` - バージョンが入っていて混乱
- ✅ `discord_bot.py` - 明確で自己説明的

### 2. **将来性**
- v4になっても`discord_bot.py`で統一
- バージョン管理はgitタグとCHANGELOGで

### 3. **標準的**
- `run.py` - Python標準的な起動スクリプト名
- `discord_bot.py` - 機能を表す名前

---

## 🔍 確認コマンド

### シンタックスチェック

```bash
python -m py_compile src/discord_bot.py run.py
```

### 起動テスト

```bash
$env:PYTHONUNBUFFERED = "1"
uv run python run.py ./agents/default
```

### ドキュメント確認

```bash
grep -r "bot_v3" --include="*.md" .
# → 結果なしなら成功
```

---

## 📁 最終ファイル構造

```
discord-AI-agent/
├── run.py                         # 🚀 エントリーポイント
│
├── src/
│   ├── __init__.py               # v3.0.3
│   ├── discord_bot.py            # メインボット
│   ├── session_adapter.py
│   ├── rate_limit.py
│   └── file_manager.py
│
├── agents/                        # 8つのエージェント
│   ├── default/
│   ├── minimal/
│   ├── creative/
│   ├── idea-digger/
│   ├── brainstorm-partner/
│   ├── technical/
│   ├── python-tutor/
│   └── market-analyst/
│
├── docs/                          # ドキュメント
│   ├── AGENT_PROFILES.md
│   ├── SPECIALIZED_AGENTS.md
│   ├── PROCESS_DISPLAY.md
│   └── PERMISSIONS.md
│
└── test_*.py                      # テストスクリプト
```

---

## ✅ まとめ

### 変更内容

- ✅ `run_bot_v3.py` → `run.py`
- ✅ `src/bot_v3.py` → `src/discord_bot.py`
- ✅ `DiscordAIBotV3` → `DiscordAIBot`
- ✅ 全ドキュメント更新

### 理由

- より明確で標準的な命名
- バージョン番号をファイル名から削除
- 将来のメンテナンス性向上

### 結果

クリーンで直感的なファイル構造になりました！🎉

---

**これで完全にプロフェッショナルな命名になりました！**
